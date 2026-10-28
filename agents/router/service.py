"""Router microagent: d1-2B via llama-server /v1/systemone (one forward pass per item)."""
import json, os, sys, glob, email, urllib.request
URL = os.environ.get("ROUTER_URL", "http://127.0.0.1:8081/v1/systemone")
Q = {
 "kind":    {"type":"choice","instructions":"What kind of email is this?",
             "criteria":{"urgent":"Needs action today","reply":"Needs a reply, not today","fyi":"Information or newsletter","spam":"Spam, scam or phishing"}},
 "phish":   {"type":"noul","instructions":"Does this ask for a password, bank details or a payment via a link?"},
 "urgency": {"type":"score","instructions":"How urgent is this?","criteria":["Can wait","This week","Today"]},
}
def ask(state):
    req = urllib.request.Request(URL, json.dumps({"state":state,"questions":Q}).encode(), {"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))
def main(sandbox):
    routes = {}
    for p in sorted(glob.glob(f"{sandbox}/inbox/*.eml")):
        m = email.message_from_string(open(p).read())
        state = f"From: {m['From']}\nSubject: {m['Subject']}\n\n{m.get_payload()}"
        routes[os.path.basename(p)] = ask(state)
    json.dump(routes, open(f"{sandbox}/out/routes.json","w"), indent=2)
    print(f"router: {len(routes)} items -> out/routes.json")
if __name__ == "__main__": main(sys.argv[1] if len(sys.argv)>1 else "sandbox")
