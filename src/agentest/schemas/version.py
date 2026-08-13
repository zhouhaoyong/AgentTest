from pydantic import Field, field_serializer, field_validator

from agentest.schemas.common import AssetModel, validate_asset_id
from agentest.schemas.system import TestEnvironmentOverride


class VersionConfig(AssetModel):
    id: str
    name: str = Field(min_length=1)
    test_url: str = ""
    description: str = ""
    test_environment: TestEnvironmentOverride | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return validate_asset_id(value)

    @field_serializer("test_environment")
    def serialize_test_environment(
        self, value: TestEnvironmentOverride | None
    ) -> dict[str, object] | None:
        return value.model_dump(exclude_none=True) if value is not None else None


__all__ = ["VersionConfig"]
