from icalendar.cal import Event
from pydantic import BaseModel

from lectures_filter.common import NotEmptyStr


class Pattern(BaseModel):
    pattern: NotEmptyStr
    exceptions: list["Pattern"] = []

    def is_matching(self, string: str) -> bool:
        if not string.startswith(self.pattern):
            return False

        string_for_next_layer = string.replace(self.pattern, "")
        for exception in self.exceptions:
            if exception.is_matching(string=string_for_next_layer):
                return False

        return True


class FilteringConfig(BaseModel):
    match_by_default: bool = True
    exceptions: list[Pattern] = []

    def should_include_event(self, event: Event) -> bool:
        title = event["SUMMARY"]
        default_result = self.match_by_default

        for exception in self.exceptions:
            if exception.is_matching(string=title):
                return not default_result

        return default_result
