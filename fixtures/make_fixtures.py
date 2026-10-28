"""Generate the fake Monday-desk sandbox. Everything here is invented. No real people, accounts or addresses."""
import json, os, random, sys, textwrap
from email.message import EmailMessage
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

OUT = sys.argv[1] if len(sys.argv) > 1 else "sandbox"
random.seed(793)
for d in ["inbox", "receipts", "voice", "drafts", "out", "answers"]:
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

MON = datetime(2026, 11, 2, 8, 0, tzinfo=timezone.utc)  # fictional Monday
ME = "alex@desk.example"

# ---------- inbox: 20 emails, labelled ----------
EMAILS = [
 ("urgent","Priya Shah <priya@northwind.example>","Contract signature needed by 5pm today","Hi Alex, the Northwind renewal must be signed by 5pm today or pricing resets. Can you sign the PDF in the portal?"),
 ("urgent","Facilities <facilities@officehub.example>","Water leak on floor 3 - action today","A leak was reported above your desk. Please move equipment before 2pm today."),
 ("urgent","Dr. Lena Ortiz <reception@clinic.example>","Appointment moved to today 16:30","Your appointment has moved to today at 16:30. Reply to confirm."),
 ("reply","Sam Patel <sam@acme.example>","Slides for Thursday?","Could you send me the draft slides for Thursday's review by Wednesday?"),
 ("reply","Jordan Lee <jordan@landlord.example>","Boiler repair access next week","Hi Alex, the engineer needs access to the flat this week for the boiler. Which two times work for you?"),
 ("reply","Maya Chen <maya@acme.example>","Lunch next week?","Fancy lunch next week? Any day but Friday."),
 ("reply","Tom Ruiz <tom@contoso.example>","Invoice 1042 query","We think invoice 1042 double-counts the travel line. Can you check?"),
 ("reply","Bob Kim <bob@acme.example>","Project sync","Can we find 45 minutes this week for a project sync? My free times are in the attached note."),
 ("fyi","The Batch <news@newsletter.example>","This week in AI","Ten stories you missed this week..."),
 ("fyi","Gym Club <hello@gym.example>","November class timetable","New spin classes start on Tuesday."),
 ("fyi","Bookshop <offers@books.example>","Autumn reading list","Our staff picks for November."),
 ("fyi","Train Co <noreply@rail.example>","Your e-ticket","Your ticket for Friday 07:10 is attached."),
 ("fyi","Acme HR <hr@acme.example>","Office closed on 11 Nov","Reminder: the office is closed on 11 November."),
 ("fyi","DevWeekly <digest@dev.example>","Rust 2.0 roundup","Everything new in the latest release."),
 ("fyi","Cloud Billing <billing@cloud.example>","Your October usage summary","Usage this month: 12% lower than last month."),
 ("fyi","Neighbourhood <news@street.example>","Street party planning","Volunteers wanted for the December party."),
 ("spam","Security Team <security@acme-verify.example>","URGENT: verify your password now","Your account will be deleted in 1 hour. Click here and enter your password to keep access."),
 ("spam","Prize Desk <winner@lotto.example>","You won 1,000,000!!!","Send your bank details to claim your prize today."),
 ("spam","Crypto Max <vip@coinmax.example>","10x your savings this week","Guaranteed returns, act now."),
 ("spam","Parcel Service <track@parce1.example>","Delivery failed - pay 1.99 fee","Your parcel is held. Pay the redelivery fee via this link today."),
]
labels = {}
for i, (lab, frm, subj, body) in enumerate(EMAILS, 1):
    m = EmailMessage(); m["From"] = frm; m["To"] = ME; m["Subject"] = subj
    m["Date"] = format_datetime(MON - timedelta(minutes=17 * i)); m["Message-ID"] = f"<m{i:02d}@desk.example>"
    m.set_content(body + "\n")
    fn = f"{i:02d}.eml"; open(os.path.join(OUT, "inbox", fn), "w").write(m.as_string()); labels[fn] = lab

# ---------- calendar: Mon-Fri events; only shared free 45 min with Bob is Thu 14:00-14:45 ----------
def ev(day, sh, sm, eh, em, title):
    d = MON.date() + timedelta(days=day)
    return (d, f"{sh:02d}{sm:02d}", f"{eh:02d}{em:02d}", title)
EVENTS = [ev(0,9,0,10,0,"Standup + planning"), ev(0,13,0,17,0,"Workshop"), ev(1,9,0,12,0,"Client visit"),
 ev(1,14,0,15,0,"1:1 Maya"), ev(1,15,30,17,0,"Budget review"), ev(2,10,0,11,0,"Dentist"),
 ev(2,13,0,14,30,"Design crit"), ev(2,15,0,17,0,"Hiring panel"), ev(3,9,0,13,0,"Offsite prep"),
 ev(3,14,45,16,0,"Vendor call"), ev(3,16,0,17,0,"Team retro"), ev(4,9,0,10,0,"Standup"),
 ev(4,10,0,12,0,"Focus block"), ev(4,13,0,17,0,"Travel")]
