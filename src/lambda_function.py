import warnings
from typing import Any

import requests
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from icalendar.cal import Calendar, Component, Event

warnings.filterwarnings("ignore", message=".*maxsplit.*", category=DeprecationWarning, module=r"ics\.utils")

app = APIGatewayHttpResolver()


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    return app.resolve(event, context)


@app.get("/")
def main() -> Response[str]:
    url = "https://apps.usos.agh.edu.pl/services/tt/upcoming_ical?lang=pl&user_id=111784&key=ZkrfPLwhRnzFZnA8uTUt"

    try:
        calendar = fetch_calendar(url=url)
    except requests.exceptions.RequestException as e:
        return Response(
            status_code=400,
            content_type="text/plain",
            body=f"Failed to fetch calendar with url {url}: {e}",
        )

    filtered_calendar = filter_lectures(calendar=calendar)

    return Response(
        status_code=200,
        content_type="text/plain; charset=utf-8",
        body=filtered_calendar.to_ical().decode("utf-8"),
    )


def fetch_calendar(url: str) -> Calendar:
    response = requests.get(url=url)
    fetched_calendar = response.text
    return Calendar.from_ical(fetched_calendar)


def filter_lectures(calendar: Calendar) -> Calendar:
    new_cal = Calendar()

    for prop, value in calendar.items():
        new_cal.add(prop, value)

    for component in calendar.walk():
        if not is_event(component=component):
            continue
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
