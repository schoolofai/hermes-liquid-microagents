---
name: find-free-slot
description: Read Alex's calendar.ics and find when Alex is busy/free, or a meeting slot that also fits another person's availability file.
version: 1.0.0
metadata:
  hermes:
    tags: [calendar, scheduling]
    requires_toolsets: [terminal]
---
# Find free slot

## When to Use
Any job that needs to know when Alex is busy or free, or needs a meeting time with someone (e.g. Bob).

## Procedure
1. See Alex's whole week (busy and free, UTC) — run with the terminal tool from the sandbox folder:
   `python3 $HERMES_HOME/skills/find-free-slot/scripts/cal_week.py calendar.ics`
2. To meet someone, pass their availability file and the meeting length in minutes:
   `python3 $HERMES_HOME/skills/find-free-slot/scripts/find_slot.py bob_availability.txt 45`
   It prints the one slot free for both and the exact start/end to book.
3. Use these printed times. Do not work out times in your head.

## Pitfalls
- calendar.ics is in the sandbox ROOT, not out/.
- All times are UTC. Every VEVENT is busy time.

## Verification
The slot you use must be one printed by find_slot.py (for meetings) or inside a FREE range from cal_week.py.
