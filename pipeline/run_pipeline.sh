#!/usr/bin/env bash
# Monday desk: router -> scribe -> receipts -> desk. Times each stage. Expects servers on 8081-8084.
set -euo pipefail
SB=${1:-sandbox}; HERE=$(cd "$(dirname "$0")/.." && pwd)
t() { local s=$(date +%s.%N); "$@"; echo "  ($(echo "$(date +%s.%N) - $s" | bc) s)"; }
echo "== router (d1-2B)";        t python3 "$HERE/agents/router/service.py" "$SB"
echo "== scribe (LFM3-Audio-2B)"; t python3 "$HERE/agents/scribe/service.py" "$SB"
echo "== receipts (LFM3-VL-2B)";  t python3 "$HERE/agents/receipts/service.py" "$SB"
echo "== desk (LFM3-1.7B in Hermes)"; t python3 "$HERE/agents/desk/run_desk.py" "$SB"
echo "== grade"; ANSWERS=${ANSWERS:-$HOME/proai-tmp/lfm3/answers/monday} python3 "$HERE/grade/grade.py" "$SB"; ANSWERS=${ANSWERS:-$HOME/proai-tmp/lfm3/answers/monday} python3 "$HERE/grade/wer.py" "$SB"
