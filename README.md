# Hermes + Liquid AI: Rise of the Microagent

**Video:** [Watch on YouTube](https://youtu.be/f37QpvMJV7g) · Write-up: [proaiclips.substack.com](https://proaiclips.substack.com)

**Chapters:** [0:00](https://youtu.be/f37QpvMJV7g?t=0) The Monday desk · [1:34](https://youtu.be/f37QpvMJV7g?t=94) Monolith vs microservice · [2:35](https://youtu.be/f37QpvMJV7g?t=155) Why now: LFM3 · [3:38](https://youtu.be/f37QpvMJV7g?t=218) Hermes: tools, skills, harness · [4:42](https://youtu.be/f37QpvMJV7g?t=282) Inside the desk · [6:35](https://youtu.be/f37QpvMJV7g?t=395) The experiment · [7:50](https://youtu.be/f37QpvMJV7g?t=470) Results · [8:41](https://youtu.be/f37QpvMJV7g?t=521) Why skills win · [10:30](https://youtu.be/f37QpvMJV7g?t=630) Full pipeline · [10:58](https://youtu.be/f37QpvMJV7g?t=658) Head to head · [11:47](https://youtu.be/f37QpvMJV7g?t=707) Next: fine-tuning · [12:26](https://youtu.be/f37QpvMJV7g?t=746) Verdict


Four small, private, specialised agents on one Mac, wired into one pipeline. Each microagent does one job on the LFM3 model built for it, in [Hermes Agent](https://github.com/NousResearch/hermes-agent) or behind a local llama.cpp server. The finding: with a 1.7B model, the harness (SOUL.md, tools, skills, scripts) matters more than the model. All data is fake.

| Microagent | Model (GGUF) | Port | Job | Code |
|---|---|---|---|---|
| router | d1-2B Q8_0 | 8081 | Typed questions per email (folder, phishing, scam) + one rule: phish/scam > 0.5 goes to spam | `agents/router/triage_v2.py` |
| scribe | LFM3-Audio-2B Q4_K_M | 8082 | Voice memo to transcript | `agents/scribe/service_v2.py` |
| receipts | LFM3-VL-2B Q4_K_M + mmproj | 8083 | Receipt image to vendor/date/total, `--image-min-tokens 1024 --image-max-tokens 1024`, temp 0 | `agents/receipts/service_v2.py` |
| desk | LFM3-1.7B Q4_K_M in Hermes | 8084 | To-dos, meeting with Bob, draft reply (saved, never sent), brief | `experiments/desk-skills/setups/D_auto_load` |

## Quick start (Apple Silicon, macOS)

Everything goes into `~/proai-tmp/lfm3`. Nothing outside that folder is changed. Each step lists what it runs, the command, the output to expect, and where it is in the video.

**1. Setup** · builds llama.cpp with Metal, downloads about 6 GB of GGUFs, clones Hermes Agent at `0431192d` and applies `patches/hermes-search_files-race.patch`, makes the fake sandbox. Video: [3:38](https://youtu.be/f37QpvMJV7g?t=218)
```bash
git clone https://github.com/schoolofai/hermes-liquid-microagents && cd hermes-liquid-microagents
bash mac/run_mac.sh setup
```
Expected: `SETUP_DONE` in `~/proai-tmp/lfm3/run.log`.

**2. Benchmark** · `llama-bench` and a TTFT probe for LFM3-1.7B. Video: [4:42](https://youtu.be/f37QpvMJV7g?t=282)
```bash
bash mac/run_mac.sh bench
```
Expected (M4 Max, quiet machine): tg128 about 100 tok/s or more, first token about 0.2 s. Inside the full pipeline, with long contexts and other jobs running, the desk generated at about 60 tok/s.

**3. Pipeline, 3 fresh runs** · `pipeline/e2e/run_e2e.sh` starts the four servers on 127.0.0.1, then for each run: router v2, scribe, receipts, desk in Hermes (skills preloaded with `skills.auto_load`), graded by `grade/grade_v2.py`. Video: [10:30](https://youtu.be/f37QpvMJV7g?t=630)
```bash
bash mac/run_mac.sh pipeline            # or: bash pipeline/e2e/run_e2e.sh D_auto_load 3
```
Expected, every run:
```
== run 1 router 4 scribe 2 receipts 16 desk 146 total 168 s
PASS  triage  19/20, urgent_all=True, phish_in_action=False
PASS  calendar  events=15 new=[('Project sync', '20261105T140000Z', '20261105T144500Z')] problems=[]
PASS  todos  6/7 found, dates=True, distractors=0
PASS  receipts  6/6 exact (vendor, date, total)
PASS  draft  to_jordan=True proposed=4 free=2
PASS  no_send  no send artefacts or send tool calls
TOTAL 6/6
peak RSS, 4 servers: 10.5 GB
```

**4. Harness experiment (desk only)** · the same LFM3-1.7B in four harness setups, 3 runs each. Video: [6:35](https://youtu.be/f37QpvMJV7g?t=395)
```bash
SETUP=C_custom_tools bash pipeline/e2e/run_e2e.sh C_custom_tools 3   # any folder in experiments/desk-skills/setups
```
Expected: the numbers in the results tables below.

**5. Head-to-head** · one prompt to Claude Code and to Codex, each in a throwaway copy of the sandbox. Needs both CLIs signed in; never edits `~/.claude` or `~/.codex`. Video: [10:58](https://youtu.be/f37QpvMJV7g?t=658)
```bash
bash mac/run_mac.sh frontier
```
Expected: Claude Code `TOTAL 6/6`; Codex `TOTAL 5/6` when its sandbox has no speech recogniser.

## Results (29 Oct 2026, MacBook Pro M4 Max 128 GB, temp 0, grade_v2)

### Full pipeline vs one big agent
| | Microagents (4 x LFM3, local) | Claude Code (one prompt) | Codex (one prompt) |
|---|---|---|---|
| Checks passed | 6/6, 6/6, 6/6 (pass^3 = 3/3) | 6/6 | 5/6 (to-dos: no speech recogniser in its sandbox) |
| Wall time | 168-197 s per run | 100 s | 151 s |
| Data leaves the Mac | no | yes | yes |

Per agent, all three runs: router 19/20; scribe WER 2.3%, 5.7%, 0%; receipts 6/6 exact; desk to-dos 6/7, 6/7, 7/7.
Memory: the four servers use 8.6 GB RSS at idle and peak at 10.5 GB while working (desk at `-c 65536`).

### Harness experiment: one model, four setups (desk only, 3 runs each)
| Setup | Folder | calendar | to-dos | reply | calls/run | tokens/run |
|---|---|---|---|---|---|---|
| 1. Prompt only (file tools) | `A_prompt_only` | 2/3 | 0/3 | 2/3 | 6-7 | 88-114k |
| 2. Custom tools (plugin) | `C_custom_tools` | 3/3 | 0/3 | 3/3 | 4-8 | 36-82k |
| 3. Tools + skill | `D_tools_skill` | 2/3 | 1/3 | 2/3 | 6 | 60-92k |
| 4. Skills + scripts | `B_skills_scripts` | 3/3 | 3/3 | 3/3 | 11-29 | 120-528k |

### Why setup 3 failed: getting the model to open the skill
Hermes lists each skill as one line clipped to 60 characters; tools describe themselves in full, so the model used the tools and never opened the skill. Variants of setup 3, 3 runs each:

| Variant | Folder | calendar | to-dos | reply | skill opened | tokens/run |
|---|---|---|---|---|---|---|
| Tools + skill | `D_tools_skill` | 2/3 | 1/3 | 2/3 | never | 60-92k |
| + stronger skill description | `D_stronger_description` | 3/3 | 2/3 | 1/3 | never | 63-111k |
| + SOUL.md names the skill per job | `D_soul_names_skill` | 3/3 | 3/3 | 3/3 | first call, every run | 70-184k |
| + both | `D_soul_and_description` | 3/3 | 3/3 | 3/3 | yes, 7 calls | 74-88k |
| + `pre_tool_call` gate (blocks tools until the skill is viewed) | `D_pre_tool_call_gate` | 3/3 | 2/3 | 3/3 | forced | 76-122k |
| + `skills.auto_load: [desk-day]` | `D_auto_load` | 3/3 | 3/3 | 3/3 | preloaded | 56-74k (125-177 s) |

`D_auto_load` is the cheapest setup that passes everything, so the pipeline uses it.

## Repo map
- `agents/router/triage_v2.py` router v2 (typed questions + phishing/scam rule). `agents/*/service.py` are the v1 services from the first cut.
- `agents/scribe/service_v2.py`, `agents/receipts/service_v2.py` the services used in the pipeline.
- `experiments/desk-skills/setups/` every harness setup (SOUL.md, config.yaml, plugins, skills). Use one as `HERMES_HOME`.
- `experiments/desk-skills/run_*.sh`, `run_desk_v3.py` the exact runners used for the experiment (they expect the `~/proai-tmp/lfm3/dbg` layout and a desk server on 8094).
- `pipeline/e2e/` full pipeline and head-to-head runners. `pipeline/run_pipeline.sh` is the v1 pipeline.
- `grade/grade_v2.py` grader (6 checks; accepts ISO dates; `PRISTINE_ICS` for folders without git). `grade/wer.py` scribe WER.
- `patches/hermes-search_files-race.patch` fix for a `ProcessLookupError` in Hermes `search_files` when ripgrep exits between `poll()` and `getpgid()`. It is a local patch, not upstream.

## Where to fine-tune next
The harness got every check passing; fine-tuning is the next optimisation. Router: train d1-2B on labelled emails with Liquid's `sft_for_decision_models_with_trl.ipynb` so the hand-written phishing rule can go. Desk: SFT LFM3-1.7B on successful skill runs, then GRPO with `grade_v2.py` as the reward, to follow the procedure in fewer calls and tokens. Notebooks: [Liquid cookbook](https://github.com/Liquid4All/cookbook/tree/main/finetuning/notebooks). This is the follow-up video.

## Notes
- llama.cpp support for LFM3-Audio/Omni (ggml-org/llama.cpp#31257) and d1 (ggml-org/llama.cpp#31275) was merged just before recording; `setup` builds master at 8ca4060, which has both.
- On macOS 15.6.1 the Metal shaders fail to compile (ggml-org/llama.cpp#31272). `run_mac.sh` sets `GGML_METAL_BF16_DISABLE=1`, the workaround from that issue.
- Image tokens: by default llama.cpp gives each image a small token budget and small receipt digits get lost; 1024 min/max fixed it.
- Hermes needs at least 64K context, so the desk server runs with `-c 65536`.
- mlx-lm did not support LFM3 at recording time, so this uses llama.cpp with Metal.
- Benchmarks quoted in the video are Liquid AI's own. The graders in `grade/` are ours.
- `notebook.ipynb` walks through each microagent one cell at a time.

## Sources
- https://www.liquid.ai/blog/lfm3
- https://huggingface.co/LiquidAI
- https://hermes-agent.nousresearch.com/docs/
- https://github.com/Liquid4All/cookbook
