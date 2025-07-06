import requests
from icalendar import Calendar

from lectures_filter.config import settings
from lectures_filter.user_config import USOSUserConfig


def fetch_calendar(usos_user_config: USOSUserConfig) -> Calendar:
    url = settings.usos_url.format(
        user_id=usos_user_config.user_id,
        key=usos_user_config.calendar_key,
    )
    response = requests.get(url=url)
    fetched_calendar = response.text
    return Calendar.from_ical(fetched_calendar)
