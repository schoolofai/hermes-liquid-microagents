"""Small calendar helpers shared by the B skills' scripts and the C plugin tools."""
import re, datetime as dt
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
def events(path="calendar.ics"):
    txt = open(path).read()
    out = []
    for b in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", txt, re.S):
        g = lambda k: (re.search(rf"^{k}[^:\r\n]*:([^\r\n]*)", b, re.M) or [None, ""])[1].strip()
        s, e = dt.datetime.strptime(g("DTSTART"), "%Y%m%dT%H%M%SZ"), dt.datetime.strptime(g("DTEND"), "%Y%m%dT%H%M%SZ")
        out.append((s, e, g("SUMMARY")))
    return sorted(out)
def week(path="calendar.ics", start="09:00", end="17:00"):
    """{date: {'busy': [(s,e,title)], 'free': [(s,e)]}} for Mon-Fri of the calendar's week (UTC)."""
    ev = events(path); mon = min(s for s, _, _ in ev).date(); mon -= dt.timedelta(days=mon.weekday())
    res = {}
    for i in range(5):
        d = mon + dt.timedelta(days=i)
        ws = dt.datetime.combine(d, dt.time.fromisoformat(start)); we = dt.datetime.combine(d, dt.time.fromisoformat(end))
        busy = [(s, e, t) for s, e, t in ev if s.date() == d]; free = []; cur = ws
        for s, e, _ in busy:
            if s > cur: free.append((cur, min(s, we)))
            cur = max(cur, e)
        if cur < we: free.append((cur, we))
        res[d] = {"busy": busy, "free": [(a, b) for a, b in free if b > a]}
    return res
def fmt(d): return f"{DAYS[d.weekday()]} {d.isoformat()}"
def week_text(path="calendar.ics"):
    lines = []
    for d, v in week(path).items():
        lines.append(f"{fmt(d)}  BUSY: " + (", ".join(f"{s:%H:%M}-{e:%H:%M} {t}" for s, e, t in v["busy"]) or "none")
                     + "  |  FREE (09:00-17:00): " + (", ".join(f"{a:%H:%M}-{b:%H:%M}" for a, b in v["free"]) or "none"))
    return "All times UTC.\n" + "\n".join(lines)
def parse_windows(path):
    """Lines like 'Thu 14:00-15:00' -> [(dayname, start, end)]."""
    return [(m[0][:3].title(), m[1], m[2]) for m in re.findall(r"\b(Mon|Tue|Wed|Thu|Fri)\w*\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", open(path).read(), re.I)]
def common_slots(other_path, minutes, path="calendar.ics"):
    out = []
    w = week(path)
    for dname, a, b in parse_windows(other_path):
        d = next(x for x in w if DAYS[x.weekday()] == dname)
        oa = dt.datetime.combine(d, dt.time.fromisoformat(a.zfill(5))); ob = dt.datetime.combine(d, dt.time.fromisoformat(b.zfill(5)))
        for fa, fb in w[d]["free"]:
            s, e = max(fa, oa), min(fb, ob)
            if (e - s).total_seconds() >= minutes * 60: out.append((s, e))
    return out
def add_event(summary, date, start, end, path="calendar.ics", uid=None):
    """Insert a valid VEVENT before END:VCALENDAR, keeping the file's line endings."""
    txt = open(path, newline="").read(); nl = "\r\n" if "\r\n" in txt else "\n"
    ds = date.replace("-", ""); s = start.replace(":", "").zfill(4); e = end.replace(":", "").zfill(4)
    if f"SUMMARY:{summary}" in txt: return f"already present: {summary}"
    block = nl.join(["BEGIN:VEVENT", f"UID:{uid or summary.lower().replace(' ', '-')}@desk.example",
                     f"DTSTART:{ds}T{s}00Z", f"DTEND:{ds}T{e}00Z", f"SUMMARY:{summary}", "END:VEVENT", "END:VCALENDAR"])
    i = txt.rstrip().rfind("END:VCALENDAR")
    if i < 0: raise ValueError("calendar.ics has no END:VCALENDAR")
    open(path, "w", newline="").write(txt[:i] + block + nl)
    return f"added {summary} {date} {start}-{end} UTC"
