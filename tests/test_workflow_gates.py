from pathlib import Path

from agentest.test_cases import fingerprint_test_case_scope
from agentest.workflow_gates import audit_workflow_gate


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_contract(path: Path) -> None:
    _write_text(path, "# 目录契约\n")


def _write_workspace(
    tmp_path: Path,
    *,
    current_url: str = "https://orders.test",
    linked_config: str = "linked: false\nlinked_ends: []\n",
) -> Path:
    workspace = tmp_path / "workspace"
    version = workspace / "projects" / "demo" / "systems" / "orders" / "versions" / "v1"
    _write_text(
        workspace / ".agentest" / "context.yaml",
        """project_id: demo
system_id: orders
version_id: v1
""",
    )
    _write_text(
        workspace / "projects" / "demo" / "project.yaml",
        """id: demo
name: 示例项目
""",
    )
    _write_text(
        workspace / "projects" / "demo" / "systems" / "orders" / "system.yaml",
        """id: orders
name: 订单系统
type: web
base_url: https://legacy-system.test
""",
    )
    _write_text(
        version / "version.yaml",
        f"""id: v1
name: v1
test_url: "{current_url}"
{linked_config}""",
    )
    _write_contract(version / "requirement.md")
    _write_contract(version / "requirements" / "requirement.md")
    _write_text(version / "requirements" / "source.md", "# 原始需求\n")
    _write_text(version / "requirements" / "20260819_Vv1_orders.md", "# 结构化需求\n")
    test_cases = """# 测试用例

### TC-001 查看订单

- 测试状态：未测试
- 执行覆盖：未执行
- 测试结果：NOT RUN
- 实际结果：未执行
- 执行时间：未执行
- 证据：无
"""
    _write_contract(version / "test-cases" / "requirement.md")
    _write_text(version / "test-cases" / "test-cases.md", test_cases)
    _write_text(
        workspace / ".agentest" / "state.yaml",
        f"""phase: test-cases
context_confirmed: true
test_cases_fingerprint: {fingerprint_test_case_scope(test_cases)}
completed_test_case_ids: []
test_case_results: {{}}
""",
    )
    return workspace


def _write_deliverable_workspace(tmp_path: Path) -> Path:
    workspace = _write_workspace(
        tmp_path,
        linked_config="""linked: true
linked_ends:
  - system_id: billing
    version_id: v2
""",
    )
    version = workspace / "projects" / "demo" / "systems" / "orders" / "versions" / "v1"
    linked_version = (
        workspace / "projects" / "demo" / "systems" / "billing" / "versions" / "v2"
    )
    _write_text(
        workspace / "projects" / "demo" / "systems" / "billing" / "system.yaml",
        """id: billing
name: 计费系统
type: web
""",
    )
    _write_text(
        linked_version / "version.yaml",
        """id: v2
name: v2
test_url: https://billing.test
linked: false
linked_ends: []
""",
    )
    test_cases = """# 测试用例

### 关键覆盖约束

#### KC-001 订单查询必须可用

- 用户要求：至少验证订单查询能够正常完成。
- 承接用例：TC-001
- 完成标准：承接用例完整执行且 PASS。
- 当前状态：已满足

### TC-001 查看订单

- 测试状态：已测试
- 执行覆盖：完整
- 测试结果：PASS
- 实际结果：订单列表正常展示。
- 执行时间：2026-08-19 10:00
- 证据：无
"""
    _write_text(version / "test-cases" / "test-cases.md", test_cases)
    _write_contract(version / "test-scripts" / "requirement.md")
    _write_text(
        version / "test-scripts" / "orders.py",
        """# 覆盖用例：TC-001
# 前置条件：测试环境和订单数据已就绪。
# 手动登录：用户手动登录后继续。
# 运行方式：python -m pytest orders.py -q。
# 缺少数据时：记录为 BLOCKED 并说明缺失数据。
# 结果判断：完整覆盖后才记录 PASS 或 FAIL。
""",
    )
    _write_contract(version / "report" / "requirement.md")
    _write_text(
        version / "report" / "report.md",
        """# 测试报告

## 1. 结论摘要

- 一句话结论：订单查询本次执行通过。
- 是否可宣称通过：是
- 汇总速览：通过 1 · 失败 0 · 阻塞 0 · 未运行 0（总 1）

## 2. 本次测试概况

## 4. 本次测试用例结果

| 测试用例 | 关联需求 | 使用脚本 | 执行覆盖 | 本次结果 | 说明 |
|---|---|---|---|---|---|
| TC-001 | 订单查询 | orders.py | 完整 | PASS | 订单列表正常展示。 |

## 5. 关键覆盖约束完成情况

| 约束 | 承接用例 | 状态 | 说明 |
|---|---|---|---|
| KC-001 | TC-001 | 已满足 | 承接用例完整执行且 PASS。 |

## 6. 本次结果汇总

- 本次测试用例总数：1
- PASS：1
- FAIL：0
- BLOCKED：0
- NOT RUN：0
""",
    )
    _write_contract(version / "evidence" / "requirement.md")
    _write_text(
        workspace / ".agentest" / "state.yaml",
        f"""phase: reporting
context_confirmed: true
test_cases_fingerprint: {fingerprint_test_case_scope(test_cases)}
completed_test_case_ids:
  - TC-001
test_case_results:
  TC-001: passed
""",
    )
    return workspace


