"""Router v2: d1-2B with clearer criteria + scam/phish override; writes out/routes.json AND out/triage.md deterministically."""
import json,glob,email,os,sys,urllib.request
sb=sys.argv[1]; URL=os.environ.get("ROUTER_URL","http://127.0.0.1:8081/v1/systemone")
Q={"kind":{"type":"choice","instructions":"Alex reads this email. Which folder should it go in?",
  "criteria":{"urgent":"A real colleague, client or service needs Alex to act today: a deadline, appointment or problem happening today",
   "reply":"A real person asks Alex a question or a favour; it can be answered later this week",
   "fyi":"A newsletter, notification, receipt, timetable or announcement; nothing to answer",
   "spam":"Scam, phishing, fake prize, crypto offer or unsolicited marketing"}},
 "phish":{"type":"noul","instructions":"Does this ask for a password, bank details or a payment via a link?"},
 "scam":{"type":"noul","instructions":"Is this email a scam, phishing or junk from an unknown sender?"}}
routes={};sec={"urgent":[],"reply":[],"fyi":[],"spam":[]}
for p in sorted(glob.glob(sb+"/inbox/*.eml")):
    m=email.message_from_string(open(p).read()); f=os.path.basename(p)
    r=urllib.request.Request(URL,json.dumps({"state":f"From: {m['From']}\nSubject: {m['Subject']}\n\n{m.get_payload()}","questions":Q}).encode(),{"Content-Type":"application/json"})
    a=json.load(urllib.request.urlopen(r,timeout=60))["answers"]
    lab="spam" if max(a["phish"]["noul"],a["scam"]["noul"])>0.5 else a["kind"]["choice"]
    routes[f]={"label":lab,"answers":a}; sec[lab].append(f"- {f}: {m['Subject']}")
json.dump(routes,open(sb+"/out/routes.json","w"),indent=2)
open(sb+"/out/triage.md","w").write("# Triage\n\n"+"\n\n".join(f"## {k.upper() if k=='fyi' else k.capitalize()}\n"+"\n".join(v) for k,v in sec.items())+"\n")
print("triage written")
