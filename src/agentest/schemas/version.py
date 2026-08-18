from pydantic import Field, field_serializer, field_validator, model_validator

from agentest.schemas.common import AssetModel, validate_asset_id
from agentest.schemas.system import TestEnvironmentOverride


class LinkedEnd(AssetModel):
    """多端联动的轻量引用：只指向另一个端（系统 + 可选版本），不复制其地址或环境。

    被引用端的测试地址仍以其自身 version.yaml 为唯一事实源；这里只登记"和谁联动"。
    """

    system_id: str
    # 省略 version_id 表示引用该系统当前范围内的版本。
    version_id: str = ""
    note: str = ""

    @field_validator("system_id")
    @classmethod
    def validate_system_id(cls, value: str) -> str:
        return validate_asset_id(value)

    @field_validator("version_id")
    @classmethod
    def validate_version_id(cls, value: str) -> str:
        return validate_asset_id(value) if value else value


class VersionConfig(AssetModel):
    id: str
    name: str = Field(min_length=1)
    # 测试地址的唯一事实源；运行时上下文只引用/缓存本字段，不另存真值。
    test_url: str = ""
    description: str = ""
    test_environment: TestEnvironmentOverride | None = None
    # 是否端联动；为真时须在 linked_ends 声明联动的端。
    linked: bool = False
    linked_ends: list[LinkedEnd] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return validate_asset_id(value)

    @model_validator(mode="after")
    def validate_linkage(self) -> "VersionConfig":
        if self.linked and not self.linked_ends:
            raise ValueError("linked=True 时必须至少声明一个 linked_ends")
        if not self.linked and self.linked_ends:
            raise ValueError("linked=False 时不应声明 linked_ends")
        keys = [(end.system_id, end.version_id) for end in self.linked_ends]
        if len(set(keys)) != len(keys):
            raise ValueError("linked_ends 不能重复引用同一端")
        return self

    @field_serializer("test_environment")
    def serialize_test_environment(
        self, value: TestEnvironmentOverride | None
    ) -> dict[str, object] | None:
        return value.model_dump(exclude_none=True) if value is not None else None


__all__ = ["LinkedEnd", "VersionConfig"]
