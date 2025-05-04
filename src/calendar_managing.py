from datetime import datetime

from icalendar import Calendar, Event
from icalendar.cal import Component


def join_calendars(calendar: Calendar, saved_calendar: Calendar) -> Calendar:
    new_cal = copy_calendar_without_components(calendar=calendar)

    for component in saved_calendar.walk(name="VEVENT", select=is_past_event):
        new_cal.add_component(component=component)

    for component in calendar.walk(name="VEVENT", select=is_future_event):
        new_cal.add_component(component=component)

    return new_cal


def is_past_event(event: Event) -> bool:
    return event["DTSTART"].dt < datetime.now()


def is_future_event(event: Event) -> bool:
    return not is_past_event(event=event)


def filter_lectures(calendar: Calendar) -> Calendar:
    new_cal = copy_calendar_without_components(calendar=calendar)

    for component in calendar.walk(name="VEVENT"):
        event: Event = component

        if not is_obligatory(event=event):
            continue

        add_to_description(event=event, text=f"UID: {event.get("UID")}")
        new_cal.add_component(component=component)

    return new_cal


def is_event(component: Component) -> bool:
    return component.name == "VEVENT"


def is_obligatory(event: Event) -> bool:
    summary = event["SUMMARY"]

    if summary.startswith("W - Knowledge Management in Critical Infrastructure"):
        return True

    if summary.startswith("CWP - Development Workshop"):
        return False

    return not summary.startswith("W")


def add_to_description(event: Event, text: str) -> None:
    event["DESCRIPTION"] += f"\n{text}"


def copy_calendar_without_components(calendar: Calendar) -> Calendar:
    new_cal = Calendar()

    for prop, value in calendar.items():
        new_cal.add(prop, value)

    return new_cal