def test_confirmation_gate_accepts_a_complete_current_version(tmp_path: Path) -> None:
    workspace = _write_workspace(tmp_path)

    assert audit_workflow_gate(workspace, "test_case_confirmation") == []


def test_formal_test_start_rejects_system_address_fallback(tmp_path: Path) -> None:
    workspace = _write_workspace(tmp_path, current_url="")

    codes = {issue.code for issue in audit_workflow_gate(workspace, "formal_test_start")}

    assert "missing_current_test_url" in codes


def test_formal_test_start_rejects_missing_linked_system(tmp_path: Path) -> None:
    workspace = _write_workspace(
        tmp_path,
        linked_config="""linked: true
linked_ends:
  - system_id: billing
    version_id: v1
""",
    )

    codes = {issue.code for issue in audit_workflow_gate(workspace, "formal_test_start")}

    assert "missing_linked_system" in codes


def test_formal_test_start_rejects_linked_system_without_system_config(
    tmp_path: Path,
) -> None:
    workspace = _write_workspace(
        tmp_path,
        linked_config="""linked: true
linked_ends:
  - system_id: billing
    version_id: v1
""",
    )
    linked_version = (
        workspace / "projects" / "demo" / "systems" / "billing" / "versions" / "v1"
    )
    _write_text(
        linked_version / "version.yaml",
        """id: v1
name: v1
test_url: https://billing.test
linked: false
linked_ends: []
""",
    )

    codes = {issue.code for issue in audit_workflow_gate(workspace, "formal_test_start")}

    assert "missing_linked_system_config" in codes


def test_golden_workspace_passes_every_workflow_gate(tmp_path: Path) -> None:
    workspace = _write_deliverable_workspace(tmp_path)

    for stage in ("test_case_confirmation", "formal_test_start", "report_delivery"):
        assert audit_workflow_gate(workspace, stage) == []


def test_golden_workspace_rejects_changed_key_coverage_after_approval(tmp_path: Path) -> None:
    workspace = _write_deliverable_workspace(tmp_path)
    test_cases_path = (
        workspace
        / "projects"
        / "demo"
        / "systems"
        / "orders"
        / "versions"
        / "v1"
        / "test-cases"
        / "test-cases.md"
    )
    content = test_cases_path.read_text(encoding="utf-8")
    test_cases_path.write_text(
        content.replace("至少验证订单查询能够正常完成。", "必须验证订单查询和导出能够正常完成。"),
        encoding="utf-8",
    )

    codes = {issue.code for issue in audit_workflow_gate(workspace, "formal_test_start")}

    assert "fingerprint_mismatch" in codes


def test_golden_workspace_rejects_key_coverage_without_current_test_case(
    tmp_path: Path,
) -> None:
    workspace = _write_deliverable_workspace(tmp_path)
    test_cases_path = (
        workspace
        / "projects"
        / "demo"
        / "systems"
        / "orders"
        / "versions"
        / "v1"
        / "test-cases"
        / "test-cases.md"
    )
    content = test_cases_path.read_text(encoding="utf-8")
    test_cases_path.write_text(
        content.replace("- 承接用例：TC-001", "- 承接用例：TC-999"),
        encoding="utf-8",
    )

    codes = {issue.code for issue in audit_workflow_gate(workspace, "test_case_confirmation")}

    assert "key_coverage_test_case_out_of_scope" in codes


