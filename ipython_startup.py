from datetime import datetime
from pathlib import Path

from icalendar import Event
from lectures_filter.main import *
from lectures_filter.filtering import filter_for_karasss

url = "https://apps.usos.agh.edu.pl/services/tt/upcoming_ical?lang=pl&user_id=111784&key=ZkrfPLwhRnzFZnA8uTUt"
path = Path("u111784.ics").resolve()
result_path = Path("result.ics").resolve()

with open(path) as f:
    calendar = Calendar.from_ical(f.read())

filtered_calendar = filter_calendar(calendar, filter_function=filter_for_karasss)

with open(result_path, "w") as f:
    f.writelines(filtered_calendar.to_ical().decode("utf-8"))
