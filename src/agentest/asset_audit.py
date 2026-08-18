"""Read-only structural checks for Version testing assets."""

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from agentest.test_cases import scope_fingerprint_matches

_TEST_CASE_HEADER = re.compile(r"^###\s+(TC-[0-9]+)\b", re.MULTILINE)
_FIELD_NAMES = ("测试状态", "测试结果", "执行覆盖", "实际结果", "执行时间", "证据")
_ALLOWED_STATUS = {"未测试", "已测试"}
_ALLOWED_RESULTS = {"PASS", "FAIL", "BLOCKED", "NOT RUN"}
_ALLOWED_COVERAGE = {"完整", "部分", "未执行"}
_MEMORY_HEADINGS = ("验证 Version", "长期用途", "稳定事实")
_SENSITIVE_MEMORY_PATTERN = re.compile(
    r"(?i)(?:password|passwd|token|cookie|storage\s*state|密码|口令|验证码)"
)
_SCRIPT_METADATA_PATTERNS = {
    "test_case": re.compile(r"\bTC-[0-9]+\b"),
    "prerequisite": re.compile(r"(?i)(?:前置条件|prerequisite)"),
    "manual_login": re.compile(r"(?i)(?:手动登录|manual\s+login)"),
    "run_command": re.compile(r"(?i)(?:运行(?:方式|命令)|python(?:\.exe)?\s+-m\s+pytest)"),
}
_NO_EVIDENCE = {"", "无", "未执行", "未生成", "无证据"}
# 报告结果表按表头名称解析，不依赖固定列顺序；模板调整列时校验仍然有效。
_REPORT_COLUMNS = {
    "id": "测试用例",
    "script": "使用脚本",
    "coverage": "执行覆盖",
    "result": "本次结果",
}
_TEST_CASE_ID_PATTERN = re.compile(r"^TC-[0-9]+$")


@dataclass(frozen=True)
class AssetAuditIssue:
    """One actionable structural problem found in a Version asset."""

    code: str
    path: str
    message: str


def audit_system_assets(system_root: Path) -> list[AssetAuditIssue]:
    """Validate System-level Element Map YAML and Memory modules."""

    issues: list[AssetAuditIssue] = []
    if not system_root.is_dir():
        return [_issue("missing_system_root", system_root, system_root, "System 目录不存在")]

    element_map = system_root / "element-map"
    element_index = element_map / "index.yaml"
    if not element_index.is_file():
        issues.append(
            _issue(
                "missing_element_map_index",
                system_root,
                element_index,
                "缺少 element-map/index.yaml",
            )
        )
    else:
        _audit_element_map(system_root, element_map, element_index, issues)

    memory = system_root / "memory"
    memory_index = memory / "index.md"
    memory_modules = memory / "modules"
    if not memory_index.is_file():
        issues.append(
            _issue("missing_memory_index", system_root, memory_index, "缺少 memory/index.md")
        )
    if not memory_modules.is_dir():
        issues.append(
            _issue("missing_memory_modules", system_root, memory_modules, "缺少 memory/modules/")
        )
    else:
        module_files = sorted(memory_modules.glob("*.md"))
        if not module_files:
            issues.append(
                _issue(
                    "missing_memory_module",
                    system_root,
                    memory_modules,
                    "memory/modules/ 中没有模块",
                )
            )
        for module_file in module_files:
            content = module_file.read_text(encoding="utf-8")
            missing_headings = [
                heading
                for heading in _MEMORY_HEADINGS
                if not re.search(rf"^##\s+{re.escape(heading)}\s*$", content, re.MULTILINE)
            ]
            if missing_headings:
                issues.append(
                    _issue(
                        "incomplete_memory_module",
                        system_root,
                        module_file,
                        f"Memory 模块缺少章节：{', '.join(missing_headings)}",
                    )
                )
            if _SENSITIVE_MEMORY_PATTERN.search(content):
                issues.append(
                    _issue(
                        "sensitive_memory_content",
                        system_root,
                        module_file,
                        "Memory 模块包含凭据或验证码相关内容",
                    )
                )

    return issues


