from agentest.test_cases import fingerprint_test_case_scope, scope_fingerprint_matches


def test_status_and_result_changes_do_not_change_scope_fingerprint() -> None:
    before = """# TC-001 查看列表

- 测试状态：未测试
- 测试结果：NOT RUN
- 实际结果：未执行
- 测试步骤：打开列表
- 预期结果：列表正常展示
"""
    after = (
        before.replace("未测试", "已测试")
        .replace("NOT RUN", "PASS")
        .replace("执行覆盖：未执行", "执行覆盖：完整")
        .replace("未执行", "列表正常展示")
    )

    assert fingerprint_test_case_scope(before) == fingerprint_test_case_scope(after)


def test_execution_coverage_changes_do_not_change_scope_fingerprint() -> None:
    before = """### TC-001 查看列表
- 测试状态：未测试
- 测试结果：NOT RUN
- 执行覆盖：未执行
- 实际说明：未执行
"""
    after = before.replace("执行覆盖：未执行", "执行覆盖：完整")

    assert fingerprint_test_case_scope(before) == fingerprint_test_case_scope(after)


def test_scope_changes_change_scope_fingerprint() -> None:
    before = """# TC-001 查看列表

- 测试状态：未测试
- 测试结果：NOT RUN
- 测试步骤：打开列表
- 预期结果：列表正常展示
"""
    after = before.replace("打开列表", "打开订单列表")

    assert fingerprint_test_case_scope(before) != fingerprint_test_case_scope(after)


def test_scope_fingerprint_matches_expected_value() -> None:
    content = "# TC-001\n\n- 测试步骤：打开列表\n"
    fingerprint = fingerprint_test_case_scope(content)

    assert scope_fingerprint_matches(content, fingerprint) is True
    assert scope_fingerprint_matches(content, "drifted") is False
