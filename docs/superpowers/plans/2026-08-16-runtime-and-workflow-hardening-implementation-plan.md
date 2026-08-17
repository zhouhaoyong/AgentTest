# 运行环境与工作流可靠性改造实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将运行环境、浏览器兜底、跨 Agent 状态和多 System 联动范围的可靠性收敛到已确认的规则。

**Architecture:** 保持现有轻量文件化边界。Schema 继续只校验单个 YAML 文件，BrowserSession 继续只封装 Playwright 生命周期；通过先失败的单元测试保护新增行为。MCP 从业务用户可见的状态和规则中移除，不新增任何连接或安装能力。

**Tech Stack:** Python 3.11、Pydantic v2、PyYAML、Playwright Python、pytest、Ruff。

---

### Task 1: 固化 Python 3.11 运行基线

**Files:**
- Modify: `.python-version`
- Modify: `prd.md:50-57`
- Modify: `tests/test_architecture_guard.py`

- [ ] **Step 1: 写入失败的版本一致性测试**

```python
def test_runtime_baseline_is_python_311() -> None:
    root = Path(__file__).parents[1]

    assert (root / ".python-version").read_text(encoding="utf-8").strip() == "3.11"
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in pyproject
    assert 'target-version = "py311"' in pyproject
    assert "- Python `>= 3.11`" in (root / "prd.md").read_text(encoding="utf-8")
```

- [ ] **Step 2: 在 Python 3.13 下运行该测试，确认因 3.13 默认版本与 PRD 声明失败**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_architecture_guard.py::test_runtime_baseline_is_python_311 -v`

Expected: FAIL，指出 `.python-version` 或 PRD 未统一为 Python 3.11。

- [ ] **Step 3: 最小化统一版本声明**

```text
.python-version: 3.11
prd.md: - Python `>= 3.11`
```

保留既有 `pyproject.toml` 的 `>=3.11` 和 Ruff `py311` 配置；不改写历史设计记录。

- [ ] **Step 4: 重跑版本一致性测试**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_architecture_guard.py::test_runtime_baseline_is_python_311 -v`

Expected: PASS。

### Task 2: 保护 BrowserSession 启动失败路径

**Files:**
- Modify: `tests/test_browser_config.py`
- Modify: `src/agentest/browser/session.py:22-66`

- [ ] **Step 1: 写入 Context 创建失败后释放 Browser 与 Playwright 的失败测试**

在测试中用 `monkeypatch` 替换 `playwright.sync_api.sync_playwright`，替身 Browser 的 `new_context()` 抛出 `RuntimeError("context failed")`。断言 `BrowserSession.start()` 仍抛出该异常，并且替身 Browser 的 `close()` 与 Playwright 的 `stop()` 各被调用一次，Session 的三个内部资源字段均回到 `None`。

- [ ] **Step 2: 运行失败测试，确认当前实现未清理资源**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_browser_config.py::test_browser_releases_resources_when_context_setup_fails -v`

Expected: FAIL，关闭调用次数为零。

- [ ] **Step 3: 写入 Chrome 回退与最大化 Context 参数的测试**

替身 Chromium 第一次收到 `channel="chrome"` 时抛异常、第二次返回 Browser；断言第二次启动成功，参数包含 `--incognito`、`--start-maximized`，Context 使用 `no_viewport=True`，关闭后所有资源释放。

- [ ] **Step 4: 在 `start()` 中增加最小清理保护**

将 Chrome 启动、Context 创建和默认超时设置置于一个 `try` 中；任何异常时调用 `close()`，抑制清理过程中的次要异常，再重新抛出原始异常。保留已有 Chrome → Chromium 回退语义与公共 API。

- [ ] **Step 5: 运行浏览器配置测试**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_browser_config.py -v`

Expected: PASS，且不启动真实浏览器。

### Task 3: 收紧跨 Agent 状态并隐藏 MCP

**Files:**
- Modify: `tests/test_schemas.py`
- Modify: `tests/test_architecture_guard.py`
- Modify: `src/agentest/schemas/workspace.py`
- Modify: `prd.md:37-45,228-236`
- Modify: `workflow/testing/rules.md:21-26`

- [ ] **Step 1: 写入失败的状态校验测试**

