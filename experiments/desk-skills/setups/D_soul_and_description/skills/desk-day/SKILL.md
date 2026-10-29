---
name: desk-day
description: "REQUIRED FIRST for Alex desk jobs: to-dos, Bob meeting, reply. Use for ANY desk/Monday task BEFORE calling read_memos, calendar_busy, add_event or write_file: gives the exact tool order and output formats."
version: 1.0.0
metadata:
  hermes:
    tags: [desk, calendar, todo, email]
    requires_toolsets: [desk, file]
---
# Desk day

## When to Use
Whenever asked to do Alex's desk jobs.

## Procedure (call the tools in this order)
1. `list_inbox` — see the emails. Note inbox/05.eml's From (Jordan Lee <jordan@landlord.example>) and Subject.
2. `read_memos` — every sentence where Alex says he must/needs to/should do something is one to-do. Only memos, never emails. `write_file` out/todo.md:
   ```
   # To-do
   - [ ] <task> (due: <day if Alex said one>)
   ```
3. `calendar_busy` with other_availability_file="bob_availability.txt", minutes=45 — the line "Free for both" gives the slot. Book the first 45 minutes of it.
4. `add_event` summary="Project sync", date=YYYY-MM-DD, start=HH:MM, end=start+45min. Never edit calendar.ics with write_file or patch.
5. Reply draft: from the FREE ranges printed by calendar_busy, pick two 1-hour times on different days, fully inside FREE. `write_file` drafts/reply_05.eml:
   ```
   To: Jordan Lee <jordan@landlord.example>
   Subject: Re: <original subject>

   Hi Jordan,

   The engineer can come at either of these times:
   - <Day HH:MM-HH:MM>
   - <Day HH:MM-HH:MM>

   Best,
   Alex
   ```
6. Brief: `read_file` out/triage.md and out/expenses.csv; `write_file` out/brief.md with ## Urgent, ## Today (Monday's BUSY events), ## Expenses (sum of total).

## Pitfalls
- To: is the email's sender, never Alex. Never send.
- Do not change out/triage.md.

## Verification
The booked slot equals the "Free for both" start; each reply time sits inside a FREE range.
