"""Helpers for protecting approved test-case scope from silent changes.

批准范围指纹覆盖"决定测试做什么"的字段：关键覆盖约束的编号、用户要求、承接用例、
完成标准，以及用例标题、关联需求、测试维度、前置条件、测试步骤和预期结果。关键覆盖
约束当前状态、执行类字段（测试状态/测试结果/执行覆盖/实际结果/执行时间/证据）以及
优先级、涉及系统等描述性字段不参与指纹，改动它们不会打断已批准的范围，也不需要重新确认。
"""

import re
from dataclasses import dataclass
from hashlib import sha256

# 用例标题（形如 ### TC-001 ...），去掉标题层级后取标题文本。
_TC_HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s*(TC-[0-9]+.*?)\s*$")
# 任意 Markdown 标题，用于判断层级与是否进入范围小节。
_HEADING_PATTERN = re.compile(r"^\s*(#{1,6})\s*(.*?)\s*$")
# 行内字段（形如 `- 关联需求：xxx` 或 `预期结果：xxx`）。
_INLINE_FIELD_PATTERN = re.compile(r"^\s*(?:[-*]\s*)?([^：:]+?)\s*[:：]\s*(.*)$")
_KEY_COVERAGE_ITEM_PATTERN = re.compile(r"^KC-[0-9]+\b")
_TEST_CASE_ID_PATTERN = re.compile(r"\bTC-[0-9]+\b")

# 参与批准范围的字段（行内形式）。
_SCOPE_INLINE_FIELDS = {
    "关联需求",
    "测试维度",
    "前置条件",
    "测试步骤",
    "预期结果",
    "测试数据",
    "数据校对",
}
# 参与批准范围的小节标题关键词（#### 形式）。
_SCOPE_SECTION_KEYWORDS = ("前置条件", "测试步骤", "预期结果", "测试数据", "数据校对")
# 不参与批准范围的行内字段：执行类 + 描述类。
_NON_SCOPE_INLINE_FIELDS = {
    "测试状态",
    "测试结果",
    "执行覆盖",
    "实际结果",
    "执行时间",
    "证据",
    "优先级",
    "涉及系统",
}
_KEY_COVERAGE_FIELDS = ("用户要求", "承接用例", "完成标准", "当前状态")


@dataclass(frozen=True)
class KeyCoverageConstraint:
    """A user-required coverage constraint that must survive approval."""

    id: str
    title: str
    user_requirement: str
    test_case_ids: tuple[str, ...]
    completion_criteria: str
    current_status: str


@dataclass(frozen=True)
class KeyCoverageParseIssue:
    """A structural problem in the key coverage section."""

    code: str
    message: str


