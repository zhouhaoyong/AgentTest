from pydantic import Field, field_validator

from agentest.schemas.common import AssetModel, validate_asset_id


class VersionConfig(AssetModel):
    id: str
    name: str = Field(min_length=1)
    test_url: str = ""
    description: str = ""

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return validate_asset_id(value)
