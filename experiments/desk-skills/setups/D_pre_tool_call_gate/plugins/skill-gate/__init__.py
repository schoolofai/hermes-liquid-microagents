"""pre_tool_call gate: desk tools and write_file are blocked until skill_view(name='desk-day') was called."""
_opened = set()
GATED = {"calendar_busy", "add_event", "read_memos", "list_inbox", "write_file", "patch"}
def _pre(tool_name, args, task_id="", **kw):
    if tool_name == "skill_view" and (args or {}).get("name") == "desk-day":
        _opened.add(task_id or "_"); return None
    if tool_name in GATED and (task_id or "_") not in _opened:
        return {"action": "block", "message": "Blocked: call skill_view with name=\"desk-day\" first, then follow its Procedure step by step."}
    return None
def register(ctx): ctx.register_hook("pre_tool_call", _pre)
