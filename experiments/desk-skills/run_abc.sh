cd ~/proai-tmp/lfm3/dbg
for i in 1 2 3; do for V in A B C; do
 S=$PWD/v3/runs/${V}_$i; rm -rf $S; mkdir -p v3/runs; cp -R ../sandbox $S
 (cd $S && git checkout -q -- calendar.ics && rm -f out/triage.md out/todo.md out/brief.md out/calendar.ics out/grade.json drafts/reply_05.eml trajectory_samples.jsonl)
 python3 v2/triage_v2.py $S > /dev/null
 s=$(date +%s); HERMES_HOME=$PWD/v3/hh_$V TERMINAL_CWD=$S PYTHONPATH=../hermes-agent timeout 1500 ../.hvenv/bin/python v3/run_desk_v3.py $S $V > $S/desk_out.txt 2>&1; e=$(date +%s)
 echo "== $V run $i desk $((e-s)) s"; ANSWERS=../answers/monday python3 v3/grade_v2.py $S | grep -E "triage|calendar|todos|draft|no_send|brief"
done; done; echo ALL_DONE