def parse_key_coverage_constraints(
    content: str,
) -> tuple[list[KeyCoverageConstraint], list[KeyCoverageParseIssue]]:
    """Parse the optional key coverage section without execution side effects."""

    section_level: int | None = None
    constraints: list[KeyCoverageConstraint] = []
    issues: list[KeyCoverageParseIssue] = []
    current_id = ""
    current_title = ""
    current_fields: dict[str, str] = {}
    seen_ids: set[str] = set()

    def finish_current() -> None:
        nonlocal current_id, current_title, current_fields
        if not current_id:
            return
        missing = [field for field in _KEY_COVERAGE_FIELDS if not current_fields.get(field)]
        if missing:
            issues.append(
                KeyCoverageParseIssue(
                    "incomplete_key_coverage_constraint",
                    f"{current_id} 缺少字段：{', '.join(missing)}",
                )
            )
        else:
            test_case_ids = tuple(
                sorted(set(_TEST_CASE_ID_PATTERN.findall(current_fields["承接用例"])))
            )
            if not test_case_ids:
                issues.append(
                    KeyCoverageParseIssue(
                        "invalid_key_coverage_test_cases",
                        f"{current_id} 的承接用例必须包含至少一个 TC-xxx",
                    )
                )
            elif current_id in seen_ids:
                issues.append(
                    KeyCoverageParseIssue(
                        "duplicate_key_coverage_id",
                        f"关键覆盖约束 ID 重复：{current_id}",
                    )
                )
            else:
                seen_ids.add(current_id)
                constraints.append(
                    KeyCoverageConstraint(
                        id=current_id,
                        title=current_title,
                        user_requirement=current_fields["用户要求"],
                        test_case_ids=test_case_ids,
                        completion_criteria=current_fields["完成标准"],
                        current_status=current_fields["当前状态"],
                    )
                )
        current_id = ""
        current_title = ""
        current_fields = {}

    for raw in content.splitlines():
        line = raw.rstrip()
        heading_match = _HEADING_PATTERN.match(line)
        if heading_match is not None:
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            if section_level is None:
                if heading == "关键覆盖约束":
                    section_level = level
                continue
            if level <= section_level:
                finish_current()
                break
            item_match = _KEY_COVERAGE_ITEM_PATTERN.match(heading)
            if item_match is not None:
                finish_current()
                current_id = item_match.group(0)
                current_title = heading[len(current_id) :].strip()
            continue

        if section_level is None or not current_id:
            continue
        field_match = _INLINE_FIELD_PATTERN.match(line)
        if field_match is None:
            continue
        key = field_match.group(1).strip()
        if key in _KEY_COVERAGE_FIELDS:
            current_fields[key] = field_match.group(2).strip()

    if section_level is None:
        return constraints, issues
    finish_current()
    if not constraints and not issues:
        issues.append(
            KeyCoverageParseIssue(
                "missing_key_coverage_constraint",
                "“关键覆盖约束”章节至少需要一条 KC-xxx 约束，或删除整个章节",
            )
        )
    return constraints, issues


def _scope_lines(content: str) -> list[str]:
    """Return only the lines that define approved test-case scope."""

    collected: list[str] = []
    in_scope_section = False

    for raw in content.splitlines():
        line = raw.rstrip()

        tc_match = _TC_HEADING_PATTERN.match(line)
        if tc_match is not None:
            collected.append(tc_match.group(1))
            in_scope_section = False
            continue

        heading_match = _HEADING_PATTERN.match(line)
        if heading_match is not None:
            level, text = heading_match.group(1), heading_match.group(2)
            is_scope_section = len(level) >= 4 and any(
                keyword in text for keyword in _SCOPE_SECTION_KEYWORDS
            )
            in_scope_section = is_scope_section
            if is_scope_section:
                collected.append(text)
            continue

        field_match = _INLINE_FIELD_PATTERN.match(line)
        if field_match is not None:
            key = field_match.group(1).strip()
            if key in _SCOPE_INLINE_FIELDS:
                collected.append(line)
                continue
            if key in _NON_SCOPE_INLINE_FIELDS:
                continue
            # 未知行内字段：仅在范围小节内才算范围内容。

        if in_scope_section:
            collected.append(line)

    constraints, _ = parse_key_coverage_constraints(content)
    for constraint in constraints:
        collected.extend(
            (
                f"关键覆盖约束：{constraint.id}",
                f"标题：{constraint.title}",
                f"用户要求：{constraint.user_requirement}",
                f"承接用例：{','.join(constraint.test_case_ids)}",
                f"完成标准：{constraint.completion_criteria}",
            )
        )

    return collected


def fingerprint_test_case_scope(content: str) -> str:
    """Return a stable digest for test-case scope, covering only scope fields."""

    normalized = "\n".join(_scope_lines(content)).strip() + "\n"
    return sha256(normalized.encode("utf-8")).hexdigest()


def scope_fingerprint_matches(content: str, expected: str) -> bool:
    """Return whether the current test-case scope matches an approved digest."""

    return bool(expected) and fingerprint_test_case_scope(content) == expected


__all__ = [
    "KeyCoverageConstraint",
    "KeyCoverageParseIssue",
    "fingerprint_test_case_scope",
    "parse_key_coverage_constraints",
    "scope_fingerprint_matches",
]
