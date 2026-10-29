#!/usr/bin/env bash
# End to end: router v2 -> scribe -> receipts (1024 image tokens) -> desk in Hermes; N fresh runs, graded with grade_v2.
# Usage: bash pipeline/e2e/run_e2e.sh [SETUP] [RUNS]     (default D_auto_load 3)
# Expects ~/proai-tmp/lfm3 laid out by mac/run_mac.sh setup (llama.cpp build, models, sandbox, answers, hermes-agent + .hvenv).
set -u
SETUP=${1:-D_auto_load}; N=${2:-3}
W=$HOME/proai-tmp/lfm3; REPO=$(cd "$(dirname "$0")/../.." && pwd); E=$W/e2e; mkdir -p $E/runs; cd $E
export GGML_METAL_BF16_DISABLE=1
S=$W/llama-main/build/bin/llama-server; M=$W/models; D1=$(ls $M/d1-2B*Q8_0*.gguf | head -1)
$S -m $D1 --host 127.0.0.1 --port 8081 -c 16384 -ngl 99 -np 1 > s_router.log 2>&1 & echo $! > pids
$S -m $M/LFM3-Audio-2B-Q4_K_M.gguf --mmproj $M/mmproj-LFM3-Audio-2B-Q8_0.gguf --host 127.0.0.1 --port 8082 -ngl 99 -np 1 > s_scribe.log 2>&1 & echo $! >> pids
$S -m $M/LFM3-VL-2B-Q4_K_M.gguf --mmproj $M/mmproj-LFM3-VL-2B-Q8_0.gguf --host 127.0.0.1 --port 8083 -ngl 99 -np 1 --jinja -c 16384 --temp 0 --image-min-tokens 1024 --image-max-tokens 1024 > s_receipts.log 2>&1 & echo $! >> pids
$S -m $M/LFM3-1.7B-Q4_K_M.gguf --host 127.0.0.1 --port 8084 -c 65536 -ngl 99 -np 1 --jinja --temp 0 > s_desk.log 2>&1 & echo $! >> pids
trap 'kill $(cat $E/pids) $(cat $E/sampler.pid 2>/dev/null) 2>/dev/null' EXIT
for p in 8081 8082 8083 8084; do until curl -sf http://127.0.0.1:$p/health >/dev/null; do sleep 2; done; done
echo SERVERS_UP; ( while true; do ps -o rss= -p $(paste -sd, pids) | awk -v t=$(date +%s) '{s+=$1} END{print t, s}' >> rss.log; sleep 2; done ) & echo $! > sampler.pid
for i in $(seq 1 $N); do
  SB=$E/runs/run$i; rm -rf $SB; cp -R $W/sandbox $SB; (cd $SB && git checkout -q . && git clean -qfdx)
  t0=$(date +%s)
  ROUTER_URL=http://127.0.0.1:8081/v1/systemone python3 $REPO/agents/router/triage_v2.py $SB > $SB/router_out.txt 2>&1; t1=$(date +%s)
  python3 $REPO/agents/scribe/service_v2.py $SB > $SB/scribe_out.txt 2>&1; t2=$(date +%s)
  python3 $REPO/agents/receipts/service_v2.py $SB > $SB/receipts_out.txt 2>&1; t3=$(date +%s)
  HERMES_HOME=$REPO/experiments/desk-skills/setups/$SETUP TERMINAL_CWD=$SB PYTHONPATH=$W/hermes-agent timeout 1500 $W/.hvenv/bin/python $REPO/pipeline/e2e/run_desk_e2e.py $SB $SETUP > $SB/desk_out.txt 2>&1; t4=$(date +%s)
  echo "== run $i router $((t1-t0)) scribe $((t2-t1)) receipts $((t3-t2)) desk $((t4-t3)) total $((t4-t0)) s"
  ANSWERS=$W/answers/monday python3 $REPO/grade/grade_v2.py $SB | tee $SB/grade.txt
done
sort -k2 -n rss.log | tail -1 | awk '{printf "peak RSS, 4 servers: %.1f GB\n", $2/1048576}'
