from pydantic import Field, field_validator

from agentest.schemas.common import AssetModel, validate_asset_id


class SystemConfig(AssetModel):
    id: str
    name: str = Field(min_length=1)
    type: str = "web"
    base_url: str = ""
    description: str = ""

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return validate_asset_id(value)
