#!/usr/bin/env bash
# Mac run for the Monday-desk demo. Everything lives in ~/proai-tmp/lfm3. Nothing else is touched or deleted.
# Usage: bash mac/run_mac.sh [setup|bench|serve|pipeline|frontier|all|stop]
set -euo pipefail
W="$HOME/proai-tmp/lfm3"; REPO=$(cd "$(dirname "$0")/.." && pwd)
export HF_HUB_CACHE="$W/hf" HERMES_HOME="$W/hermes-home"
export GGML_METAL_BF16_DISABLE=1   # workaround from ggml-org/llama.cpp#31272 (bf16 constexpr cast fails to compile on macOS 15 Metal)
LOG="$W/run.log"; mkdir -p "$W" "$HF_HUB_CACHE" "$HERMES_HOME" "$W/out"
say_log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

guard() {  # one Mac job at a time: refuse while another ProAI job is running
  if pgrep -f "mlx_lm|speak.py|nb_run.py|nb_speed.py" >/dev/null; then say_log "another Mac job is running; refusing"; exit 3; fi
  local free; free=$(df -g "$HOME" | awk 'NR==2{print $4}'); say_log "free disk ${free} GB"
  [ "$free" -ge 15 ] || { say_log "need >= 15 GB free; stopping (no deletions)"; exit 4; }
}

build() {  # $1 dir name, $2 optional PR number
  local d="$W/$1"; [ -x "$d/build/bin/llama-server" ] && return
  git clone -q https://github.com/ggml-org/llama.cpp "$d"
  if [ -n "${2:-}" ]; then (cd "$d" && git fetch -q origin "pull/$2/head:pr$2" && git checkout -q "pr$2"); fi
  cmake -S "$d" -B "$d/build" -DGGML_METAL=ON -DCMAKE_BUILD_TYPE=Release >/dev/null
  cmake --build "$d/build" -j --target llama-server llama-bench >/dev/null
  say_log "built $1 at $(cd "$d" && git rev-parse --short HEAD)"
}

