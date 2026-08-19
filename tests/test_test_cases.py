from agentest.test_cases import (
    fingerprint_test_case_scope,
    parse_key_coverage_constraints,
    scope_fingerprint_matches,
)

_KEY_COVERAGE = """### 关键覆盖约束

#### KC-001 至少验证两个订单列表
- 用户要求：至少验证两个订单列表。
- 承接用例：TC-001、TC-002
- 完成标准：两个用例均完整执行且 PASS。
- 当前状态：未开始
"""


def test_key_coverage_scope_changes_require_reapproval() -> None:
    requirement_changed = _KEY_COVERAGE.replace("两个订单列表", "三个订单列表", 1)
    test_case_changed = _KEY_COVERAGE.replace("TC-001、TC-002", "TC-001、TC-003")
    criteria_changed = _KEY_COVERAGE.replace("均完整执行且 PASS", "均完整执行")

    assert fingerprint_test_case_scope(_KEY_COVERAGE) != fingerprint_test_case_scope(
        requirement_changed
    )
    assert fingerprint_test_case_scope(_KEY_COVERAGE) != fingerprint_test_case_scope(
        test_case_changed
    )
    assert fingerprint_test_case_scope(_KEY_COVERAGE) != fingerprint_test_case_scope(
        criteria_changed
    )


def test_key_coverage_execution_status_does_not_change_scope_fingerprint() -> None:
    executed = _KEY_COVERAGE.replace("当前状态：未开始", "当前状态：已满足")

    assert fingerprint_test_case_scope(_KEY_COVERAGE) == fingerprint_test_case_scope(executed)


def test_parses_key_coverage_test_case_mapping() -> None:
    constraints, issues = parse_key_coverage_constraints(_KEY_COVERAGE)

    assert issues == []
    assert constraints[0].id == "KC-001"
    assert constraints[0].test_case_ids == ("TC-001", "TC-002")


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
