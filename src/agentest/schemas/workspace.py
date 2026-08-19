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
# 单条用例的执行判定（区分"执行过 vs 通过 vs 阻塞"）。
# executed 语义仍由 completed_test_case_ids 承担（"已出结论"），此处只记终态结果，
# 避免与进度字段语义打架；not_run 表示登记在案但尚未跑。
TestCaseOutcome = Literal["passed", "failed", "blocked", "not_run"]


class WorkspaceContext(AssetModel):
    # 一次工作只针对用户确认的 项目 / 系统 / 版本；测试地址以 version.yaml 为唯一事实源。
    project_id: str
    system_id: str
    system_type: WorkspaceSystemType = ""
    version_id: str

    @field_validator("project_id", "system_id", "version_id")
    @classmethod
    def validate_required_id(cls, value: str) -> str:
        return validate_asset_id(value)


class WorkspaceState(AssetModel):
    phase: WorkflowPhase = "intake"
    context_confirmed: bool = False
    last_action: str = ""
    pending_questions: list[str] = Field(default_factory=list)
    # 已完成的测试用例 ID（增量结果 / 断点续跑用）。仅记录进度，不代表授权仍有效。
    completed_test_case_ids: list[str] = Field(default_factory=list)
    # 上次批准时测试用例范围的指纹；不包含执行状态、结果、说明、时间和证据。
    test_cases_fingerprint: str = ""
    # 测试尚未开始时可为空；只要 completed_test_case_ids 有内容，就必须逐用例记录结果。
    test_case_results: dict[str, TestCaseOutcome] = Field(default_factory=dict)


__all__ = [
    "WorkspaceContext",
    "WorkspaceState",
    "WorkflowPhase",
    "WorkspaceSystemType",
    "TestCaseOutcome",
]
