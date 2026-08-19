from pathlib import Path

import yaml

from agentest.asset_audit import audit_system_assets, audit_version_assets
from agentest.test_cases import fingerprint_test_case_scope


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_contract(path: Path, name: str) -> None:
    write_text(path, f"# {name} 目录契约\n\n## 目录职责\n\n保存资产。\n")


def test_audit_reports_missing_execution_assets_and_fields(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(
        version / "test-cases" / "test-cases.md",
        """# 测试用例

### TC-001 查看列表

#### 测试步骤

1. 打开列表。

#### 预期结果

- 列表展示。
""",
    )

    issues = audit_version_assets(version, require_execution_assets=True)
    codes = {issue.code for issue in issues}

    assert "missing_test_cases_contract" in codes
    assert "missing_test_scripts" in codes
    assert "missing_report" in codes
    assert "missing_execution_field" in codes


def test_audit_rejects_pass_when_execution_is_only_partial(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(
        version / "test-cases" / "test-cases.md",
        """# 测试用例

### TC-001 查看列表

- 测试状态：已测试
- 测试结果：PASS
- 执行覆盖：部分
- 实际结果：只验证了其中一个子场景。
- 执行时间：2026-08-17 10:00
- 证据：无
""",
    )

    codes = {issue.code for issue in audit_version_assets(version)}

    assert "inconsistent_execution_coverage" in codes


def test_audit_rejects_pass_when_test_case_is_not_tested(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(
        version / "test-cases" / "test-cases.md",
        """# 测试用例

### TC-001 查看列表

- 测试状态：未测试
- 测试结果：PASS
- 执行覆盖：未执行
- 实际结果：未执行。
- 执行时间：未执行
- 证据：无
""",
    )

    codes = {issue.code for issue in audit_version_assets(version)}

    assert "inconsistent_execution_coverage" in codes


def test_audit_accepts_structured_system_assets(tmp_path: Path) -> None:
    system = tmp_path / "projects" / "demo" / "systems" / "web"
    write_text(
        system / "element-map" / "index.yaml",
        """version: 1
modules:
  - id: login
    file: modules/login.yaml
    purpose: 登录与全局导航
""",
    )
    write_text(
        system / "element-map" / "modules" / "login.yaml",
        """module_id: login
title: 登录与全局导航
verified_version: v1
viewport: 1920x1080
pages:
  - id: login-page
    url_pattern: '#/login'
    entry:
      - type: url
        value: '#/login'
    elements:
      - id: login-button
        purpose: 提交登录
        text: 登录
        locator:
          primary:
            type: role
            value: 'get_by_role("button", name="登录")'
        stability: 语义角色与稳定文案
        verified_version: v1
        verified_viewport: 1920x1080
""",
    )
    write_text(system / "memory" / "index.md", "# Memory 索引\n")
    write_text(
        system / "memory" / "modules" / "business-rules.md",
        """# 业务规则

## 验证 Version

v1

## 长期用途

供后续版本复用稳定规则。

## 稳定事实

登录成功后进入首页。
""",
    )

    assert audit_system_assets(system) == []


def _system_with_memory(system: Path) -> None:
    write_text(system / "memory" / "index.md", "# Memory 索引\n")
    write_text(
        system / "memory" / "modules" / "business-rules.md",
        """# 业务规则

## 验证 Version

v1

## 长期用途

供后续版本复用稳定规则。

## 稳定事实

登录成功后进入首页。
""",
    )


def test_audit_accepts_minimal_element_map_without_optional_fields(tmp_path: Path) -> None:
    # 分级校验：省略 stability / verified_version / verified_viewport / entry 等增强字段仍应通过。
    system = tmp_path / "projects" / "demo" / "systems" / "web"
    write_text(
        system / "element-map" / "index.yaml",
        """version: 1
modules:
  - id: login
    file: modules/login.yaml
    purpose: 登录与全局导航
""",
    )
    write_text(
        system / "element-map" / "modules" / "login.yaml",
        """module_id: login
title: 登录与全局导航
viewport: 1920x1080
pages:
  - id: login-page
    url_pattern: '#/login'
    elements:
      - id: login-button
        purpose: 提交登录
        locator:
          primary:
            type: role
            value: 'get_by_role("button", name="登录")'
""",
    )
    _system_with_memory(system)

    assert audit_system_assets(system) == []


def test_audit_reports_element_missing_core_locator(tmp_path: Path) -> None:
    # 缺少定位核心字段（locator.primary.value）时必须报错。
    system = tmp_path / "projects" / "demo" / "systems" / "web"
    write_text(
        system / "element-map" / "index.yaml",
        """version: 1
modules:
  - id: login
    file: modules/login.yaml
    purpose: 登录
""",
    )
    write_text(
        system / "element-map" / "modules" / "login.yaml",
        """module_id: login
title: 登录
pages:
  - id: login-page
    url_pattern: '#/login'
    elements:
      - id: login-button
        purpose: 提交登录
        locator:
          primary:
            type: role
""",
    )
    _system_with_memory(system)

    codes = {issue.code for issue in audit_system_assets(system)}

    assert "incomplete_element_map_element" in codes


def test_audit_accepts_index_with_new_fields_and_global(tmp_path: Path) -> None:
    # 索引新字段（title/routes/covers/requirement_keywords 等）与 global 段应通过。
    system = tmp_path / "projects" / "demo" / "systems" / "web"
    write_text(
        system / "element-map" / "index.yaml",
        """version: 1
global:
  - id: top-nav
    purpose: 全局顶部导航
    locator:
      primary:
        type: role
        value: 'get_by_role("navigation")'
modules:
  - id: contacts
    file: modules/contacts.yaml
    title: 通讯录
    routes:
      - '#/user-center/contacts'
    entry: 顶部导航"通讯录"
    covers:
      - 接单数量
    requirement_keywords:
      - 接单数量
    last_verified_version: v1
""",
    )
    write_text(
        system / "element-map" / "modules" / "contacts.yaml",
        """module_id: contacts
title: 通讯录
viewport: 1920x1080
pages:
  - id: contacts-list
    url_pattern: '#/user-center/contacts'
    elements:
      - id: order-grid
        purpose: 接单数量网格
        locator:
          primary:
            type: css
            value: 'div.n-grid.max-w-520px'
""",
    )
    _system_with_memory(system)

    assert audit_system_assets(system) == []


def test_audit_flags_weak_locators(tmp_path: Path) -> None:
    # 模糊 class 匹配、css 含中文、text 带操作性括号都应标为 weak_element_locator。
    system = tmp_path / "projects" / "demo" / "systems" / "web"
    write_text(
        system / "element-map" / "index.yaml",
        """version: 1
modules:
  - id: orders
    file: modules/orders.yaml
""",
    )
    write_text(
        system / "element-map" / "modules" / "orders.yaml",
        """module_id: orders
title: 订单
pages:
  - id: order-list
    url_pattern: '#/orders'
    elements:
      - id: gear
        purpose: 设置齿轮
        locator:
          primary:
            type: css
            value: "[class*='setting']"
      - id: cn-css
        purpose: 中文伪选择器
        locator:
          primary:
            type: css
            value: 订单标题
      - id: order-open
        purpose: 打开订单
        locator:
          primary:
            type: text
            value: 订单标题（点击卡片标题区）
""",
    )
    _system_with_memory(system)

    weak = [
        issue for issue in audit_system_assets(system) if issue.code == "weak_element_locator"
    ]

    assert len(weak) == 3


def test_audit_skips_unverified_element_stub(tmp_path: Path) -> None:
    # 标 unverified 的存根元素（无 locator）不应触发 incomplete_element_map_element。
    system = tmp_path / "projects" / "demo" / "systems" / "web"
    write_text(
        system / "element-map" / "index.yaml",
        """version: 1
modules:
  - id: contacts
    file: modules/contacts.yaml
""",
    )
    write_text(
        system / "element-map" / "modules" / "contacts.yaml",
        """module_id: contacts
title: 通讯录
viewport: 1920x1080
pages:
  - id: contacts-list
    url_pattern: '#/user-center/contacts'
    elements:
      - id: batch-limit-entry
        purpose: 批量限单入口
        unverified: true
""",
    )
    _system_with_memory(system)

    assert audit_system_assets(system) == []


def test_audit_reports_incomplete_element_map_and_memory(tmp_path: Path) -> None:
    system = tmp_path / "projects" / "demo" / "systems" / "web"
    write_text(system / "element-map" / "index.yaml", "modules: []\n")
    write_text(system / "memory" / "index.md", "# Memory 索引\n")
    write_text(
        system / "memory" / "modules" / "business-rules.md",
        """# 业务规则

## 稳定事实

账号 password 不得写入资产。
""",
    )

    codes = {issue.code for issue in audit_system_assets(system)}

    assert "invalid_element_map_index" in codes
    assert "incomplete_memory_module" in codes
    assert "sensitive_memory_content" in codes


def test_audit_accepts_consistent_executed_version(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    test_cases = """# 测试用例

### TC-001 查看列表

- 测试状态：已测试
- 测试结果：PASS
- 执行覆盖：完整
- 实际结果：列表展示。
- 执行时间：2026-08-17 10:00
- 证据：无

#### 测试步骤

1. 打开列表。

#### 预期结果

- 列表展示。
"""
    write_text(version / "test-cases" / "test-cases.md", test_cases)
    write_contract(version / "test-cases" / "requirement.md", "test-cases")
    write_contract(version / "test-scripts" / "requirement.md", "test-scripts")
    write_text(
        version / "test-scripts" / "lists.py",
        """\"\"\"TC-001

前置条件：测试环境可用。手动登录后运行：python -m pytest lists.py -q。
\"\"\"
""",
    )
    write_contract(version / "report" / "requirement.md", "report")
    write_text(
        version / "report" / "report.md",
        """# 测试报告

## 测试用例结果

| 测试用例 | 关联需求 | 使用脚本 | 执行覆盖 | 本次结果 | 说明 |
|---|---|---|---|---|---|
| TC-001 | 列表 | lists.py | 完整 | PASS | 列表展示。 |

## 本次结果汇总

- 本次测试用例总数：1
- PASS：1
- FAIL：0
- BLOCKED：0
- NOT RUN：0
""",
    )
    state_path = tmp_path / ".agentest" / "state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        yaml.safe_dump(
            {
                "completed_test_case_ids": ["TC-001"],
                "test_cases_fingerprint": fingerprint_test_case_scope(test_cases),
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    assert audit_version_assets(version, state_path=state_path, require_execution_assets=True) == []


def test_audit_reports_incomplete_test_script_metadata(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "test-scripts" / "lists.py", "# TC-001\n")

    issues = audit_version_assets(version, require_execution_assets=True)

    assert any(
        issue.code == "incomplete_test_script_metadata" and issue.path == "test-scripts/lists.py"
        for issue in issues
    )


def test_audit_reports_scope_count_and_evidence_problems(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    test_cases = """# 测试用例

### TC-001 查看列表

- 测试状态：已测试
- 测试结果：FAIL
- 执行覆盖：完整
- 实际结果：失败。
- 执行时间：2026-08-17 10:00
- 证据：evidence/bug.png
"""
    write_text(version / "test-cases" / "test-cases.md", test_cases)
    write_contract(version / "test-cases" / "requirement.md", "test-cases")
    write_contract(version / "report" / "requirement.md", "report")
    write_text(
        version / "report" / "report.md",
        """# 测试报告

| 测试用例 | 关联需求 | 使用脚本 | 执行覆盖 | 本次结果 | 说明 |
|---|---|---|---|---|---|
| TC-002 | 列表 | lists.py | 完整 | PASS | 错误。 |

## 本次结果汇总

- 本次测试用例总数：2
- PASS：2
- FAIL：0
- BLOCKED：0
- NOT RUN：0
""",
    )

    codes = {issue.code for issue in audit_version_assets(version, require_execution_assets=True)}

    assert "report_test_case_mismatch" in codes
    assert "report_summary_mismatch" in codes
    assert "missing_evidence" in codes
    assert "missing_referenced_asset" in codes


def test_audit_reports_report_result_and_coverage_mismatch(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    test_cases = """# 测试用例

### TC-001 查看列表

- 测试状态：已测试
- 测试结果：BLOCKED
- 执行覆盖：部分
- 实际结果：缺少第二个状态数据。
- 执行时间：2026-08-17 10:00
- 证据：无
"""
    write_text(version / "test-cases" / "test-cases.md", test_cases)
    write_contract(version / "test-cases" / "requirement.md", "test-cases")
    write_contract(version / "test-scripts" / "requirement.md", "test-scripts")
    write_text(
        version / "test-scripts" / "lists.py",
        """\"\"\"TC-001

前置条件：测试环境可用。手动登录后运行：python -m pytest lists.py -q。
\"\"\"
""",
    )
    write_contract(version / "report" / "requirement.md", "report")
    write_text(
        version / "report" / "report.md",
        """# 测试报告

| 测试用例 | 关联需求 | 使用脚本 | 执行覆盖 | 本次结果 | 说明 |
|---|---|---|---|---|---|
| TC-001 | 列表 | lists.py | 完整 | PASS | 表格错误地写成完整通过。 |

## 本次结果汇总

- 本次测试用例总数：1
- PASS：1
- FAIL：0
- BLOCKED：0
- NOT RUN：0
""",
    )

    codes = {issue.code for issue in audit_version_assets(version, require_execution_assets=True)}

    assert "report_execution_coverage_mismatch" in codes
    assert "report_result_mismatch" in codes


def test_audit_reports_fingerprint_drift(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(
        version / "test-cases" / "test-cases.md",
        """# 测试用例

### TC-001 查看列表

- 测试状态：未测试
- 测试结果：NOT RUN
- 执行覆盖：未执行
- 实际结果：未执行
- 执行时间：未执行
- 证据：无
""",
    )
    write_contract(version / "test-cases" / "requirement.md", "test-cases")
    state_path = tmp_path / ".agentest" / "state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("test_cases_fingerprint: drifted\n", encoding="utf-8")

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "fingerprint_mismatch" in codes


def test_audit_reports_missing_fingerprint(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    write_text(
        version / "test-cases" / "test-cases.md",
        """# 测试用例

### TC-001 查看列表

- 测试状态：未测试
- 测试结果：NOT RUN
- 执行覆盖：未执行
- 实际结果：未执行
- 执行时间：未执行
- 证据：无
""",
    )
    write_contract(version / "test-cases" / "requirement.md", "test-cases")
    state_path = tmp_path / ".agentest" / "state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("completed_test_case_ids: []\n", encoding="utf-8")

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "missing_fingerprint" in codes


def _write_state_fixture(tmp_path: Path, state: dict) -> tuple[Path, Path]:
    """构造一个结构完整、无关校验干净的 version，只让 state 校验成为唯一变量。"""
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    test_cases = """# 测试用例

### TC-001 查看列表

- 测试状态：未测试
- 测试结果：NOT RUN
- 执行覆盖：未执行
- 实际结果：未执行
- 执行时间：未执行
- 证据：无
"""
    write_text(version / "test-cases" / "test-cases.md", test_cases)
    write_contract(version / "test-cases" / "requirement.md", "test-cases")
    state.setdefault("test_cases_fingerprint", fingerprint_test_case_scope(test_cases))
    state_path = tmp_path / ".agentest" / "state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(yaml.safe_dump(state, allow_unicode=True), encoding="utf-8")
    return version, state_path


def test_audit_accepts_valid_test_case_results(tmp_path: Path) -> None:
    version, state_path = _write_state_fixture(
        tmp_path,
        {
            "completed_test_case_ids": ["TC-001"],
            "test_case_results": {"TC-001": "passed"},
        },
    )

    assert audit_version_assets(version, state_path=state_path) == []


def test_audit_accepts_state_without_results(tmp_path: Path) -> None:
    # 不写 test_case_results 保持向后兼容，不应报错。
    version, state_path = _write_state_fixture(
        tmp_path, {"completed_test_case_ids": []}
    )

    assert audit_version_assets(version, state_path=state_path) == []


def test_audit_flags_result_out_of_scope(tmp_path: Path) -> None:
    version, state_path = _write_state_fixture(
        tmp_path, {"test_case_results": {"TC-999": "failed"}}
    )

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "unknown_result_test_case" in codes


def test_audit_flags_invalid_outcome_value(tmp_path: Path) -> None:
    version, state_path = _write_state_fixture(
        tmp_path, {"test_case_results": {"TC-001": "flaky"}}
    )

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "invalid_test_case_outcome" in codes


def test_audit_flags_completed_result_not_terminal(tmp_path: Path) -> None:
    version, state_path = _write_state_fixture(
        tmp_path,
        {
            "completed_test_case_ids": ["TC-001"],
            "test_case_results": {"TC-001": "not_run"},
        },
    )

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "completed_result_not_terminal" in codes


def test_audit_flags_passed_result_not_completed(tmp_path: Path) -> None:
    version, state_path = _write_state_fixture(
        tmp_path,
        {
            "completed_test_case_ids": [],
            "test_case_results": {"TC-001": "passed"},
        },
    )

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "passed_result_not_completed" in codes