```python
@pytest.mark.parametrize(
    "phase",
    [
        "intake",
        "context",
        "requirements",
        "exploration",
        "test-points",
        "testing",
        "reporting",
        "regression",
    ],
)
def test_workspace_state_accepts_only_workflow_phases(phase: str) -> None:
    assert WorkspaceState(phase=phase).phase == phase


def test_workspace_state_rejects_unknown_phase_and_mcp_consent() -> None:
    with pytest.raises(ValidationError):
        WorkspaceState(phase="requirement")
    with pytest.raises(ValidationError):
        BrowserPreferences(mcp_consent="granted")
```

另写浏览器偏好非法值被拒绝的测试。

- [ ] **Step 2: 运行状态测试，确认旧实现接受未知阶段和 `mcp_consent`**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_schemas.py -k 'workspace_state or browser_preferences' -v`

Expected: FAIL。

- [ ] **Step 3: 以 Literal 收敛状态**

在 `workspace.py` 中定义 `WorkflowPhase` 与 `BrowserSelection`；将默认阶段改为 `intake`，浏览器选择只允许 `auto`、`agent_browser`、`playwright`，删除 `mcp_consent`。在 `schemas/__init__.py` 中导出新增的公共类型。

- [ ] **Step 4: 写入用户文档不暴露 MCP 的失败测试**

```python
def test_user_facing_browser_guidance_hides_mcp_details() -> None:
    root = Path(__file__).parents[1]
    for path in [root / "README.md", root / "prd.md", root / "workflow" / "testing" / "rules.md"]:
        assert "MCP" not in path.read_text(encoding="utf-8")
```

- [ ] **Step 5: 运行文档测试，确认 PRD 与正式测试规则仍提及 MCP**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_architecture_guard.py::test_user_facing_browser_guidance_hides_mcp_details -v`

Expected: FAIL。

- [ ] **Step 6: 用用户可理解的浏览器能力表述替换 MCP 文案**

保留“不自动安装或配置外部浏览器连接”“不复用已登录会话”的安全边界；删除 PRD 和正式测试规则中 MCP 的字面表述，不在 README 新增相关术语。

- [ ] **Step 7: 重跑状态与文档测试**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_schemas.py -k 'workspace_state or browser_preferences' -v && PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_architecture_guard.py::test_user_facing_browser_guidance_hides_mcp_details -v`

Expected: PASS。

### Task 4: 校验多 System 联动范围

**Files:**
- Create: `src/agentest/schemas/integration_scope.py`
- Modify: `src/agentest/schemas/__init__.py`
- Modify: `tests/test_schemas.py`

- [ ] **Step 1: 写入联动范围的失败测试**

```python
def test_integration_scope_accepts_ordered_systems() -> None:
    scope = IntegrationScopeConfig(
        id="order-sync",
        name="订单联动",
        systems=[
            {"order": 1, "system_id": "shop-web", "version_id": "v1"},
            {"order": 2, "system_id": "warehouse-web", "version_id": "v2"},
        ],
    )
    assert [member.order for member in scope.systems] == [1, 2]
```

另写少于两个参与项、重复顺序和非法 System / Version ID 都触发 `ValidationError` 的测试。

- [ ] **Step 2: 运行联动范围测试，确认因类型不存在而失败**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_schemas.py -k integration_scope -v`

Expected: FAIL，指出 `IntegrationScopeConfig` 尚不存在。

- [ ] **Step 3: 新增最小 Schema**

`IntegrationScopeMember` 保存 `order`、`system_id`、`version_id`、`test_url`；`IntegrationScopeConfig` 保存 `id`、`name`、`description`、`systems`。复用 `AssetModel` 和 `validate_asset_id`，要求至少两个成员、顺序正数且唯一；不读取项目目录，不校验远端地址。

- [ ] **Step 4: 导出 Schema 并重跑相关测试**

Run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_schemas.py -k integration_scope -v`

Expected: PASS。

### Task 5: 在 Python 3.11 环境完成全量验收

**Files:**
- Verify only: 当前工作区

- [ ] **Step 1: 使用 uv 在独立 Python 3.11 环境同步锁定依赖**

Run: `uv run --python 3.11 --no-progress python --version`

Expected: `Python 3.11.x`。

- [ ] **Step 2: 运行完整测试套件**

Run: `uv run --python 3.11 --no-progress pytest -p no:cacheprovider`

Expected: 全部测试通过。

- [ ] **Step 3: 运行 Ruff 检查**

Run: `uv run --python 3.11 --no-progress ruff check .`

Expected: `All checks passed!`。

- [ ] **Step 4: 复核范围**

确认未改动 `projects/`，未处理第 1、2 项，也未执行 Git 操作。
