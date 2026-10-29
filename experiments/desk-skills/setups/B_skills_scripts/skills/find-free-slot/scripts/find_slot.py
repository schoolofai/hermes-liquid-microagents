"""find_slot.py OTHER_AVAILABILITY_FILE MINUTES -> times free for both Alex (calendar.ics) and the other person."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__)); import deskcal
other, mins = sys.argv[1], int(sys.argv[2])
slots = deskcal.common_slots(other, mins)
if not slots: print("no common slot"); sys.exit(1)
for s, e in slots:
    print(f"{deskcal.fmt(s.date())} {s:%H:%M}-{e:%H:%M} UTC is free for both; book {s:%H:%M} to {(s + __import__('datetime').timedelta(minutes=mins)):%H:%M}")
