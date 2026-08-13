from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from agentest.schemas.common import AssetModel, validate_asset_id

SystemType = Literal["web", "h5", "app", "miniapp"]


class Viewport(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    width: int = Field(ge=1)
    height: int = Field(ge=1)


class ViewportOverride(AssetModel):
    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)


class TestEnvironmentOverride(AssetModel):
    viewport: ViewportOverride | None = None
    device_scale_factor: float | None = Field(default=None, gt=0)
    is_mobile: bool | None = None
    has_touch: bool | None = None
    locale: str | None = None
    timezone_id: str | None = None
    action_timeout_ms: int | None = Field(default=None, ge=0)
    navigation_timeout_ms: int | None = Field(default=None, ge=0)
    login: Literal["manual"] | None = None


class TestEnvironment(AssetModel):
    viewport: Viewport = Field(default_factory=lambda: Viewport(width=1280, height=720))
    device_scale_factor: float = Field(default=1, gt=0)
    is_mobile: bool = False
    has_touch: bool = False
    locale: str = "zh-CN"
    timezone_id: str = "Asia/Shanghai"
    action_timeout_ms: int = Field(default=5000, ge=0)
    navigation_timeout_ms: int = Field(default=30000, ge=0)
    login: Literal["manual"] = "manual"

    @classmethod
    def defaults_for_type(cls, system_type: SystemType) -> "TestEnvironment":
        if system_type in {"h5", "app", "miniapp"}:
            return cls(
                viewport=Viewport(width=390, height=844),
                device_scale_factor=3,
                is_mobile=True,
                has_touch=True,
            )
        return cls()

    def merged_with(self, override: TestEnvironmentOverride | None) -> "TestEnvironment":
        """Apply a sparse System or Version environment override."""
        if override is None:
            return self.model_copy(deep=True)

        data = self.model_dump()
        for field_name, value in override.model_dump(exclude_none=True).items():
            if field_name == "viewport":
                for viewport_field, viewport_value in value.items():
                    data["viewport"][viewport_field] = viewport_value
            else:
                data[field_name] = value
        return type(self).model_validate(data)


class SystemConfig(AssetModel):
    id: str
    name: str = Field(min_length=1)
    type: SystemType = "web"
    base_url: str = ""
    description: str = ""
    test_environment: TestEnvironment | None = None

    @model_validator(mode="before")
    @classmethod
    def resolve_test_environment(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = dict(value)
        system_type = data.get("type", "web")
        defaults = TestEnvironment.defaults_for_type(system_type)
        environment = data.get("test_environment")
        if environment is None:
            data["test_environment"] = defaults.model_dump()
            return data

        if isinstance(environment, TestEnvironmentOverride):
            override = environment
        elif isinstance(environment, TestEnvironment):
            override = TestEnvironmentOverride.model_validate(environment.model_dump())
        else:
            override = TestEnvironmentOverride.model_validate(environment)
        data["test_environment"] = defaults.merged_with(override).model_dump()
        return data

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return validate_asset_id(value)

    @model_validator(mode="after")
    def validate_type_suffix_and_environment(self) -> "SystemConfig":
        expected_suffix = f"-{self.type}"
        if not self.id.endswith(expected_suffix):
            raise ValueError(f"System ID must end with the system type suffix: {expected_suffix}")
        return self


__all__ = [
    "SystemConfig",
    "SystemType",
    "TestEnvironment",
    "TestEnvironmentOverride",
    "Viewport",
    "ViewportOverride",
]
