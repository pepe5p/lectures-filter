from datetime import datetime
from typing import Callable, cast

from icalendar import Calendar, Event
from icalendar.cal import Component


def join_calendars(main_calendar: Calendar, calendar_to_join: Calendar) -> Calendar:
    new_cal = copy_calendar_without_components(calendar=main_calendar)

    for component in calendar_to_join.walk(name="VEVENT", select=is_past_event):
        new_cal.add_component(component=component)

    for component in main_calendar.walk(name="VEVENT", select=is_future_event):
        new_cal.add_component(component=component)

    return new_cal


def is_past_event(event: Event) -> bool:
    return event["DTSTART"].dt < datetime.now()


def is_future_event(event: Event) -> bool:
    return not is_past_event(event=event)


def filter_calendar(calendar: Calendar, filter_function: Callable[[Event], bool]) -> Calendar:
    new_cal = copy_calendar_without_components(calendar=calendar)

    for event in calendar.walk(name="VEVENT"):
        event = cast(Event, event)

        if not filter_function(event):
            continue

        add_to_description(event=event, text=f"UID: {event.get("UID")}")
        new_cal.add_component(component=event)

    return new_cal


def is_event(component: Component) -> bool:
    return component.name == "VEVENT"


def add_to_description(event: Event, text: str) -> None:
    event["DESCRIPTION"] += f"\n{text}"


def copy_calendar_without_components(calendar: Calendar) -> Calendar:
    new_cal = Calendar()

    for prop, value in calendar.items():
        new_cal.add(prop, value)

    return new_cal
