from typing import Annotated

from pydantic import Field

type NotEmptyStr = Annotated[str, Field(min_length=1, description="A non-empty string")]
