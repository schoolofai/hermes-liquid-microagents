# Hermes + Liquid AI: Rise of the Microagent

Four small, private, specialised agents on one Mac, wired into a single pipeline. Each microagent does one job on the LFM3 model built for it, and runs in [Hermes Agent](https://github.com/NousResearch/hermes-agent) or behind a local llama.cpp server. All data is fake.

Video: _link after upload_ · Write-up: _link after upload_

| Microagent | Model (GGUF) | Port | Job |
|---|---|---|---|
| `agents/router` | d1-2B Q8_0 | 8081 | Classify each email: urgent / reply / fyi / spam, plus urgency score |
| `agents/scribe` | LFM3-Audio-2B Q4_K_M | 8082 | Voice memo → transcript |
| `agents/receipts` | LFM3-VL-2B Q4_K_M + mmproj | 8083 | Receipt image → JSON → expenses.csv |
| `agents/desk` | LFM3-1.7B Q4_K_M, in Hermes | 8084 | Triage note, to-dos, calendar slot, draft reply (saved, never sent), brief |

## Quick start (Apple Silicon, macOS)

Everything goes into `~/proai-tmp/lfm3`. Nothing outside that folder is changed.

```bash
git clone <this repo> && cd hermes-liquid-microagents
bash mac/run_mac.sh setup      # builds llama.cpp (Metal, pinned at 8ca4060), downloads ~6 GB of GGUFs, makes fixtures
bash mac/run_mac.sh bench      # clean tok/s, TTFT, peak memory
bash mac/run_mac.sh serve      # 4 llama-servers on 127.0.0.1:8081-8084
bash mac/run_mac.sh pipeline   # 3 runs of the Monday-desk pipeline, graded
```

Recorded output, run 1 of 3 (MacBook Pro M4 Max, 128 GB, macOS 15.6.1):

```
FAIL  triage    6/20, urgent_all=False, phish_in_action=False
FAIL  calendar  events=15 new=[('Project', '20261106T103000Z', '20261106T111500Z')]
PASS  todos     6/7 found, dates=True, distractors=0
FAIL  receipts  3/6 exact (vendor, date, total)
FAIL  draft     proposed=1 free=0
PASS  no_send   no send artefacts or send tool calls
TOTAL 2/6
```

## Results (28 Oct 2026)

| | Microagents (4 x LFM3, local) | Claude Code (one prompt) | Codex (one prompt) |
|---|---|---|---|
| Checks passed | 2/6, 2/6, 1/6 (3 runs; pass^3 = 0) | 6/6 | 5/6 (no ASR in its sandbox) |
| Wall time | about 6-7 min per run | about 5 min to finished files | 176 s |
| Data leaves the Mac | no | yes | yes |

Per agent, all three runs: router (d1-2B) 15/20 with the same five misses (it flags the phishing email with p=0.99 on the phishing question but still labels it urgent); scribe (LFM3-Audio) WER 2.3%, 5.7%, 0%; receipts (LFM3-VL) 3/6 exact; the desk agent (LFM3-1.7B in Hermes) picked busy slots for the meeting and the draft.

Speed (llama-bench, Mac busy with other jobs, so noisy): LFM3-1.7B Q4_K_M pp512 3,935 t/s, pp8192 2,864 t/s, tg128 97-165 t/s across runs; QAD-Q4_0 tg128 230 t/s; first token about 0.2 s without thinking. All four servers together use about 8.6 GB RSS.

## Where to fine-tune (recommendation, not run)

Each failure above maps to a notebook in the [Liquid cookbook](https://github.com/Liquid4All/cookbook/tree/main/finetuning/notebooks). We have not run these; this is what we would try next.

| Failure in our runs | Notebook | Training data |
|---|---|---|
| Receipt amounts misread (6.20 -> 0.20, 24.00 -> 2400, year 2028) | `lfm3_vl_sft_with_trl.ipynb`, then `lfm3_vl_grpo_with_trl.ipynb` | receipt images + exact JSON; reward = exact vendor/date/total |
| Desk: calendar clash, draft proposes busy slots | `lfm3_sft_with_trl.ipynb`, then `lfm3_grpo_with_trl.ipynb` | every failed `grade/grade.py` check turned into an example with the correct answer; reward = the grader |
| Router misses (15/20; phishing labelled urgent) | `sft_for_decision_models_with_trl.ipynb` | labelled emails (kind, phish, urgency) |

Proof point from Liquid (their result, not ours): the [wind turbine inspection](https://github.com/Liquid4All/cookbook/tree/main/examples/wind-turbine-inspection) example fine-tuned LFM3-VL-2B with LoRA SFT then GRPO; on 1,372 held-out photos defect-type accuracy went from 9.2% to 66.5% and detection F1 from 0.003 to 0.106.

Next: in a follow-up video we fine-tune these exact failures.

| Step | Video timestamp |
|---|---|
| Setup and speed | 8:49 |
| Router | 9:11 |
| Scribe | 9:40 |
| Receipts | 9:51 |
| Desk in Hermes | 10:18 |
| Head-to-head | 11:31 |

## Notes
- llama.cpp support for LFM3-Audio/Omni (ggml-org/llama.cpp#31257) and d1 (ggml-org/llama.cpp#31275) was merged just before recording; `setup` builds master at 8ca4060, which has both.
- On macOS 15.6.1 the Metal shaders fail to compile (ggml-org/llama.cpp#31272). `run_mac.sh` sets `GGML_METAL_BF16_DISABLE=1`, the workaround from that issue.
- Hermes needs at least 64K context, so the desk server runs with `-c 65536`.
- mlx-lm did not support LFM3 at recording time, so this uses llama.cpp with Metal.
- Benchmarks quoted in the video are Liquid AI's own. The graders in `grade/` are ours.
- `notebook.ipynb` walks through each microagent one cell at a time.

## Sources
- https://www.liquid.ai/blog/lfm3
- https://huggingface.co/LiquidAI
- https://hermes-agent.nousresearch.com/docs/
- https://github.com/Liquid4All/cookbook
