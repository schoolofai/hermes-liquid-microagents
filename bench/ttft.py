"""Median TTFT and decode tok/s over 5 streamed runs of a fixed ~2K-token prompt."""
import json, sys, time, statistics, urllib.request
URL = sys.argv[1].rstrip("/") + "/chat/completions"
PROMPT = ("Summarise the following meeting notes in five bullets.\n" + "The team reviewed the quarterly plan and agreed next steps. " * 180)
def run(think):
    body = {"messages": [{"role": "user", "content": PROMPT}], "stream": True, "max_tokens": 200, "temperature": 0.1,
            "chat_template_kwargs": {"enable_thinking": think}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    t0 = time.time(); first = None; n = 0
    for line in urllib.request.urlopen(req):
        if not line.startswith(b"data: ") or line.strip() == b"data: [DONE]": continue
        delta = json.loads(line[6:])["choices"][0]["delta"]
        if delta.get("content") or delta.get("reasoning_content"):
            first = first or time.time(); n += 1
    t1 = time.time(); return first - t0, n / max(1e-6, t1 - first)
out = {}
for think in (True, False):
    r = [run(think) for _ in range(5)]
    out["thinking" if think else "no_thinking"] = {"ttft_s": statistics.median(x[0] for x in r), "decode_tok_s": statistics.median(x[1] for x in r)}
print(json.dumps(out, indent=2))
