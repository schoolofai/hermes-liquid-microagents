"""desk-tools: calendar_busy, list_inbox, read_memos, add_event (all relative to the agent's cwd = sandbox)."""
import json, glob, os, email, importlib.util
_spec = importlib.util.spec_from_file_location("deskcal", os.path.join(os.path.dirname(__file__), "deskcal.py"))
deskcal = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(deskcal)

def _obj(props, req=()): return {"type": "object", "properties": props, "required": list(req)}

def calendar_busy(params, **kw):
    try:
        txt = deskcal.week_text("calendar.ics")
        other = params.get("other_availability_file"); mins = int(params.get("minutes") or 0)
        if other:
            sl = deskcal.common_slots(other, mins or 30)
            txt += "\n\nFree for both (Alex + " + other + "): " + ("; ".join(f"{deskcal.fmt(s.date())} {s:%H:%M}-{e:%H:%M}" for s, e in sl) or "none")
        return json.dumps({"success": True, "calendar": txt})
    except Exception as e: return json.dumps({"success": False, "error": str(e)})

def list_inbox(params, **kw):
    out = []
    for p in sorted(glob.glob("inbox/*.eml")):
        m = email.message_from_string(open(p).read())
        out.append({"file": p, "from": m["From"], "subject": m["Subject"]})
    return json.dumps({"success": True, "emails": out})

def read_memos(params, **kw):
    return json.dumps({"success": True, "memos": {os.path.basename(p): open(p).read().strip() for p in sorted(glob.glob("out/transcripts/memo*.txt"))}})

def add_event(params, **kw):
    try: return json.dumps({"success": True, "result": deskcal.add_event(params["summary"], params["date"], params["start"], params["end"])})
    except Exception as e: return json.dumps({"success": False, "error": str(e)})

def register(ctx):
    T = "desk"
    ctx.register_tool(name="calendar_busy", toolset=T, handler=calendar_busy, schema={"name": "calendar_busy",
        "description": "Alex's week from calendar.ics: BUSY and FREE times per weekday (UTC, 09:00-17:00). Give other_availability_file (e.g. bob_availability.txt) and minutes to also get the times free for both.",
        "parameters": _obj({"other_availability_file": {"type": "string"}, "minutes": {"type": "integer"}})})
    ctx.register_tool(name="list_inbox", toolset=T, handler=list_inbox, schema={"name": "list_inbox",
        "description": "List emails in inbox/ with file name, From and Subject.", "parameters": _obj({})})
    ctx.register_tool(name="read_memos", toolset=T, handler=read_memos, schema={"name": "read_memos",
        "description": "Return the text of all of Alex's voice memo transcripts (the only source of to-dos).", "parameters": _obj({})})
    ctx.register_tool(name="add_event", toolset=T, handler=add_event, schema={"name": "add_event",
        "description": "Add a meeting to calendar.ics as a valid VEVENT (UTC). Never edit calendar.ics any other way.",
        "parameters": _obj({"summary": {"type": "string"}, "date": {"type": "string", "description": "YYYY-MM-DD"},
                            "start": {"type": "string", "description": "HH:MM"}, "end": {"type": "string", "description": "HH:MM"}}, ["summary", "date", "start", "end"])})
