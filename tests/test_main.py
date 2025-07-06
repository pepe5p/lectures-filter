from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from icalendar import Calendar
from pytest_mock import MockerFixture

from lectures_filter.main import lambda_handler
from lectures_filter.user_config import UserConfig, USOSUserConfig


def test_lambda_handler(
    mocker: MockerFixture,
    api_gw_event: dict[str, Any],
    lambda_context: LambdaContext,
) -> None:
    mocker.patch("lectures_filter.main.fetch_calendar", return_value=Calendar())
    mock_s3_client_wrapper = mocker.patch("lectures_filter.main.s3_client_wrapper")
    mock_s3_client_wrapper.download_from_s3.side_effect = [
        UserConfig(
            usos=USOSUserConfig(
                user_id="123456",
                calendar_key="abcdefg",
            ),
        )
        .model_dump_json()
        .encode("utf-8"),
        Calendar().to_ical(),
    ]

    response = lambda_handler(event=api_gw_event, context=lambda_context)

    assert response["statusCode"] == 200, response["body"]
    assert "BEGIN:VCALENDAR" in response["body"]
