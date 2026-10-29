---
name: book-meeting
description: Add a meeting to Alex's calendar.ics as a valid iCalendar VEVENT without breaking the file.
version: 1.0.0
metadata:
  hermes:
    tags: [calendar, ics]
    requires_toolsets: [terminal]
---
# Book meeting

## When to Use
After a slot is chosen (use the find-free-slot skill first), to put the meeting into calendar.ics.

## Procedure
1. Run with the terminal tool from the sandbox folder (times UTC, 24h):
   `python3 $HERMES_HOME/skills/book-meeting/scripts/add_event.py "Project sync" 2026-11-05 14:00 14:45`
   (replace the date and times with the slot from find_slot.py).
2. Do NOT edit calendar.ics with write_file or patch: they break the CRLF line endings.

## Verification
Run `grep -n -A4 "Project sync" calendar.ics` and check DTSTART/DTEND match the slot. The script refuses to add the same meeting twice.