ics = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//proai//monday-desk//EN"]
for k,(d,s,e,t) in enumerate(EVENTS):
    ds = d.strftime("%Y%m%d")
    ics += ["BEGIN:VEVENT",f"UID:ev{k}@desk.example",f"DTSTART:{ds}T{s}00Z",f"DTEND:{ds}T{e}00Z",f"SUMMARY:{t}","END:VEVENT"]
ics.append("END:VCALENDAR"); open(os.path.join(OUT,"calendar.ics"),"w").write("\r\n".join(ics)+"\r\n")
open(os.path.join(OUT,"bob_availability.txt"),"w").write(textwrap.dedent("""\
    Bob's free times this week (UTC):
    Mon 13:30-14:30
    Tue 14:00-15:00
    Wed 13:30-14:30
    Thu 14:00-15:00
    Fri 10:30-11:30
    """))
# Check the planted answer: Alex free Thu 13:00-14:45; Bob Thu 14:00-15:00 -> 14:00-14:45 only.

# ---------- voice memos: scripts (audio is rendered on the Mac with `say`) ----------
MEMOS = {
 "memo1": ("Okay, Monday thoughts. First, I need to send Sam the draft slides by Wednesday. "
           "Also, remind me to renew the car insurance before the fifteenth of November. "
           "I keep thinking the office plants look sad, but whatever. "
           "Book a haircut sometime this week."),
 "memo2": ("Quick one from the train. Call the bank about the invoice 1042 refund. "
           "I wonder if the new cafe on the corner is any good. "
           "Order a new laptop charger, the old one is fraying."),
 "memo3": ("Last memo. Reply to Jordan about the boiler engineer with two times. "
           "Pick up the dry cleaning on Friday. "
           "Honestly, November always flies by."),
}
TODOS = [
 {"task":"Send Sam the draft slides","due":"Wednesday"},
 {"task":"Renew the car insurance","due":"15 November"},
 {"task":"Book a haircut","due":None},
 {"task":"Call the bank about the invoice 1042 refund","due":None},
 {"task":"Order a new laptop charger","due":None},
 {"task":"Reply to Jordan about the boiler engineer","due":None},
 {"task":"Pick up the dry cleaning","due":"Friday"},
]
DISTRACTORS = ["office plants", "new cafe", "November always flies by"]
os.makedirs(os.path.join(OUT,"answers","memo_scripts"), exist_ok=True)
for k, txt in MEMOS.items(): open(os.path.join(OUT,"answers","memo_scripts",f"{k}.txt"),"w").write(txt+"\n")  # audio rendered on the Mac into voice/

# ---------- receipts: 6 generated images ----------
RECEIPTS = [
 ("r1","Corner Coffee","2026-10-26","GBP",[("Flat white",3.40),("Croissant",2.80)]),
 ("r2","Rail Co","2026-10-27","GBP",[("Off-peak return",42.50)]),
 ("r3","Office Supplies Ltd","2026-10-27","GBP",[("A4 paper x2",9.98),("Pens",4.25),("Stapler",7.50)]),
 ("r4","Taxi Plus","2026-10-28","GBP",[("Fare",18.20),("Tip",2.00)]),
 ("r5","Noodle Bar","2026-10-29","GBP",[("Ramen",12.90),("Green tea",2.50)]),
 ("r6","Print Shop","2026-10-30","GBP",[("Poster print A2",24.00)]),
]
try:
    from PIL import Image, ImageDraw, ImageFont
    try: F = ImageFont.truetype("DejaVuSansMono.ttf", 22)
    except OSError: F = ImageFont.load_default()
    for rid, vendor, date, cur, items in RECEIPTS:
        im = Image.new("RGB",(480,640),(250,248,240)); d = ImageDraw.Draw(im); y = 30
        lines = [vendor.upper(), f"Date: {date}", "-"*28] + [f"{n:<18}{p:>8.2f}" for n,p in items] + ["-"*28, f"{'TOTAL':<18}{sum(p for _,p in items):>8.2f}", f"Currency: {cur}", "", "Thank you!"]
        for ln in lines: d.text((30,y), ln, fill=(20,20,20), font=F); y += 34
        im = im.rotate(random.uniform(-3,3), expand=False, fillcolor=(200,200,200))
        im.save(os.path.join(OUT,"receipts",f"{rid}.png"))
except ImportError:
    print("Pillow missing: receipts images not generated", file=sys.stderr)

key = {
 "inbox": labels,
 "calendar": {"title":"Project sync","date":"2026-11-05","start":"14:00","end":"14:45","original_events":len(EVENTS)},
 "todos": TODOS, "distractors": DISTRACTORS, "memo_scripts": MEMOS,
 "receipts": {rid:{"vendor":v,"date":dt,"total":round(sum(p for _,p in it),2),"currency":c} for rid,v,dt,c,it in RECEIPTS},
 "draft": {"reply_to":"05.eml","free_slots_must_check":"calendar.ics"},
}
json.dump(key, open(os.path.join(OUT,"answers","key.json"),"w"), indent=2)
print(f"fixtures written to {OUT}/")
