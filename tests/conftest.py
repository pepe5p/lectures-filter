from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest
from icalendar import Event

TEST_DATETIME = datetime(2023, 11, 1, 0, 0, 0)


@pytest.fixture()
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@pytest.fixture()
def api_gw_event() -> dict:
    return {
        "headers": {},
        "body": "",
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/",
                "protocol": "HTTP/1.1",
                "sourceIp": "192.168.0.1/32",
                "userAgent": "agent",
            },
            "stage": "$default",
        },
        "rawPath": "/",
    }


def create_event(start: datetime, end: datetime) -> Event:
    event = Event()
    event.add("dtstart", start)
    event.add("dtend", end)
    return event


def create_past_event(start: datetime | None = None) -> Event:
    start = start or datetime(2020, 11, 1)
    assert start < TEST_DATETIME
    end = start + timedelta(hours=1, minutes=30)
    return create_event(start=start, end=end)


def create_future_event(start: datetime | None = None) -> Event:
    start = start or datetime(2023, 12, 1)
    assert start > TEST_DATETIME
    end = start + timedelta(hours=1, minutes=30)
    return create_event(start=start, end=end)
