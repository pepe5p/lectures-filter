from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import ClientError
from icalendar import Calendar

from lectures_filter.config import settings
from lectures_filter.user_config import UserConfig

if TYPE_CHECKING:
    from types_boto3_s3 import S3Client


class S3ClientWrapper:
    def __init__(self, s3_client: "S3Client") -> None:
        self.s3_client = s3_client

    def download_from_s3(self, s3_key: str) -> bytes:
        s3_object = self.s3_client.get_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
        )
        return s3_object["Body"].read()

    def upload_to_s3(self, s3_key: str, content: bytes) -> None:
        self.s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=content,
        )


s3_client: "S3Client" = boto3.client("s3")
s3_client_wrapper = S3ClientWrapper(s3_client=s3_client)


class UserConfigNotFoundError(Exception):
    def __init__(self, s3_key: str) -> None:
        self.s3_key = s3_key


class UserCalendarRepository:
    def __init__(self, s3_client_wrapper: S3ClientWrapper, user_id: str) -> None:
        self.s3_client_wrapper = s3_client_wrapper
        self.user_id = user_id

    @property
    def user_config_s3_key(self) -> str:
        return f"u{self.user_id}.json"

    @property
    def calendar_s3_key(self) -> str:
        return f"u{self.user_id}.ics"

    def get_user_config(self) -> UserConfig:
        try:
            body = self.s3_client_wrapper.download_from_s3(s3_key=self.user_config_s3_key)
        except ClientError:
            raise UserConfigNotFoundError(s3_key=self.user_config_s3_key)

        return UserConfig.model_validate_json(json_data=body)

    def get_saved_calendar(self) -> Calendar:
        body = self.s3_client_wrapper.download_from_s3(s3_key=self.calendar_s3_key)
        return Calendar.from_ical(st=body)

    def save_calendar(self, calendar: Calendar) -> None:
        self.s3_client_wrapper.upload_to_s3(s3_key=self.calendar_s3_key, content=calendar.to_ical())
