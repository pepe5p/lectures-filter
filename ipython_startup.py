from pathlib import Path

from icalendar import Calendar

from lambda_function import *

url = "https://apps.usos.agh.edu.pl/services/tt/upcoming_ical?lang=pl&user_id=111784&key=ZkrfPLwhRnzFZnA8uTUt"
path = Path("u111784.ics").resolve()
result_path = Path("result.ics").resolve()

with open(path) as f:
    calendar = Calendar.from_ical(f.read())

filtered_calendar = filter_lectures(calendar)

with open(result_path, "w") as f:
    f.writelines(filtered_calendar.to_ical().decode("utf-8"))
