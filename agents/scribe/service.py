"""Scribe microagent: LFM3-Audio-2B on llama-server (PR #31257 build), OpenAI-style input_audio."""
import base64, json, os, sys, glob, urllib.request
URL = os.environ.get("SCRIBE_URL", "http://127.0.0.1:8082/v1/chat/completions")
def transcribe(wav):
    b64 = base64.b64encode(open(wav,"rb").read()).decode()
    body = {"messages":[{"role":"system","content":"Transcribe the audio exactly. Output only the transcript."},
                        {"role":"user","content":[{"type":"input_audio","input_audio":{"data":b64,"format":"wav"}}]}],
            "temperature":0.0}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"].strip()
def main(sandbox):
    os.makedirs(f"{sandbox}/out/transcripts", exist_ok=True)
    for w in sorted(glob.glob(f"{sandbox}/voice/*.wav")):
        name = os.path.splitext(os.path.basename(w))[0]
        open(f"{sandbox}/out/transcripts/{name}.txt","w").write(transcribe(w)+"\n"); print("scribe:", name)
if __name__ == "__main__": main(sys.argv[1] if len(sys.argv)>1 else "sandbox")
