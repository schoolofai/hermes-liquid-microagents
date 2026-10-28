"""Word error rate of scribe transcripts vs the memo scripts."""
import json, re, sys, glob, os
SB = sys.argv[1] if len(sys.argv) > 1 else "sandbox"; K = json.load(open(os.path.join(os.environ.get("ANSWERS", f"{SB}/answers"), "key.json")))
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()
def wer(r, h):
    d = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        p, d[0] = d[0], i
        for j, hw in enumerate(h, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (rw != hw))
    return d[-1] / max(1, len(r))
for k, ref in K["memo_scripts"].items():
    hyp = open(f"{SB}/out/transcripts/{k}.txt").read() if os.path.exists(f"{SB}/out/transcripts/{k}.txt") else ""
    print(f"{k}: WER {wer(norm(ref), norm(hyp)):.3f}")
