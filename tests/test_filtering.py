import pytest
from icalendar.cal import Event

from lectures_filter.filtering import FilteringConfig

TEST_FILTERING_CONFIG_1 = FilteringConfig.model_validate(
    {
        "match_by_default": False,
        "exceptions": [
            {"pattern": "A", "exceptions": []},
        ],
    },
)
TEST_FILTERING_CONFIG_2 = FilteringConfig.model_validate(
    {
        "match_by_default": True,
        "exceptions": [
            {
                "pattern": "W",
                "exceptions": [
                    {"pattern": " - Knowledge Management in Critical Infrastructure", "exceptions": []},
                ],
            },
            {"pattern": "CWP - Development Workshop", "exceptions": []},
        ],
    }
)


@pytest.mark.parametrize(
    "config, event, expected_result",
    [
        (
            TEST_FILTERING_CONFIG_1,
            Event(SUMMARY="A"),
            True,
        ),
        (
            TEST_FILTERING_CONFIG_1,
            Event(SUMMARY="Ale fajny event"),
            True,
        ),
        (
            TEST_FILTERING_CONFIG_1,
            Event(SUMMARY="B"),
            False,
        ),
        (
            TEST_FILTERING_CONFIG_2,
            Event(SUMMARY="W - Knowledge Management in Critical Infrastructure"),
            True,
        ),
        (
            TEST_FILTERING_CONFIG_2,
            Event(SUMMARY="W - Model Checking"),
            False,
        ),
        (
            TEST_FILTERING_CONFIG_2,
            Event(SUMMARY="CWP - Development Workshop"),
            False,
        ),
        (
            TEST_FILTERING_CONFIG_2,
            Event(SUMMARY="Other Event"),
            True,
        ),
    ],
)
def test_filtering_config_should_include_event(
    config: FilteringConfig,
    event: Event,
    expected_result: bool,
) -> None:
    assert config.should_include_event(event=event) is expected_result
