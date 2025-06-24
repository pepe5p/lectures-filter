from freezegun import freeze_time
from icalendar import Calendar

from lectures_filter.calendar_managing import join_calendars
from tests.conftest import create_future_event, create_past_event, TEST_DATETIME


@freeze_time(TEST_DATETIME)
def test_join_calendars() -> None:
    past_event = create_past_event()
    future_event = create_future_event()

    calendar = Calendar()
    calendar.add_component(component=future_event)
    saved_calendar = Calendar()
    saved_calendar.add_component(component=past_event)
    saved_calendar.add_component(component=future_event)

    joined_calendar = join_calendars(main_calendar=calendar, calendar_to_join=saved_calendar)

    assert len(joined_calendar.walk(name="VEVENT")) == 2
