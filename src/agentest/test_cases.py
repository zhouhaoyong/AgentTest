"""Helpers for protecting approved test-case scope from silent changes.

批准范围指纹只覆盖"决定测试做什么"的字段：用例标题、关联需求、测试维度、
前置条件、测试步骤、预期结果。执行类字段（测试状态/测试结果/执行覆盖/实际结果/
执行时间/证据）以及优先级、涉及系统等描述性字段不参与指纹，改动它们不会打断已批准
的范围，也不需要重新确认。
"""

import re
from hashlib import sha256

# 用例标题（形如 ### TC-001 ...），去掉标题层级后取标题文本。
_TC_HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s*(TC-[0-9]+.*?)\s*$")
# 任意 Markdown 标题，用于判断层级与是否进入范围小节。
_HEADING_PATTERN = re.compile(r"^\s*(#{1,6})\s*(.*?)\s*$")
# 行内字段（形如 `- 关联需求：xxx` 或 `预期结果：xxx`）。
_INLINE_FIELD_PATTERN = re.compile(r"^\s*(?:[-*]\s*)?([^：:]+?)\s*[:：]\s*(.*)$")

# 参与批准范围的字段（行内形式）。
_SCOPE_INLINE_FIELDS = {"关联需求", "测试维度", "前置条件", "测试步骤", "预期结果"}
# 参与批准范围的小节标题关键词（#### 形式）。
_SCOPE_SECTION_KEYWORDS = ("前置条件", "测试步骤", "预期结果")
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

    return collected


def fingerprint_test_case_scope(content: str) -> str:
    """Return a stable digest for test-case scope, covering only scope fields."""

    normalized = "\n".join(_scope_lines(content)).strip() + "\n"
    return sha256(normalized.encode("utf-8")).hexdigest()


def scope_fingerprint_matches(content: str, expected: str) -> bool:
    """Return whether the current test-case scope matches an approved digest."""

    return bool(expected) and fingerprint_test_case_scope(content) == expected


__all__ = ["fingerprint_test_case_scope", "scope_fingerprint_matches"]
