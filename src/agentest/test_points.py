"""Helpers for protecting approved test-point scope from silent changes."""

import re
from hashlib import sha256

_MUTABLE_FIELD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?(?:测试状态|测试结果|实际结果|实际说明|执行时间|证据)\s*[:：].*$"
)


def fingerprint_test_point_scope(content: str) -> str:
    """Return a stable digest for test-point scope, excluding execution fields."""

    scope_lines = [
        line.rstrip() for line in content.splitlines() if _MUTABLE_FIELD_PATTERN.match(line) is None
    ]
    normalized = "\n".join(scope_lines).strip() + "\n"
    return sha256(normalized.encode("utf-8")).hexdigest()


def scope_fingerprint_matches(content: str, expected: str) -> bool:
    """Return whether the current test-point scope matches an approved digest."""

    return bool(expected) and fingerprint_test_point_scope(content) == expected


__all__ = ["fingerprint_test_point_scope", "scope_fingerprint_matches"]
