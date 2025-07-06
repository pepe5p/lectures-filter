import os
import warnings
from typing import Any, TYPE_CHECKING

import boto3
import requests
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from icalendar.cal import Calendar

from lectures_filter.calendar_managing import filter_calendar, join_calendars
from lectures_filter.filtering import filter_for_karasss

if TYPE_CHECKING:
    from types_boto3_s3 import S3Client

warnings.filterwarnings("ignore", message=".*maxsplit.*", category=DeprecationWarning, module=r"ics\.utils")

app = APIGatewayHttpResolver()

s3_client: "S3Client" = boto3.client("s3")

USOS_URL = os.getenv(
    "USOS_URL",
    "https://apps.usos.agh.edu.pl/services/tt/upcoming_ical?lang=pl&user_id={user_id}&key={key}",
)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "lectures-filter-bucket")


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
    user_id = "111784"
    key = "ZkrfPLwhRnzFZnA8uTUt"

    try:
        calendar = fetch_calendar(user_id=user_id, key=key)
    except requests.exceptions.RequestException as e:
        url = e.request.url if e.request else "unknown"
        return Response(
            status_code=400,
            content_type="text/plain",
            body=f"Failed to fetch calendar with url `{url}`: {e}",
        )

    saved_calendar = get_saved_calendar(user_id=user_id)
    joint_calendar = join_calendars(main_calendar=calendar, calendar_to_join=saved_calendar)
    filtered_calendar = filter_calendar(calendar=joint_calendar, filter_function=filter_for_karasss)

    return Response(
        status_code=200,
        content_type="text/plain; charset=utf-8",
        body=filtered_calendar.to_ical().decode("utf-8"),
    )


def fetch_calendar(user_id: str, key: str) -> Calendar:
    url = USOS_URL.format(user_id=user_id, key=key)
    response = requests.get(url=url)
    fetched_calendar = response.text
    return Calendar.from_ical(fetched_calendar)


def get_saved_calendar(user_id: str) -> Calendar:
    s3_key = f"u{user_id}.ics"
    path = f"/tmp/{s3_key}"
    s3_client.download_file(
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        Filename=path,
    )
    with open(path) as f:
        calendar = Calendar.from_ical(f.read())

    return calendar