def test_golden_workspace_rejects_state_that_disagrees_with_test_case(tmp_path: Path) -> None:
    workspace = _write_deliverable_workspace(tmp_path)
    state_path = workspace / ".agentest" / "state.yaml"
    content = state_path.read_text(encoding="utf-8")
    state_path.write_text(content.replace("TC-001: passed", "TC-001: failed"), encoding="utf-8")

    codes = {issue.code for issue in audit_workflow_gate(workspace, "report_delivery")}

    assert "test_case_state_result_mismatch" in codes


def test_golden_workspace_rejects_linked_version_without_test_url(tmp_path: Path) -> None:
    workspace = _write_deliverable_workspace(tmp_path)
    linked_version_path = (
        workspace
        / "projects"
        / "demo"
        / "systems"
        / "billing"
        / "versions"
        / "v2"
        / "version.yaml"
    )
    content = linked_version_path.read_text(encoding="utf-8")
    linked_version_path.write_text(
        content.replace("test_url: https://billing.test", 'test_url: ""'),
        encoding="utf-8",
    )

    codes = {issue.code for issue in audit_workflow_gate(workspace, "formal_test_start")}

    assert "missing_linked_test_url" in codes


def test_golden_workspace_rejects_passing_report_with_blocked_key_coverage(
    tmp_path: Path,
) -> None:
    workspace = _write_deliverable_workspace(tmp_path)
    version = workspace / "projects" / "demo" / "systems" / "orders" / "versions" / "v1"
    test_cases_path = version / "test-cases" / "test-cases.md"
    test_cases = test_cases_path.read_text(encoding="utf-8")
    test_cases_path.write_text(
        test_cases.replace("- 测试状态：已测试", "- 测试状态：未测试")
        .replace("- 执行覆盖：完整", "- 执行覆盖：部分")
        .replace("- 测试结果：PASS", "- 测试结果：BLOCKED")
        .replace("- 当前状态：已满足", "- 当前状态：部分阻塞"),
        encoding="utf-8",
    )
    _write_text(
        workspace / ".agentest" / "state.yaml",
        f"""phase: reporting
context_confirmed: true
test_cases_fingerprint: {fingerprint_test_case_scope(test_cases)}
completed_test_case_ids:
  - TC-001
test_case_results:
  TC-001: blocked
""",
    )
    report_path = version / "report" / "report.md"
    report = report_path.read_text(encoding="utf-8")
    report_path.write_text(
        report.replace(
            "通过 1 · 失败 0 · 阻塞 0 · 未运行 0",
            "通过 0 · 失败 0 · 阻塞 1 · 未运行 0",
        )
        .replace(
            "| TC-001 | 订单查询 | orders.py | 完整 | PASS |",
            "| TC-001 | 订单查询 | orders.py | 部分 | BLOCKED |",
        )
        .replace("| KC-001 | TC-001 | 已满足 |", "| KC-001 | TC-001 | 部分阻塞 |")
        .replace("- PASS：1", "- PASS：0")
        .replace("- BLOCKED：0", "- BLOCKED：1"),
        encoding="utf-8",
    )

    codes = {issue.code for issue in audit_workflow_gate(workspace, "report_delivery")}

    assert "inconsistent_report_conclusion" in codes


def test_golden_workspace_rejects_script_that_declares_the_wrong_test_case(
    tmp_path: Path,
) -> None:
    workspace = _write_deliverable_workspace(tmp_path)
    script_path = (
        workspace
        / "projects"
        / "demo"
        / "systems"
        / "orders"
        / "versions"
        / "v1"
        / "test-scripts"
        / "orders.py"
    )
    content = script_path.read_text(encoding="utf-8")
    script_path.write_text(
        content.replace("覆盖用例：TC-001", "覆盖用例：TC-999"),
        encoding="utf-8",
    )

    codes = {issue.code for issue in audit_workflow_gate(workspace, "report_delivery")}

    assert "script_test_case_out_of_scope" in codes
    assert "report_script_test_case_mismatch" in codes