def _audit_element_map(
    system_root: Path,
    element_map: Path,
    index_path: Path,
    issues: list[AssetAuditIssue],
) -> None:
    try:
        raw: Any = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        issues.append(
            _issue(
                "invalid_element_map_index",
                system_root,
                index_path,
                "Element Map index 不是有效 YAML",
            )
        )
        return
    if (
        not isinstance(raw, dict)
        or raw.get("version") != 1
        or not isinstance(raw.get("modules"), list)
    ):
        issues.append(
            _issue(
                "invalid_element_map_index",
                system_root,
                index_path,
                "Element Map index 必须包含 version: 1 和 modules 列表",
            )
        )
        return

    for module in raw["modules"]:
        if not isinstance(module, dict) or not all(
            isinstance(module.get(field), str) and module[field].strip()
            for field in ("id", "file", "purpose")
        ):
            issues.append(
                _issue(
                    "invalid_element_map_index",
                    system_root,
                    index_path,
                    "Element Map index 的模块必须包含 id、file、purpose",
                )
            )
            continue
        module_path = element_map / module["file"]
        if not module_path.is_file():
            issues.append(
                _issue(
                    "missing_element_map_module",
                    system_root,
                    module_path,
                    f"Element Map 模块不存在：{module['file']}",
                )
            )
            continue
        _audit_element_map_module(system_root, module_path, issues)


