from typing import Literal

from pydantic import Field, field_validator

from agentest.schemas.common import AssetModel, validate_asset_id

WorkspaceSystemType = Literal["", "web", "h5", "app", "miniapp"]
WorkflowPhase = Literal[
    "intake",
    "context",
    "requirements",
    "exploration",
    "test-cases",
    "testing",
    "reporting",
    "regression",
]


class WorkspaceContext(AssetModel):
    # 一次工作只针对用户确认的 项目 / 系统 / 版本；测试地址以 version.yaml 为唯一事实源。
    project_id: str
    system_id: str
    system_type: WorkspaceSystemType = ""
    version_id: str = ""

    @field_validator("project_id", "system_id")
    @classmethod
    def validate_required_id(cls, value: str) -> str:
        return validate_asset_id(value)

    @field_validator("version_id")
    @classmethod
    def validate_optional_id(cls, value: str) -> str:
        return validate_asset_id(value) if value else value


class WorkspaceState(AssetModel):
    phase: WorkflowPhase = "intake"
    context_confirmed: bool = False
    last_action: str = ""
    pending_questions: list[str] = Field(default_factory=list)
    # 已完成的测试用例 ID（增量结果 / 断点续跑用）。仅记录进度，不代表授权仍有效。
    completed_test_case_ids: list[str] = Field(default_factory=list)
    # 上次批准时测试用例范围的指纹；不包含执行状态、结果、说明、时间和证据。
    test_cases_fingerprint: str = ""


__all__ = [
    "WorkspaceContext",
    "WorkspaceState",
    "WorkflowPhase",
    "WorkspaceSystemType",
]
