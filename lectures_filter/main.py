from typing import Any

import requests
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext

from lectures_filter.calendar_managing import filter_calendar, join_calendars
from lectures_filter.clients.s3 import s3_client_wrapper, UserCalendarRepository, UserConfigNotFoundError
from lectures_filter.clients.usos import fetch_calendar

app = APIGatewayHttpResolver()


@app.get("/<usos_user_id>/calendar")
def main(usos_user_id: str) -> Response[str]:
    user_calendar_repository = UserCalendarRepository(
        s3_client_wrapper=s3_client_wrapper,
        user_id=usos_user_id,
    )

    try:
        user_config = user_calendar_repository.get_user_config()
    except UserConfigNotFoundError as e:
        return Response(
            status_code=404,
            content_type="text/plain",
            body=f"User config not found for user ID `{usos_user_id}`: {e}",
        )

    try:
        calendar = fetch_calendar(usos_user_config=user_config.usos)
    except requests.exceptions.RequestException as e:
        url = e.request.url if e.request else "unknown"
        return Response(
            status_code=400,
            content_type="text/plain",
            body=f"Failed to fetch calendar with url `{url}`: {e}",
        )

    saved_calendar = user_calendar_repository.get_saved_calendar()
    joint_calendar = join_calendars(new_calendar=calendar, old_calendar=saved_calendar)
    user_calendar_repository.save_calendar(calendar=joint_calendar)
    filtered_calendar = filter_calendar(
        calendar=joint_calendar,
        filter_function=user_config.filtering.should_include_event,
    )

    return Response(
        status_code=200,
        content_type="text/plain; charset=utf-8",
        body=filtered_calendar.to_ical().decode("utf-8"),
    )


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: LambdaContext, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    return app.resolve(event, context)
