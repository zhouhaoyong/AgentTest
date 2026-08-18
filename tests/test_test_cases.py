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
- 实际结果：未执行
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


def test_priority_and_system_changes_do_not_change_scope_fingerprint() -> None:
    before = """### TC-001 查看列表

- 优先级：P0
- 测试维度：功能测试
- 关联需求：订单列表
- 涉及系统：单系统
- 测试状态：未测试

#### 测试步骤

1. 打开列表

#### 预期结果

- 列表正常展示
"""
    after = before.replace("优先级：P0", "优先级：P1").replace(
        "涉及系统：单系统", "涉及系统：订单系统, 支付系统"
    )

    assert fingerprint_test_case_scope(before) == fingerprint_test_case_scope(after)


def test_requirement_and_dimension_changes_change_scope_fingerprint() -> None:
    before = """### TC-001 查看列表

- 测试维度：功能测试
- 关联需求：订单列表

#### 测试步骤

1. 打开列表
"""
    requirement_changed = before.replace("关联需求：订单列表", "关联需求：订单详情")
    dimension_changed = before.replace("测试维度：功能测试", "测试维度：兼容性测试")

    assert fingerprint_test_case_scope(before) != fingerprint_test_case_scope(requirement_changed)
    assert fingerprint_test_case_scope(before) != fingerprint_test_case_scope(dimension_changed)


def test_section_form_steps_and_expectations_are_in_scope() -> None:
    before = """### TC-001 查看列表

#### 前置条件

- 已登录

#### 测试步骤

1. 打开列表

#### 预期结果

- 列表正常展示
"""
    step_changed = before.replace("打开列表", "打开订单列表")
    precondition_changed = before.replace("已登录", "已登录且有订单")

    assert fingerprint_test_case_scope(before) != fingerprint_test_case_scope(step_changed)
    assert fingerprint_test_case_scope(before) != fingerprint_test_case_scope(precondition_changed)


def test_title_changes_change_scope_fingerprint() -> None:
    before = "### TC-001 查看列表\n\n- 测试步骤：打开列表\n"
    after = before.replace("查看列表", "查看订单列表")

    assert fingerprint_test_case_scope(before) != fingerprint_test_case_scope(after)


def test_scope_fingerprint_matches_expected_value() -> None:
    content = "# TC-001\n\n- 测试步骤：打开列表\n"
    fingerprint = fingerprint_test_case_scope(content)

    assert scope_fingerprint_matches(content, fingerprint) is True
    assert scope_fingerprint_matches(content, "drifted") is False
