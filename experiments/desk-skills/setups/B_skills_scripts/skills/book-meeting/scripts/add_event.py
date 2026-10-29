"""add_event.py "SUMMARY" YYYY-MM-DD HH:MM HH:MM  -> appends a valid VEVENT to calendar.ics (UTC)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__)); import deskcal
print(deskcal.add_event(*sys.argv[1:5]))
