"""Read-only structural checks for Version testing assets."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agentest.test_points import scope_fingerprint_matches

_TEST_POINT_HEADER = re.compile(r"^###\s+(TP-[0-9]+)\b", re.MULTILINE)
_FIELD_NAMES = ("测试状态", "测试结果", "实际说明", "执行时间", "证据")
_ALLOWED_STATUS = {"未测试", "已测试"}
_ALLOWED_RESULTS = {"PASS", "FAIL", "BLOCKED", "NOT RUN"}
_NO_EVIDENCE = {"", "无", "未执行", "未生成", "无证据"}
_REPORT_ROW = re.compile(
    r"^\|\s*(TP-[0-9]+)\s*\|[^|]*\|\s*([^|]*)\|\s*(PASS|FAIL|BLOCKED|NOT RUN)\s*\|.*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class AssetAuditIssue:
    """One actionable structural problem found in a Version asset."""

    code: str
    path: str
    message: str


def audit_version_assets(
    version_root: Path,
    *,
    state_path: Path | None = None,
    require_execution_assets: bool = False,
) -> list[AssetAuditIssue]:
    """Return structural issues without modifying the supplied asset directories."""

    issues: list[AssetAuditIssue] = []
    if not version_root.is_dir():
        return [_issue("missing_version_root", version_root, version_root, "Version 目录不存在")]

    _check_file(version_root, version_root / "version.yaml", "missing_version_file", issues)
    _check_file(version_root, version_root / "requirement.md", "missing_version_contract", issues)

    requirements = version_root / "requirements"
    if requirements.is_dir():
        _check_file(
            version_root, requirements / "requirement.md", "missing_requirements_contract", issues
        )
        _check_file(version_root, requirements / "source.md", "missing_requirement_source", issues)
        structured = [
            path
            for path in requirements.glob("*.md")
            if path.name not in {"requirement.md", "source.md"}
        ]
        if not structured:
            issues.append(
                _issue(
                    "missing_structured_requirement",
                    version_root,
                    requirements,
                    "requirements/ 中没有结构化需求文档",
                )
            )
    else:
        issues.append(
            _issue("missing_requirements", version_root, requirements, "缺少 requirements/")
        )

    test_points_dir = version_root / "test-points"
    test_points_file = test_points_dir / "test-points.md"
    _check_file(version_root, test_points_file, "missing_test_points", issues)
    _check_file(
        version_root, test_points_dir / "requirement.md", "missing_test_points_contract", issues
    )

    test_point_content = (
        test_points_file.read_text(encoding="utf-8") if test_points_file.is_file() else ""
    )
    test_point_blocks = _parse_test_points(test_point_content)
    test_point_ids = set(test_point_blocks)
    _check_duplicate_ids(version_root, test_point_content, issues)
    for test_point_id, block in test_point_blocks.items():
        _check_test_point_fields(version_root, test_point_id, block, issues)

    if require_execution_assets:
        scripts_dir = version_root / "test-scripts"
        _check_file(
            version_root, scripts_dir / "requirement.md", "missing_test_scripts_contract", issues
        )
        if not scripts_dir.is_dir():
            issues.append(
                _issue(
                    "missing_test_scripts",
                    version_root,
                    scripts_dir,
                    "正式测试后缺少 test-scripts/",
                )
            )
        elif not any(scripts_dir.glob("*.py")):
            issues.append(
                _issue(
                    "missing_test_script_file",
                    version_root,
                    scripts_dir,
                    "test-scripts/ 中没有 Python 测试脚本",
                )
            )

        report_dir = version_root / "report"
        report_file = report_dir / "report.md"
        _check_file(version_root, report_dir / "requirement.md", "missing_report_contract", issues)
        _check_file(version_root, report_file, "missing_report", issues)
        if report_file.is_file():
            report_content = report_file.read_text(encoding="utf-8")
            _check_report(version_root, report_content, test_point_ids, issues)

    if state_path is not None and state_path.is_file():
        _check_state(version_root, test_point_content, test_point_ids, state_path, issues)

    return issues


def _parse_test_points(content: str) -> dict[str, str]:
    matches = list(_TEST_POINT_HEADER.finditer(content))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        blocks[match.group(1)] = content[match.start() : end]
    return blocks


def _check_test_point_fields(
    version_root: Path,
    test_point_id: str,
    block: str,
    issues: list[AssetAuditIssue],
) -> None:
    for field in _FIELD_NAMES:
        match = re.search(
            rf"^\s*(?:[-*]\s*)?{re.escape(field)}\s*[:：]\s*(.*?)\s*$", block, re.MULTILINE
        )
        if match is None:
            issues.append(
                _issue(
                    "missing_execution_field",
                    version_root,
                    version_root / "test-points" / "test-points.md",
                    f"{test_point_id} 缺少 {field}",
                )
            )
    status = _field_value(block, "测试状态")
    result = _field_value(block, "测试结果")
    if status and status not in _ALLOWED_STATUS:
        issues.append(
            _issue(
                "invalid_test_status",
                version_root,
                version_root / "test-points" / "test-points.md",
                f"{test_point_id} 的测试状态无效",
            )
        )
    if result and result not in _ALLOWED_RESULTS:
        issues.append(
            _issue(
                "invalid_test_result",
                version_root,
                version_root / "test-points" / "test-points.md",
                f"{test_point_id} 的测试结果无效",
            )
        )
    evidence = _field_value(block, "证据")
    if evidence and evidence not in _NO_EVIDENCE:
        evidence_path = version_root / evidence.replace("/", "\\")
        if not evidence_path.is_file():
            issues.append(
                _issue(
                    "missing_evidence",
                    version_root,
                    version_root / "test-points" / "test-points.md",
                    f"{test_point_id} 引用的证据不存在",
                )
            )


def _check_report(
    version_root: Path,
    content: str,
    test_point_ids: set[str],
    issues: list[AssetAuditIssue],
) -> None:
    report_file = version_root / "report" / "report.md"
    rows = _REPORT_ROW.findall(content)
    report_ids = {test_point_id for test_point_id, _, _ in rows}
    if report_ids != test_point_ids:
        issues.append(
            _issue(
                "report_test_point_mismatch",
                version_root,
                report_file,
                "报告与测试点文件的 TP 集合不一致",
            )
        )

    summary = {
        key: _summary_value(content, label)
        for key, label in (
            ("total", "本次测试点总数"),
            ("PASS", "PASS"),
            ("FAIL", "FAIL"),
            ("BLOCKED", "BLOCKED"),
            ("NOT RUN", "NOT RUN"),
        )
    }
    if any(value is None for value in summary.values()):
        issues.append(
            _issue("missing_report_summary", version_root, report_file, "报告缺少完整结果汇总")
        )
    else:
        actual_counts = {result: 0 for result in _ALLOWED_RESULTS}
        for _, _, result in rows:
            actual_counts[result] += 1
        expected = {key: summary[key] for key in _ALLOWED_RESULTS}
        if summary["total"] != len(rows) or expected != actual_counts:
            issues.append(
                _issue(
                    "report_summary_mismatch", version_root, report_file, "报告结果汇总与明细不一致"
                )
            )

    for _, script_reference, _ in rows:
        script_reference = script_reference.strip().strip("`")
        if script_reference and script_reference not in {"无", "-"}:
            script_path = version_root / "test-scripts" / Path(script_reference).name
            if not script_path.is_file():
                issues.append(
                    _issue(
                        "missing_referenced_asset",
                        version_root,
                        report_file,
                        f"报告引用的脚本不存在：{script_reference}",
                    )
                )

    for reference in re.findall(r"(?:evidence|test-scripts)/[^\s)`|]+", content):
        reference_path = version_root / reference.replace("/", "\\")
        if not reference_path.is_file():
            issues.append(
                _issue(
                    "missing_referenced_asset",
                    version_root,
                    report_file,
                    f"报告引用的资产不存在：{reference}",
                )
            )


def _check_state(
    version_root: Path,
    test_point_content: str,
    test_point_ids: set[str],
    state_path: Path,
    issues: list[AssetAuditIssue],
) -> None:
    try:
        raw: Any = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        issues.append(
            _issue("invalid_state_yaml", version_root, state_path, "state.yaml 不是有效 YAML")
        )
        return
    if not isinstance(raw, dict):
        issues.append(
            _issue("invalid_state_shape", version_root, state_path, "state.yaml 顶层必须是对象")
        )
        return

    completed = raw.get("completed_test_point_ids", [])
    unknown = set(completed) - test_point_ids if isinstance(completed, list) else set()
    if unknown:
        issues.append(
            _issue(
                "unknown_completed_test_point",
                version_root,
                state_path,
                "state.yaml 包含当前范围外的测试点 ID",
            )
        )

    expected = raw.get("test_points_fingerprint", "")
    if not expected:
        issues.append(
            _issue("missing_fingerprint", version_root, state_path, "state.yaml 缺少测试点范围指纹")
        )
    elif not scope_fingerprint_matches(test_point_content, expected):
        issues.append(
            _issue(
                "fingerprint_mismatch", version_root, state_path, "测试点范围指纹与当前文件不一致"
            )
        )


def _field_value(block: str, field: str) -> str:
    match = re.search(
        rf"^\s*(?:[-*]\s*)?{re.escape(field)}\s*[:：]\s*(.*?)\s*$", block, re.MULTILINE
    )
    return match.group(1).strip() if match else ""


def _summary_value(content: str, label: str) -> int | None:
    match = re.search(rf"^\s*-\s*{re.escape(label)}\s*[:：]\s*(\d+)\s*$", content, re.MULTILINE)
    return int(match.group(1)) if match else None


def _check_duplicate_ids(version_root: Path, content: str, issues: list[AssetAuditIssue]) -> None:
    ids = _TEST_POINT_HEADER.findall(content)
    if len(ids) != len(set(ids)):
        issues.append(
            _issue(
                "duplicate_test_point_id",
                version_root,
                version_root / "test-points" / "test-points.md",
                "测试点 ID 重复",
            )
        )


def _check_file(
    version_root: Path,
    path: Path,
    code: str,
    issues: list[AssetAuditIssue],
) -> None:
    if not path.is_file():
        issues.append(
            _issue(code, version_root, path, f"缺少 {path.relative_to(version_root).as_posix()}")
        )


def _issue(code: str, version_root: Path, path: Path, message: str) -> AssetAuditIssue:
    try:
        relative_path = path.relative_to(version_root).as_posix()
    except ValueError:
        relative_path = str(path)
    return AssetAuditIssue(code=code, path=relative_path, message=message)


__all__ = ["AssetAuditIssue", "audit_version_assets"]
