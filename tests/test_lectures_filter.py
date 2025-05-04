from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from freezegun import freeze_time
from icalendar import Calendar
from pytest_mock import MockerFixture

from calendar_managing import join_calendars
from lambda_function import lambda_handler
from tests.conftest import create_future_event, create_past_event, TEST_DATETIME


def test_lambda_handler(
    mocker: MockerFixture,
    api_gw_event: APIGatewayProxyEventV2,
    lambda_context: LambdaContext,
) -> None:
    mocker.patch("lambda_function.get_saved_calendar", return_value=Calendar())
    response = lambda_handler(event=api_gw_event, context=lambda_context)
    assert response["statusCode"] == 200
    assert "BEGIN:VCALENDAR" in response["body"]


@freeze_time(TEST_DATETIME)
def test_join_calendars() -> None:
    past_event = create_past_event()
    future_event = create_future_event()

    calendar = Calendar()
    calendar.add_component(component=future_event)
    saved_calendar = Calendar()
    saved_calendar.add_component(component=past_event)
    saved_calendar.add_component(component=future_event)

    joined_calendar = join_calendars(calendar=calendar, saved_calendar=saved_calendar)

    assert len(joined_calendar.walk(name="VEVENT")) == 2
