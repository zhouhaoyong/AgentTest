from pydantic import Field, field_validator

from agentest.schemas.common import AssetModel, load_yaml_model, validate_asset_id


class ProjectConfig(AssetModel):
    id: str
    name: str = Field(min_length=1)
    description: str = ""

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return validate_asset_id(value)


__all__ = ["ProjectConfig", "load_yaml_model"]