setup() {
  guard
  python3 -m venv "$W/.venv"; source "$W/.venv/bin/activate"; pip -q install -U "huggingface_hub[cli]" pillow cmake
  build llama-main   # PRs #31257 (Audio/Omni) and #31275 (d1) were merged into master by run time, so one build serves all four
  hf download LiquidAI/LFM3-1.7B-GGUF LFM3-1.7B-Q4_K_M.gguf LFM3-1.7B-QAD-Q4_0.gguf --local-dir "$W/models"
  hf download LiquidAI/LFM3-VL-2B-GGUF LFM3-VL-2B-Q4_K_M.gguf mmproj-LFM3-VL-2B-Q8_0.gguf --local-dir "$W/models"
  hf download LiquidAI/LFM3-Audio-2B-GGUF LFM3-Audio-2B-Q4_K_M.gguf mmproj-LFM3-Audio-2B-Q8_0.gguf --local-dir "$W/models"
  hf download LiquidAI/d1-2B-GGUF --include "*Q8_0*" --local-dir "$W/models"
  [ -d "$W/hermes-agent" ] || git clone -q https://github.com/NousResearch/hermes-agent "$W/hermes-agent"
  (cd "$W/hermes-agent" && git checkout -q 0431192d && (git apply --check "$REPO/patches/hermes-search_files-race.patch" 2>/dev/null && git apply "$REPO/patches/hermes-search_files-race.patch" || true))
  [ -x "$W/.hvenv/bin/python" ] || { python3 -m venv "$W/.hvenv"; "$W/.hvenv/bin/pip" -q install -e "$W/hermes-agent"; }
  rm -rf "$W/sandbox"; python3 "$REPO/fixtures/make_fixtures.py" "$W/sandbox"
  for m in "$W"/sandbox/answers/memo_scripts/*.txt; do n=$(basename "${m%.txt}"); say -v Samantha -o "$W/sandbox/voice/$n.aiff" -f "$m"; afconvert -f WAVE -d LEI16@16000 "$W/sandbox/voice/$n.aiff" "$W/sandbox/voice/$n.wav"; rm "$W/sandbox/voice/$n.aiff"; done
  rm -rf "$W/answers/monday"; mkdir -p "$W/answers"; mv "$W/sandbox/answers" "$W/answers/monday"   # keys live OUTSIDE the sandbox so agents cannot read them
  (cd "$W/sandbox" && git init -q && git add -A && git commit -qm fixtures)   # reset between runs with git checkout/clean
  say_log "SETUP_DONE"
}

D1=$(ls "$W"/models/d1-2B*Q8_0*.gguf 2>/dev/null | head -1 || true)
serve() {
  S="$W/llama-main/build/bin/llama-server"; A="$S"; DS="$S"
  nohup "$DS" -m "$D1" --host 127.0.0.1 --port 8081 -b 8192 -ub 8192 -ngl 99 -np 1 >"$W/out/s_router.log" 2>&1 &
  nohup "$A" -m "$W/models/LFM3-Audio-2B-Q4_K_M.gguf" --mmproj "$W/models/mmproj-LFM3-Audio-2B-Q8_0.gguf" --host 127.0.0.1 --port 8082 -ngl 99 -np 1 >"$W/out/s_scribe.log" 2>&1 &
  nohup "$S" -m "$W/models/LFM3-VL-2B-Q4_K_M.gguf" --mmproj "$W/models/mmproj-LFM3-VL-2B-Q8_0.gguf" --host 127.0.0.1 --port 8083 -ngl 99 -np 1 --jinja -c 16384 --temp 0.1 --top-p 1.0 --top-k 50 --min-p 0.0 --repeat-penalty 1.1 --no-reasoning-preserve >"$W/out/s_receipts.log" 2>&1 &
  nohup "$S" -m "$W/models/LFM3-1.7B-Q4_K_M.gguf" --host 127.0.0.1 --port 8084 -c 65536 -ngl 99 -np 1 --jinja --temp 0.1 --top-p 1.0 --top-k 50 --min-p 0.0 --repeat-penalty 1.1 --no-reasoning-preserve >"$W/out/s_desk.log" 2>&1 &
  for p in 8081 8082 8083 8084; do until curl -sf "http://127.0.0.1:$p/health" >/dev/null; do sleep 2; done; done
  say_log "SERVERS_UP"; ps -o pid,rss,command -p $(pgrep -d, -f llama-server) | tee "$W/out/rss_all.txt"
}

bench() {  # clean numbers: run with nothing else going
  guard; B="$W/llama-main/build/bin/llama-bench"
  for m in LFM3-1.7B-Q4_K_M LFM3-1.7B-QAD-Q4_0 LFM3-VL-2B-Q4_K_M; do
    "$B" -m "$W/models/$m.gguf" -p 512,8192 -n 128 -r 5 -ngl 99 -o json >"$W/out/bench_$m.json"; say_log "bench $m done"; done
  "$W/llama-main/build/bin/llama-server" -m "$W/models/LFM3-1.7B-Q4_K_M.gguf" --port 8099 -c 32768 -ngl 99 -np 1 >"$W/out/s_bench.log" 2>&1 & PID=$!
  until curl -sf http://127.0.0.1:8099/health >/dev/null; do sleep 1; done
  python3 "$REPO/bench/ttft.py" http://127.0.0.1:8099/v1 >"$W/out/ttft.json"
  ps -o rss= -p $PID | awk '{printf "server RSS after TTFT runs: %.2f GB\n", $1/1048576}' >"$W/out/peak_32k.txt"; kill $PID; wait $PID 2>/dev/null || true
  say_log "BENCH_DONE (server RSS in out/peak_32k.txt, TTFT in out/ttft.json)"
}

pipeline() {  # router v2 -> scribe -> receipts -> desk (Hermes, skills.auto_load); 3 fresh runs, grade_v2. Starts and stops its own servers.
  bash "$REPO/pipeline/e2e/run_e2e.sh" "${SETUP:-D_auto_load}" 3 | tee "$W/out/e2e.txt"; say_log "PIPELINE_DONE"
}

frontier() {  # same tasks as ONE big agent; throwaway folders; no session persistence; never edits ~/.claude or ~/.codex
  bash "$REPO/pipeline/e2e/run_frontier.sh" | tee "$W/out/frontier.txt"; say_log "FRONTIER_DONE"
}

stop() { pkill -f "$W/llama-" || true; say_log "servers stopped"; }
case "${1:-all}" in
  setup) setup;; bench) bench;; serve) serve;; pipeline) pipeline;; frontier) frontier;; stop) stop;;
  all) setup; bench; pipeline; frontier; (cd "$W" && tar czf results.tgz out run.log); say_log "ALL_DONE";;
esac
