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
# 定位质量校验（W1-3）：高精度识别占位 / 弱定位，避免误伤合法的中文 role/text 定位。
_CJK_PATTERN = re.compile(r"[一-鿿]")
# 模糊属性匹配：[class*=、[attr^=、[data-x$= 等；不误伤 [aria-label=（无 *^$~ 通配）。
_FUZZY_ATTR_PATTERN = re.compile(r"\[[a-zA-Z_:-]+[*^$~]=")
# text 定位夹带操作性说明括号（如 "订单标题（点击卡片标题区）"），疑为占位而非真实文本。
_TEXT_INSTRUCTION_PATTERN = re.compile(
    r"[（(][^）)]*(?:点击|选择|取|进入|见图|如下|或)[^）)]*[）)]"
)
# css / xpath / testid 定位串应为选择器而非中文自然语言；role / label / text 允许中文。
_SELECTOR_LOCATOR_TYPES = {"css", "xpath", "testid"}
# 合法定位类型（与 template-element-map-module.yaml 的 type 取值对齐）。
_ALLOWED_LOCATOR_TYPES = {"testid", "role", "label", "css", "text", "xpath"}


def _read_text(path: Path) -> str:
    """读取文本，容忍 BOM 与非 UTF-8（Windows 常见 GBK）编码，避免因编码直接崩溃。

    先按 ``utf-8-sig``（同时吃掉 BOM）解码，失败回退 ``gbk``；两者都不行时用替换字符兜底，
    保证校验流程不因单个文件编码异常而整体中断。
    """

    data = path.read_bytes()
    for encoding in ("utf-8-sig", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


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
            content = _read_text(module_file)
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
        raw: Any = yaml.safe_load(_read_text(index_path))
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

    _audit_element_map_global(system_root, index_path, raw.get("global"), issues)

    for module in raw["modules"]:
        if not isinstance(module, dict) or not all(
            isinstance(module.get(field), str) and module[field].strip()
            for field in ("id", "file")
        ):
            issues.append(
                _issue(
                    "invalid_element_map_index",
                    system_root,
                    index_path,
                    "Element Map index 的模块必须包含 id、file",
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
        raw: Any = yaml.safe_load(_read_text(module_path))
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
    # 验证视口必填：响应式布局随视口变化，缺了它结论无法复现（#5 统一为必填）。
    if not (isinstance(raw.get("viewport"), str) and raw["viewport"].strip()):
        issues.append(
            _issue(
                "missing_element_map_viewport",
                system_root,
                module_path,
                "Element Map 模块缺少 viewport（验证视口，必填）",
            )
        )
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
    element_ids: list[str] = []
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
            element_ids.append(element["id"])
            # unverified 存根（"观察到、未点击验证"）只登记不强校验定位，复用前需补验。
            if element.get("unverified"):
                continue
            locator = element.get("locator")
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
                continue
            _check_locator_quality(system_root, module_path, primary, issues)

    duplicate_ids = sorted({eid for eid in element_ids if element_ids.count(eid) > 1})
    if duplicate_ids:
        issues.append(
            _issue(
                "duplicate_element_id",
                system_root,
                module_path,
                f"Element Map 模块内元素 id 重复：{', '.join(duplicate_ids)}",
            )
        )


def _audit_element_map_global(
    system_root: Path,
    index_path: Path,
    raw_global: Any,
    issues: list[AssetAuditIssue],
) -> None:
    """校验索引可选的 global 段（全局导航壳 / 登录入口 / 公共弹窗组件）。"""

    if raw_global is None:
        return
    if not isinstance(raw_global, list):
        issues.append(
            _issue(
                "invalid_element_map_index",
                system_root,
                index_path,
                "Element Map index 的 global 必须是列表",
            )
        )
        return
    for element in raw_global:
        if not isinstance(element, dict) or not element.get("id"):
            issues.append(
                _issue(
                    "invalid_element_map_index",
                    system_root,
                    index_path,
                    "global 元素必须包含 id",
                )
            )
            continue
        locator = element.get("locator")
        if isinstance(locator, dict) and isinstance(locator.get("primary"), dict):
            _check_locator_quality(system_root, index_path, locator["primary"], issues)


def _check_locator_quality(
    system_root: Path,
    path: Path,
    primary: dict[str, Any],
    issues: list[AssetAuditIssue],
) -> None:
    """标记疑似占位 / 数据派生 / 模糊匹配的弱定位（W1-3）。高精度，避免误伤合法中文 role/text。"""

    value = primary.get("value")
    if not isinstance(value, str) or not value.strip():
        return
    loc_type = primary.get("type")
    if loc_type not in _ALLOWED_LOCATOR_TYPES:
        issues.append(
            _issue(
                "invalid_locator_type",
                system_root,
                path,
                f"定位类型 {loc_type!r} 非法，应为 testid/role/label/css/text/xpath 之一",
            )
        )
    if _FUZZY_ATTR_PATTERN.search(value):
        issues.append(
            _issue(
                "weak_element_locator",
                system_root,
                path,
                f"定位使用模糊属性匹配（如 [class*=]），应改用稳定属性或移入 fallback：{value}",
            )
        )
    if loc_type in _SELECTOR_LOCATOR_TYPES and _CJK_PATTERN.search(value):
        issues.append(
            _issue(
                "weak_element_locator",
                system_root,
                path,
                f"{loc_type} 定位串含中文，疑为占位 / 自然语言而非选择器：{value}",
            )
        )
    if loc_type == "text" and _TEXT_INSTRUCTION_PATTERN.search(value):
        issues.append(
            _issue(
                "weak_element_locator",
                system_root,
                path,
                f"text 定位含操作性说明括号，疑为占位而非真实可见文本：{value}",
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

    test_case_content = _read_text(test_cases_file) if test_cases_file.is_file() else ""
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
            report_content = _read_text(report_file)
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
        content = _read_text(script_path)
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
    rows, missing_columns = _parse_report_rows(content)
    if missing_columns:
        labels = "、".join(_REPORT_COLUMNS[key] for key in sorted(missing_columns))
        issues.append(
            _issue(
                "incomplete_report_table",
                version_root,
                report_file,
                f"报告结果表缺少列：{labels}",
            )
        )
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
        _read_text(test_cases_file) if test_cases_file.is_file() else ""
    )
    for test_case_id, _, coverage, result in rows:
        block = test_case_blocks.get(test_case_id, "")
        expected_coverage = _field_value(block, "执行覆盖")
        expected_result = _field_value(block, "测试结果")
        coverage_known = "coverage" not in missing_columns
        if coverage_known and expected_coverage and coverage != expected_coverage:
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

    # 允许文件名含空格：只在 Markdown 链接右括号 / 表格竖线 / 反引号 / 换行处截断，
    # 不再遇到空格就切断，避免把 "evidence/我的 证据.png" 误判成坏路径。
    for reference in re.findall(r"(?:evidence|test-scripts)/[^)`|\n]+", content):
        reference_path = _resolve_asset_path(version_root, reference.strip())
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
        raw: Any = yaml.safe_load(_read_text(state_path)) or {}
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

    _check_test_case_results(version_root, test_case_ids, completed, raw, state_path, issues)


# 逐用例结果的终态取值（与 schemas.workspace.TestCaseOutcome 对齐）。
_TERMINAL_OUTCOMES = {"passed", "failed", "blocked"}
_VALID_OUTCOMES = _TERMINAL_OUTCOMES | {"not_run"}


def _check_test_case_results(
    version_root: Path,
    test_case_ids: set[str],
    completed: Any,
    raw: dict[str, Any],
    state_path: Path,
    issues: list[AssetAuditIssue],
) -> None:
    """可选字段 test_case_results 的一致性校验（不写不报错，向后兼容）。"""
    results = raw.get("test_case_results")
    if results is None:
        return
    if not isinstance(results, dict):
        issues.append(
            _issue(
                "invalid_test_case_results",
                version_root,
                state_path,
                "state.yaml 的 test_case_results 必须是 用例ID -> 结果 的对象",
            )
        )
        return

    # key 必须在当前用例范围内。
    if set(results) - test_case_ids:
        issues.append(
            _issue(
                "unknown_result_test_case",
                version_root,
                state_path,
                "test_case_results 含当前范围外的测试用例 ID",
            )
        )

    # 结果取值合法性。
    if any(outcome not in _VALID_OUTCOMES for outcome in results.values()):
        issues.append(
            _issue(
                "invalid_test_case_outcome",
                version_root,
                state_path,
                "test_case_results 含非法结果值（应为 passed/failed/blocked/not_run）",
            )
        )

    completed_set = set(completed) if isinstance(completed, list) else set()

    # completed 里的 id 若出现在 results，其结果必须是终态之一（不能还是 not_run）。
    if any(results.get(cid) == "not_run" for cid in completed_set if cid in results):
        issues.append(
            _issue(
                "completed_result_not_terminal",
                version_root,
                state_path,
                "已完成用例在 test_case_results 里仍标 not_run，进度与结果不一致",
            )
        )

    # 判 passed 的用例，其 id 应已在 completed（出过结论才谈得上通过）。
    if any(
        outcome == "passed" and cid not in completed_set
        for cid, outcome in results.items()
    ):
        issues.append(
            _issue(
                "passed_result_not_completed",
                version_root,
                state_path,
                "test_case_results 判 passed 的用例未记入 completed_test_case_ids",
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

    资产文件里的路径应用正斜杠书写；为兼容偶发的 Windows 反斜杠写法，这里先把反斜杠
    归一为正斜杠，再用 ``PurePosixPath`` 解析后交给当前平台的 ``Path`` 拼接，
    Windows / macOS / Linux 行为一致。
    """

    normalized = reference.strip().replace("\\", "/")
    return version_root.joinpath(*PurePosixPath(normalized).parts)


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _parse_report_rows(content: str) -> tuple[list[tuple[str, str, str, str]], set[str]]:
    """Parse the report result table by header name.

    返回 ``(rows, missing_columns)``。表头只要同时含"测试用例"与"本次结果"两列即认定为结果表；
    其余列（使用脚本 / 执行覆盖）缺失时不再抛 ValueError，而是记入 ``missing_columns``，
    对应字段以空串占位，交由调用方降级处理，保证少列的报告也能得到明确提示而非崩溃。
    """

    lines = content.splitlines()
    header_index: int | None = None
    columns: dict[str, int] = {}
    for index, line in enumerate(lines):
        if "|" not in line:
            continue
        cells = _split_table_row(line)
        if _REPORT_COLUMNS["id"] in cells and _REPORT_COLUMNS["result"] in cells:
            columns = {
                key: cells.index(label)
                for key, label in _REPORT_COLUMNS.items()
                if label in cells
            }
            header_index = index
            break
    if header_index is None:
        return [], set()
    missing = {key for key in _REPORT_COLUMNS if key not in columns}

    rows: list[tuple[str, str, str, str]] = []
    max_index = max(columns.values())
    for line in lines[header_index + 1 :]:
        if "|" not in line:
            break
        cells = _split_table_row(line)
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells if cell):
            continue
        if len(cells) <= max_index:
            continue
        row = {key: cells[idx] for key, idx in columns.items()}
        test_case_id = row["id"].strip("`").strip()
        if not _TEST_CASE_ID_PATTERN.match(test_case_id):
            continue
        rows.append(
            (
                test_case_id,
                row.get("script", ""),
                row.get("coverage", ""),
                row.get("result", ""),
            )
        )
    return rows, missing


def _issue(code: str, version_root: Path, path: Path, message: str) -> AssetAuditIssue:
    try:
        relative_path = path.relative_to(version_root).as_posix()
    except ValueError:
        relative_path = str(path)
    return AssetAuditIssue(code=code, path=relative_path, message=message)


__all__ = ["AssetAuditIssue", "audit_system_assets", "audit_version_assets"]
