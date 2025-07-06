from typing import TYPE_CHECKING

import boto3
from icalendar import Calendar

from lectures_filter.config import settings
from lectures_filter.user_config import UserConfig

if TYPE_CHECKING:
    from types_boto3_s3 import S3Client

s3_client: "S3Client" = boto3.client("s3")


class UserConfigNotFoundError(Exception):
    def __init__(self, s3_key: str) -> None:
        self.s3_key = s3_key


def get_user_config(user_id: str) -> UserConfig:
    s3_key = f"u{user_id}.json"
    try:
        path = download_from_s3(s3_key=s3_key)
    except s3_client.exceptions.NoSuchKey:
        raise UserConfigNotFoundError(s3_key=s3_key)

    with open(path) as f:
        user_config = UserConfig.model_validate_json(f.read())

    return user_config


def get_saved_calendar(user_id: str) -> Calendar:
    s3_key = f"u{user_id}.ics"
    path = download_from_s3(s3_key=s3_key)

    with open(path) as f:
        calendar = Calendar.from_ical(f.read())

    return calendar


def download_from_s3(s3_key: str) -> str:
    path = f"/tmp/{s3_key}"
    s3_client.download_file(
        Bucket=settings.s3_bucket_name,
        Key=s3_key,
        Filename=path,
    )
    return path
