"""Print Alex's busy and free times per weekday from calendar.ics (run from the sandbox folder)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__)); import deskcal
print(deskcal.week_text(sys.argv[1] if len(sys.argv) > 1 else "calendar.ics"))