def _audit_element_map_module(
    system_root: Path,
    module_path: Path,
    issues: list[AssetAuditIssue],
) -> None:
    try:
        raw: Any = yaml.safe_load(module_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        issues.append(
            _issue(
                "invalid_element_map_module",
                system_root,
                module_path,
                "Element Map 模块不是有效 YAML",
            )
        )
        return
    # 分级校验（item 11）：只强校验"定位与识别所需"的核心字段，省 token。
    # 强校验：模块 module_id/title；页面 id/url_pattern；元素 id/purpose 与 locator.primary。
    # 不校验（可选、按需填）：stability、verified_version、verified_viewport、viewport、
    # entry、fallback、action、expected_state、states、script_refs 等增强字段。
    if not isinstance(raw, dict) or any(not raw.get(field) for field in ("module_id", "title")):
        issues.append(
            _issue(
                "invalid_element_map_module",
                system_root,
                module_path,
                "Element Map 模块缺少 module_id 或 title",
            )
        )
        return
    if not isinstance(raw.get("pages"), list) or not raw["pages"]:
        issues.append(
            _issue(
                "invalid_element_map_module",
                system_root,
                module_path,
                "Element Map 模块 pages 不能为空",
            )
        )
        return
    for page in raw["pages"]:
        if not isinstance(page, dict) or any(
            not page.get(field) for field in ("id", "url_pattern")
        ):
            issues.append(
                _issue(
                    "incomplete_element_map_page",
                    system_root,
                    module_path,
                    "页面缺少 id 或 url_pattern",
                )
            )
            continue
        if not isinstance(page.get("elements"), list) or not page["elements"]:
            issues.append(
                _issue(
                    "incomplete_element_map_page",
                    system_root,
                    module_path,
                    "页面 elements 不能为空",
                )
            )
            continue
        for element in page["elements"]:
            if not isinstance(element, dict) or any(
                not element.get(field) for field in ("id", "purpose")
            ):
                issues.append(
                    _issue(
                        "incomplete_element_map_element",
                        system_root,
                        module_path,
                        "元素缺少 id 或 purpose",
                    )
                )
                continue
            locator = element["locator"]
            if not isinstance(locator, dict) or not isinstance(locator.get("primary"), dict):
                issues.append(
                    _issue(
                        "incomplete_element_map_element",
                        system_root,
                        module_path,
                        "元素缺少 locator.primary",
                    )
                )
                continue
            primary = locator["primary"]
            if not primary.get("type") or not primary.get("value"):
                issues.append(
                    _issue(
                        "incomplete_element_map_element",
                        system_root,
                        module_path,
                        "locator.primary 缺少 type 或 value",
                    )
                )


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

    test_cases_dir = version_root / "test-cases"
    test_cases_file = test_cases_dir / "test-cases.md"
    _check_file(version_root, test_cases_file, "missing_test_cases", issues)
    _check_file(
        version_root, test_cases_dir / "requirement.md", "missing_test_cases_contract", issues
    )

    test_case_content = (
        test_cases_file.read_text(encoding="utf-8") if test_cases_file.is_file() else ""
    )
    test_case_blocks = _parse_test_cases(test_case_content)
    test_case_ids = set(test_case_blocks)
    _check_duplicate_ids(version_root, test_case_content, issues)
    for test_case_id, block in test_case_blocks.items():
        _check_test_case_fields(version_root, test_case_id, block, issues)

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
        else:
            _check_test_scripts(version_root, scripts_dir, issues)

        report_dir = version_root / "report"
        report_file = report_dir / "report.md"
        _check_file(version_root, report_dir / "requirement.md", "missing_report_contract", issues)
        _check_file(version_root, report_file, "missing_report", issues)
        if report_file.is_file():
            report_content = report_file.read_text(encoding="utf-8")
            _check_report(version_root, report_content, test_case_ids, issues)

    if state_path is not None and state_path.is_file():
        _check_state(version_root, test_case_content, test_case_ids, state_path, issues)

    return issues


def _check_test_scripts(
    version_root: Path,
    scripts_dir: Path,
    issues: list[AssetAuditIssue],
) -> None:
    for script_path in sorted(scripts_dir.glob("*.py")):
        content = script_path.read_text(encoding="utf-8")
        missing = [
            name
            for name, pattern in _SCRIPT_METADATA_PATTERNS.items()
            if not pattern.search(content)
        ]
        if missing:
            issues.append(
                _issue(
                    "incomplete_test_script_metadata",
                    version_root,
                    script_path,
                    f"测试脚本缺少元数据：{', '.join(missing)}",
                )
            )


def _parse_test_cases(content: str) -> dict[str, str]:
    matches = list(_TEST_CASE_HEADER.finditer(content))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        blocks[match.group(1)] = content[match.start() : end]
    return blocks


def _check_test_case_fields(
    version_root: Path,
    test_case_id: str,
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
                    version_root / "test-cases" / "test-cases.md",
                    f"{test_case_id} 缺少 {field}",
                )
            )
    status = _field_value(block, "测试状态")
    result = _field_value(block, "测试结果")
    if status and status not in _ALLOWED_STATUS:
        issues.append(
            _issue(
                "invalid_test_status",
                version_root,
                version_root / "test-cases" / "test-cases.md",
                f"{test_case_id} 的测试状态无效",
            )
        )
    if result and result not in _ALLOWED_RESULTS:
        issues.append(
            _issue(
                "invalid_test_result",
                version_root,
                version_root / "test-cases" / "test-cases.md",
                f"{test_case_id} 的测试结果无效",
            )
        )
    coverage = _field_value(block, "执行覆盖")
    if coverage and coverage not in _ALLOWED_COVERAGE:
        issues.append(
            _issue(
                "invalid_execution_coverage",
                version_root,
                version_root / "test-cases" / "test-cases.md",
                f"{test_case_id} 的执行覆盖无效",
            )
        )
    elif coverage and (
        (result in {"PASS", "FAIL"} and (coverage != "完整" or status != "已测试"))
        or (coverage == "部分" and result != "BLOCKED")
        or (coverage == "未执行" and result not in {"BLOCKED", "NOT RUN"})
    ):
        issues.append(
            _issue(
                "inconsistent_execution_coverage",
                version_root,
                version_root / "test-cases" / "test-cases.md",
                f"{test_case_id} 的执行覆盖与测试状态/结果不一致",
            )
        )
    evidence = _field_value(block, "证据")
    if evidence and evidence not in _NO_EVIDENCE:
        evidence_path = _resolve_asset_path(version_root, evidence)
        if not evidence_path.is_file():
            issues.append(
                _issue(
                    "missing_evidence",
                    version_root,
                    version_root / "test-cases" / "test-cases.md",
                    f"{test_case_id} 引用的证据不存在",
                )
            )


