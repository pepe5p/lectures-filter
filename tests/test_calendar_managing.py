from freezegun import freeze_time
from icalendar import Calendar

from lectures_filter.calendar_managing import join_calendars
from tests.conftest import create_future_event, create_past_event, TEST_DATETIME


@freeze_time(TEST_DATETIME)
def test_join_calendars() -> None:
    past_event = create_past_event()
    future_event = create_future_event()

    new_calendar = Calendar()
    new_calendar.add_component(component=future_event)
    old_calendar = Calendar()
    old_calendar.add_component(component=past_event)
    old_calendar.add_component(component=future_event)

    joined_calendar = join_calendars(new_calendar=new_calendar, old_calendar=old_calendar)

    assert len(joined_calendar.walk(name="VEVENT")) == 2
