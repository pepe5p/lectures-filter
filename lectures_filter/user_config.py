from pydantic import BaseModel, Field

from lectures_filter.common import NotEmptyStr
from lectures_filter.filtering import FilteringConfig


class USOSUserConfig(BaseModel):
    user_id: NotEmptyStr = Field(description="The user's ID in the USOS system, used to fetch their calendar.")
    calendar_key: NotEmptyStr = Field(description="The user's key in the USOS system, used to fetch their calendar.")


class UserConfig(BaseModel):
    usos: USOSUserConfig
    filtering: FilteringConfig = FilteringConfig()
