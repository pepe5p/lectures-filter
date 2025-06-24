from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from icalendar import Calendar
from pytest_mock import MockerFixture

from lectures_filter.main import lambda_handler


def test_lambda_handler(
    mocker: MockerFixture,
    api_gw_event: APIGatewayProxyEventV2,
    lambda_context: LambdaContext,
) -> None:
    mocker.patch("lectures_filter.main.get_saved_calendar", return_value=Calendar())
    response = lambda_handler(event=api_gw_event, context=lambda_context)
    assert response["statusCode"] == 200
    assert "BEGIN:VCALENDAR" in response["body"]
