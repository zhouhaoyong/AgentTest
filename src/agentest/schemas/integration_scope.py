from pydantic import Field, field_validator, model_validator

from agentest.schemas.common import AssetModel, validate_asset_id


class IntegrationScopeMember(AssetModel):
    order: int = Field(ge=1)
    system_id: str
    version_id: str
    test_url: str = ""

    @field_validator("system_id", "version_id")
    @classmethod
    def validate_asset_reference_id(cls, value: str) -> str:
        return validate_asset_id(value)


class IntegrationScopeConfig(AssetModel):
    id: str
    name: str = Field(min_length=1)
    description: str = ""
    systems: list[IntegrationScopeMember] = Field(min_length=2)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return validate_asset_id(value)

    @model_validator(mode="after")
    def validate_unique_member_order(self) -> "IntegrationScopeConfig":
        orders = [member.order for member in self.systems]
        if len(set(orders)) != len(orders):
            raise ValueError("systems must use unique order values")
        return self


__all__ = ["IntegrationScopeConfig", "IntegrationScopeMember"]
