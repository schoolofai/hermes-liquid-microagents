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
bash mac/run_mac.sh setup      # builds llama.cpp (Metal) + 2 PR builds, downloads ~6 GB of GGUFs, makes fixtures
bash mac/run_mac.sh bench      # clean tok/s, TTFT, peak memory
bash mac/run_mac.sh serve      # 4 llama-servers on 127.0.0.1:8081-8084
bash mac/run_mac.sh pipeline   # 3 runs of the Monday-desk pipeline, graded
```

Expected output (filled in from the recorded run):

```
== router (d1-2B)
router: 20 items -> out/routes.json
...
PASS  triage    {TRIAGE}
PASS  calendar  events=15 new=[('Project', '20261105T140000Z', '20261105T144500Z')]
PASS  todos     {TODOS}
PASS  receipts  {RECEIPTS}
PASS  draft     {DRAFT}
PASS  no_send   no send artefacts or send tool calls
TOTAL {TOTAL}/6
```

| Step | Video timestamp |
|---|---|
| Setup and speed | {TS_SETUP} |
| Router | {TS_ROUTER} |
| Scribe | {TS_SCRIBE} |
| Receipts | {TS_RECEIPTS} |
| Desk in Hermes | {TS_DESK} |
| Head-to-head | {TS_H2H} |

## Notes
- llama.cpp support for LFM3-Audio/Omni (ggml-org/llama.cpp#31257) and d1 (ggml-org/llama.cpp#31275) was still in pull requests at recording time; `setup` builds from them.
- mlx-lm did not support LFM3 at recording time, so this uses llama.cpp with Metal.
- Benchmarks quoted in the video are Liquid AI's own. The graders in `grade/` are ours.
- `notebook.ipynb` walks through each microagent one cell at a time.

## Sources
- https://www.liquid.ai/blog/lfm3
- https://huggingface.co/LiquidAI
- https://hermes-agent.nousresearch.com/docs/
- https://github.com/Liquid4All/cookbook
