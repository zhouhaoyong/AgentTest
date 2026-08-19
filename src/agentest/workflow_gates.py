"""Read-only workflow gates for confirmation, test start and report delivery."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeVar

from pydantic import BaseModel

from agentest.asset_audit import AssetAuditIssue, audit_version_assets
from agentest.schemas.common import load_yaml_model
from agentest.schemas.project import ProjectConfig
from agentest.schemas.system import SystemConfig
from agentest.schemas.version import VersionConfig
from agentest.schemas.workspace import WorkspaceContext

WorkflowGateStage = Literal[
    "test_case_confirmation",
    "formal_test_start",
    "report_delivery",
]

ModelT = TypeVar("ModelT", bound=BaseModel)


def audit_workflow_gate(
    workspace_root: Path,
    stage: WorkflowGateStage,
) -> list[AssetAuditIssue]:
    """Return every current workflow blocker without changing workspace assets."""

    root = workspace_root.resolve()
    issues: list[AssetAuditIssue] = []
    if stage not in {"test_case_confirmation", "formal_test_start", "report_delivery"}:
        return [
            _issue(
                root,
                root,
                "invalid_workflow_gate_stage",
                "工作流闸门阶段无效",
            )
        ]

    context_path = root / ".agentest" / "context.yaml"
    context = _load_model(
        root,
        context_path,
        WorkspaceContext,
        "missing_workspace_context",
        "invalid_workspace_context",
        issues,
    )
    if context is None:
        return _deduplicate(issues)

    project_root = root / "projects" / context.project_id
    project = _load_model(
        root,
        project_root / "project.yaml",
        ProjectConfig,
        "missing_project_config",
        "invalid_project_config",
        issues,
    )
    system_root = project_root / "systems" / context.system_id
    system = _load_model(
        root,
        system_root / "system.yaml",
        SystemConfig,
        "missing_system_config",
        "invalid_system_config",
        issues,
    )
    version_root = system_root / "versions" / context.version_id
    version = _load_model(
        root,
        version_root / "version.yaml",
        VersionConfig,
        "missing_version_config",
        "invalid_version_config",
        issues,
    )
    if project is None or system is None or version is None:
        return _deduplicate(issues)

    _check_config_ids(
        root,
        project_root,
        system_root,
        version_root,
        context,
        project,
        system,
        version,
        issues,
    )

    state_path = root / ".agentest" / "state.yaml"
    if not state_path.is_file():
        issues.append(
            _issue(
                root,
                state_path,
                "missing_workspace_state",
                "缺少 .agentest/state.yaml，无法确认当前测试范围和执行进度",
            )
        )
    issues.extend(
        audit_version_assets(
            version_root,
            state_path=state_path if state_path.is_file() else None,
            require_execution_assets=stage == "report_delivery",
        )
    )

    if not version.test_url:
        issues.append(
            _issue(
                root,
                version_root / "version.yaml",
                "missing_current_test_url",
                "当前 Version 未填写测试地址，不能使用 System 的历史地址代替",
            )
        )

    if stage == "formal_test_start":
        _check_linked_ends(root, project_root, context, version, issues)

    return _deduplicate(issues)


def _load_model(
    workspace_root: Path,
    path: Path,
    model_type: type[ModelT],
    missing_code: str,
    invalid_code: str,
    issues: list[AssetAuditIssue],
) -> ModelT | None:
    if not path.is_file():
        issues.append(_issue(workspace_root, path, missing_code, f"缺少配置文件：{path.name}"))
        return None
    try:
        return load_yaml_model(path, model_type)
    except Exception:
        issues.append(_issue(workspace_root, path, invalid_code, f"配置文件无效：{path.name}"))
        return None


def _check_config_ids(
    workspace_root: Path,
    project_root: Path,
    system_root: Path,
    version_root: Path,
    context: WorkspaceContext,
    project: ProjectConfig,
    system: SystemConfig,
    version: VersionConfig,
    issues: list[AssetAuditIssue],
) -> None:
    expected = (
        (project.id, context.project_id, project_root / "project.yaml", "project"),
        (system.id, context.system_id, system_root / "system.yaml", "system"),
        (version.id, context.version_id, version_root / "version.yaml", "version"),
    )
    for configured_id, context_id, path, label in expected:
        if configured_id != context_id:
            issues.append(
                _issue(
                    workspace_root,
                    path,
                    "context_config_id_mismatch",
                    f"当前上下文与 {label} 配置的 ID 不一致",
                )
            )


def _check_linked_ends(
    workspace_root: Path,
    project_root: Path,
    context: WorkspaceContext,
    version: VersionConfig,
    issues: list[AssetAuditIssue],
) -> None:
    for linked_end in version.linked_ends:
        if not linked_end.version_id:
            issues.append(
                _issue(
                    workspace_root,
                    project_root / "systems" / linked_end.system_id,
                    "missing_linked_version",
                    f"联动端 {linked_end.system_id} 未明确 Version，不能猜测当前范围",
                )
            )
            continue
        if (
            linked_end.system_id == context.system_id
            and linked_end.version_id == context.version_id
        ):
            issues.append(
                _issue(
                    workspace_root,
                    project_root
                    / "systems"
                    / linked_end.system_id
                    / "versions"
                    / linked_end.version_id,
                    "self_linked_end",
                    "联动端不能引用当前 System 和 Version 自身",
                )
            )
            continue
        linked_system_root = project_root / "systems" / linked_end.system_id
        if not linked_system_root.is_dir():
            issues.append(
                _issue(
                    workspace_root,
                    linked_system_root,
                    "missing_linked_system",
                    f"联动 System 不存在：{linked_end.system_id}",
                )
            )
            continue
        linked_system = _load_model(
            workspace_root,
            linked_system_root / "system.yaml",
            SystemConfig,
            "missing_linked_system_config",
            "invalid_linked_system_config",
            issues,
        )
        if linked_system is None:
            continue
        if linked_system.id != linked_end.system_id:
            issues.append(
                _issue(
                    workspace_root,
                    linked_system_root / "system.yaml",
                    "linked_system_config_id_mismatch",
                    f"联动 System 配置 ID 与引用不一致：{linked_end.system_id}",
                )
            )
            continue
        linked_version_root = linked_system_root / "versions" / linked_end.version_id
        if not linked_version_root.is_dir():
            issues.append(
                _issue(
                    workspace_root,
                    linked_version_root,
                    "missing_linked_version",
                    f"联动 Version 不存在：{linked_end.system_id}/{linked_end.version_id}",
                )
            )
            continue
        linked_version = _load_model(
            workspace_root,
            linked_version_root / "version.yaml",
            VersionConfig,
            "missing_linked_version_config",
            "invalid_linked_version_config",
            issues,
        )
        if linked_version is not None and not linked_version.test_url:
            issues.append(
                _issue(
                    workspace_root,
                    linked_version_root / "version.yaml",
                    "missing_linked_test_url",
                    f"联动端 {linked_end.system_id}/{linked_end.version_id} 未填写测试地址",
                )
            )


def _issue(workspace_root: Path, path: Path, code: str, message: str) -> AssetAuditIssue:
    try:
        display_path = path.relative_to(workspace_root).as_posix()
    except ValueError:
        display_path = path.as_posix()
    return AssetAuditIssue(code=code, path=display_path, message=message)


def _deduplicate(issues: list[AssetAuditIssue]) -> list[AssetAuditIssue]:
    unique: list[AssetAuditIssue] = []
    seen: set[tuple[str, str, str]] = set()
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    return unique


__all__ = ["WorkflowGateStage", "audit_workflow_gate"]
