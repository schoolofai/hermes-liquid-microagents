"""Receipts microagent: LFM3-VL-2B + mmproj on llama-server, image in, JSON out -> out/expenses.csv."""
import base64, csv, json, os, re, sys, glob, urllib.request
URL = os.environ.get("RECEIPTS_URL", "http://127.0.0.1:8083/v1/chat/completions")
SYS = open(os.path.join(os.path.dirname(__file__),"SOUL.md")).read()
def read(png):
    b64 = base64.b64encode(open(png,"rb").read()).decode()
    body = {"messages":[{"role":"system","content":SYS},
        {"role":"user","content":[{"type":"image_url","image_url":{"url":f"data:image/png;base64,{b64}"}},
                                  {"type":"text","text":'Return only JSON: {"vendor":..., "date":..., "total":..., "currency":...}'}]}],
        "temperature":0.0}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type":"application/json"})
    txt = json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"]
    m = re.search(r"\{.*\}", txt, re.S); return json.loads(m.group(0)) if m else {"error": txt[:200]}
def main(sandbox):
    rows = []
    for p in sorted(glob.glob(f"{sandbox}/receipts/*.png")):
        r = read(p); r["file"] = os.path.basename(p); rows.append(r); print("receipts:", r)
    with open(f"{sandbox}/out/expenses.csv","w",newline="") as f:
        w = csv.DictWriter(f, ["file","vendor","date","total","currency"], extrasaction="ignore"); w.writeheader(); w.writerows(rows)
if __name__ == "__main__": main(sys.argv[1] if len(sys.argv)>1 else "sandbox")
