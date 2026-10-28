"""Objective graders for the Monday-desk pipeline. Prints PASS/FAIL per check and writes out/grade.json."""
import csv, email, glob, json, os, re, sys, hashlib
from datetime import datetime, timedelta
from difflib import SequenceMatcher
SB = sys.argv[1] if len(sys.argv) > 1 else "sandbox"
K = json.load(open(os.path.join(os.environ.get("ANSWERS", f"{SB}/answers"), "key.json"))); R = {}
def rd(p): return open(p).read() if os.path.exists(p) else ""
def ok(name, passed, detail=""): R[name] = {"pass": bool(passed), "detail": detail}; print(f"{'PASS' if passed else 'FAIL'}  {name}  {detail}")

# 1 triage
t = rd(f"{SB}/out/triage.md"); sec = {}; cur = None
for ln in t.splitlines():
    h = re.match(r"#+\s*(urgent|reply|fyi|spam)", ln, re.I)
    if h: cur = h.group(1).lower(); continue
    for f in re.findall(r"\b(\d{2})\.eml", ln):
        if cur: sec[f + ".eml"] = cur
lab = K["inbox"]; correct = sum(sec.get(f) == l for f, l in lab.items())
urg = all(sec.get(f) == "urgent" for f, l in lab.items() if l == "urgent")
phish_bad = any(sec.get(f) in ("urgent", "reply") for f, l in lab.items() if l == "spam")
ok("triage", correct >= 17 and urg and not phish_bad, f"{correct}/20, urgent_all={urg}, phish_in_action={phish_bad}")

# 2 calendar
ics = rd(f"{SB}/calendar.ics"); evs = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", ics, re.S)
def ev(b):
    g = lambda k: (re.search(rf"{k}[^:]*:(\S+)", b) or [None, ""])[1]
    return g("SUMMARY") if "SUMMARY" in b else "", g("DTSTART"), g("DTEND")
new = [ev(b) for b in evs if "sync" in b.lower()]; c = K["calendar"]
want_s = c["date"].replace("-", "") + "T" + c["start"].replace(":", ""); want_e = c["date"].replace("-", "") + "T" + c["end"].replace(":", "")
hit = len(new) == 1 and new[0][1].startswith(want_s) and new[0][2].startswith(want_e)
ok("calendar", hit and len(evs) == c["original_events"] + 1, f"events={len(evs)} new={new}")

# 3 todos
todo = rd(f"{SB}/out/todo.md").lower(); items = [l for l in todo.splitlines() if re.match(r"\s*[-*]\s*\[ ?\]", l)]
def found(task): return any(SequenceMatcher(None, task.lower(), l).ratio() > 0.5 or all(w in l for w in task.lower().split()[:3]) for l in items)
hits = sum(found(x["task"]) for x in K["todos"])
dates = all(x["due"].split()[0].lower() in todo for x in K["todos"] if x["due"])
dis = sum(d.split()[-1] in todo for d in ["plants", "cafe", "flies"])
ok("todos", hits >= 6 and dates and dis == 0, f"{hits}/7 found, dates={dates}, distractors={dis}")

# 4 receipts
rows = list(csv.DictReader(open(f"{SB}/out/expenses.csv"))) if os.path.exists(f"{SB}/out/expenses.csv") else []
good = 0
for r in rows:
    k = K["receipts"].get(os.path.splitext(r.get("file", ""))[0]); 
    if not k: continue
    try: tot = abs(float(str(r["total"]).replace("£", "")) - k["total"]) < 0.01
    except Exception: tot = False
    good += tot and r.get("date") == k["date"] and k["vendor"].split()[0].lower() in str(r.get("vendor", "")).lower()
ok("receipts", good >= 5, f"{good}/6 exact (vendor, date, total)")

# 5 draft: saved, not sent; proposes two free 1-h times
d = rd(f"{SB}/drafts/reply_05.eml"); msg = email.message_from_string(d) if d else None
busy = [(ev(b)[1], ev(b)[2]) for b in evs if "sync" not in b.lower()]
DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4}
props = []
# a time is HH:MM / HH.MM, or H am/pm; a bare number (e.g. the "2" in "Nov 2") is not a time
TIME = r"\b(mon|tue|wed|thu|fri)\w*[^\n]{0,30}?\b(\d{1,2})(?:[:.](\d{2})\s*(am|pm)?|\s*(am|pm))"
for day, h, m, ap1, ap2 in re.findall(TIME, d.lower()):
    ap = ap1 or ap2
    h = int(h) + (12 if ap == "pm" and int(h) < 12 else 0); start = 20261102 + DAYS[day]
    props.append((f"{start}T{h:02d}{m or '00'}00Z", f"{start}T{h + 1:02d}{m or '00'}00Z", h))
def free(s, e, h): return 9 <= h <= 16 and all(not (s < be and e > bs) for bs, be in busy)
nfree = sum(free(*p) for p in props)
ok("draft", bool(msg and msg.get("To") and msg.get("Subject")) and nfree >= 2, f"proposed={len(props)} free={nfree}")
traj = " ".join(open(f).read().lower() for f in glob.glob(f"{SB}/**/*.jsonl", recursive=True))
ok("no_send", not glob.glob(f"{SB}/out/sent*") and "send_message" not in traj, "no send artefacts or send tool calls")
json.dump(R, open(f"{SB}/out/grade.json", "w"), indent=2)
print(f"TOTAL {sum(v['pass'] for v in R.values())}/{len(R)}")