def _check_report(
    version_root: Path,
    content: str,
    test_case_ids: set[str],
    issues: list[AssetAuditIssue],
) -> None:
    report_file = version_root / "report" / "report.md"
    rows = _parse_report_rows(content)
    report_ids = {test_case_id for test_case_id, _, _, _ in rows}
    if report_ids != test_case_ids:
        issues.append(
            _issue(
                "report_test_case_mismatch",
                version_root,
                report_file,
                "报告与测试用例文件的 测试用例 ID 集合不一致",
            )
        )

    summary = {
        key: _summary_value(content, label)
        for key, label in (
            ("total", "本次测试用例总数"),
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
        for _, _, _, result in rows:
            if result in actual_counts:
                actual_counts[result] += 1
        expected = {key: summary[key] for key in _ALLOWED_RESULTS}
        if summary["total"] != len(rows) or expected != actual_counts:
            issues.append(
                _issue(
                    "report_summary_mismatch", version_root, report_file, "报告结果汇总与明细不一致"
                )
            )

    for _test_case_id, script_reference, _coverage, _result in rows:
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
    # Re-read the Version test-case file so the report cannot silently change result semantics.
    test_cases_file = version_root / "test-cases" / "test-cases.md"
    test_case_blocks = _parse_test_cases(
        test_cases_file.read_text(encoding="utf-8") if test_cases_file.is_file() else ""
    )
    for test_case_id, _, coverage, result in rows:
        block = test_case_blocks.get(test_case_id, "")
        expected_coverage = _field_value(block, "执行覆盖")
        expected_result = _field_value(block, "测试结果")
        if expected_coverage and coverage != expected_coverage:
            issues.append(
                _issue(
                    "report_execution_coverage_mismatch",
                    version_root,
                    report_file,
                    f"{test_case_id} 的报告执行覆盖与测试用例文件不一致",
                )
            )
        if expected_result and result != expected_result:
            issues.append(
                _issue(
                    "report_result_mismatch",
                    version_root,
                    report_file,
                    f"{test_case_id} 的报告结果与测试用例文件不一致",
                )
            )

    for reference in re.findall(r"(?:evidence|test-scripts)/[^\s)`|]+", content):
        reference_path = _resolve_asset_path(version_root, reference)
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
    test_case_content: str,
    test_case_ids: set[str],
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

    completed = raw.get("completed_test_case_ids", [])
    unknown = set(completed) - test_case_ids if isinstance(completed, list) else set()
    if unknown:
        issues.append(
            _issue(
                "unknown_completed_test_case",
                version_root,
                state_path,
                "state.yaml 包含当前范围外的测试用例 ID",
            )
        )

    expected = raw.get("test_cases_fingerprint", "")
    if not expected:
        issues.append(
            _issue(
                "missing_fingerprint", version_root, state_path, "state.yaml 缺少测试用例范围指纹"
            )
        )
    elif not scope_fingerprint_matches(test_case_content, expected):
        issues.append(
            _issue(
                "fingerprint_mismatch", version_root, state_path, "测试用例范围指纹与当前文件不一致"
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
    ids = _TEST_CASE_HEADER.findall(content)
    if len(ids) != len(set(ids)):
        issues.append(
            _issue(
                "duplicate_test_case_id",
                version_root,
                version_root / "test-cases" / "test-cases.md",
                "测试用例 ID 重复",
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


def _resolve_asset_path(version_root: Path, reference: str) -> Path:
    """Resolve a POSIX-style relative asset reference under the version root.

    资产文件里的路径一律用正斜杠书写；这里用 ``PurePosixPath`` 解析后再交给当前平台的
    ``Path`` 拼接，Windows / macOS / Linux 行为一致，不再手动替换分隔符。
    """

    return version_root.joinpath(*PurePosixPath(reference.strip()).parts)


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _parse_report_rows(content: str) -> list[tuple[str, str, str, str]]:
    """Parse the report result table by header name (id, script, coverage, result)."""

    lines = content.splitlines()
    header_index: int | None = None
    columns: dict[str, int] = {}
    for index, line in enumerate(lines):
        if "|" not in line:
            continue
        cells = _split_table_row(line)
        if _REPORT_COLUMNS["id"] in cells and _REPORT_COLUMNS["result"] in cells:
            columns = {key: cells.index(label) for key, label in _REPORT_COLUMNS.items()}
            header_index = index
            break
    if header_index is None or len(columns) != len(_REPORT_COLUMNS):
        return []

    rows: list[tuple[str, str, str, str]] = []
    for line in lines[header_index + 1 :]:
        if "|" not in line:
            break
        cells = _split_table_row(line)
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells if cell):
            continue
        if len(cells) <= max(columns.values()):
            continue
        test_case_id = cells[columns["id"]].strip("`").strip()
        if not _TEST_CASE_ID_PATTERN.match(test_case_id):
            continue
        rows.append(
            (
                test_case_id,
                cells[columns["script"]],
                cells[columns["coverage"]],
                cells[columns["result"]],
            )
        )
    return rows


def _issue(code: str, version_root: Path, path: Path, message: str) -> AssetAuditIssue:
    try:
        relative_path = path.relative_to(version_root).as_posix()
    except ValueError:
        relative_path = str(path)
    return AssetAuditIssue(code=code, path=relative_path, message=message)


__all__ = ["AssetAuditIssue", "audit_system_assets", "audit_version_assets"]
