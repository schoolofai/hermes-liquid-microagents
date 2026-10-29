#!/usr/bin/env bash
# One prompt (pipeline/one_big_agent_prompt.md) to Claude Code and Codex, each in a throwaway copy of the sandbox (no .git), graded with grade_v2.
# Needs both CLIs installed and signed in. Writes into ~/proai-tmp/lfm3/e2e/frontier only.
set -u; W=$HOME/proai-tmp/lfm3; E=$W/e2e; mkdir -p $E; git -C $W/sandbox show HEAD:calendar.ics > $E/pristine_calendar.ics; R=$(cd "$(dirname "$0")/../.." && pwd)
P=$(cat $R/pipeline/one_big_agent_prompt.md)
for a in claude codex; do F=$E/frontier/$a-run; rm -rf $F; mkdir -p $E/frontier; cp -R $W/sandbox $F; (cd $F && git checkout -q . && git clean -qfdx && rm -rf .git); done
s=$(date +%s); (cd $E/frontier/claude-run && claude -p "$P" --permission-mode acceptEdits --no-session-persistence --output-format json > ../claude.json 2>../claude.err); echo "claude $(( $(date +%s)-s )) s"
s=$(date +%s); (cd $E/frontier/codex-run && codex exec --ephemeral --skip-git-repo-check --sandbox workspace-write --json "$P" > ../codex.jsonl 2>../codex.err); echo "codex $(( $(date +%s)-s )) s"
for a in claude codex; do echo "== $a"; PRISTINE_ICS=$E/pristine_calendar.ics ANSWERS=$W/answers/monday python3 $R/grade/grade_v2.py $E/frontier/$a-run; done
echo FRONTIER_DONE
