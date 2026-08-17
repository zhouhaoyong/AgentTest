# Chrome Session Reuse and Test Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with verification checkpoints.

**Goal:** 让批量测试真正复用同一隔离 Chrome 会话，同时正确处理业务新页签，并让测试模板与 Web 窗口规则一致。

**Architecture:** `BrowserSession.goto()` 复用测试组主 Page，`new_page()` 保留为显式新页签入口；Chrome 预检只识别系统 Chrome，启动失败不再回退到 Chromium。测试脚本模板使用测试组级 Session，测试用例仍独立记录结果。卡顿控制继续采用 Prompt 约束，不增加复杂运行器。

**Tech Stack:** Python 3.11、Playwright、pytest、Pydantic、Markdown/YAML 工作流资产。

## Global Constraints

- 所有业务测试仍使用隔离的 Chrome，不复用用户已打开的浏览器窗口、Profile 或登录态。
- 不使用 Edge，不使用 Playwright 自带 Chromium 作为静默回退。
- 主 Page 默认复用；只有业务明确打开新页签时才创建辅助 Page。
- 不保存凭据、Cookie、Storage State 或敏感测试产物。
- 不执行用户业务系统测试；验证只针对 AgentTest 自身。
- 不执行 Git 命令。

---

### Task 1: 主 Page 复用与新页签边界

**Files:**
- Modify: `src/agentest/browser/session.py`
- Test: `tests/test_browser_config.py`

- [x] 写测试：同一个 Session 连续调用 `goto()` 时复用同一个 Page；显式调用 `new_page()` 时才创建新 Page。
- [x] 运行新增测试，确认当前实现失败，因为 `goto()` 每次调用 `new_page()`。
- [x] 在 `BrowserSession` 中缓存主 Page；`goto()` 只导航主 Page；保留 `new_page()` 作为显式新页签入口。
- [x] 保证 `close()` 清理 Context 时同步清空主 Page 引用。
- [x] 运行浏览器 Session 测试，确认主 Page 复用和资源释放通过。

### Task 2: Chrome-only 预检与启动

**Files:**
- Modify: `src/agentest/browser/preflight.py`
- Modify: `src/agentest/browser/session.py`
- Test: `tests/test_browser_preflight.py`
- Test: `tests/test_browser_config.py`

- [x] 写测试：Chrome 启动失败时不会尝试第二次 Chromium 回退；仅 Edge 可用时不能被识别为 Chrome 可用。
- [x] 运行新增测试，确认当前实现失败，因为当前逻辑包含 Chromium 回退并识别 Edge。
- [x] 预检只检查 Chrome 命令和 Windows 常见 Chrome 安装路径，不再检查 Edge 或 Playwright bundled Chromium。
- [x] 启动只使用 `channel="chrome"`；失败时抛出明确的 Chrome 不可用错误。
- [x] 保留“是否需要我协助安装或启用 Chrome”的用户提示，不自动安装或切换浏览器。
- [x] 运行预检和 Session 测试，确认 Chrome-only 行为通过。

### Task 3: 测试组级 Session 模板

**Files:**
- Modify: `workflow/testing/template-test-script.py`
- Modify: `workflow/testing/template-test-scripts-directory-requirement.md`
- Modify: `workflow/context/template-version-requirement.md`
- Modify: `README.md`
- Test: `tests/test_directory_contracts.py`

- [x] 写契约测试：模板声明测试组级 Session、显式传入测试环境，并说明业务新页签由测试步骤显式处理。
- [x] 运行契约测试，确认当前模板缺少这些约束。
- [x] 将模板改为测试组级 BrowserSession，多个测试用例共享该 Session；默认示例使用 Web 最大化环境，并提示实际项目应传入最终 System / Version 环境。
- [x] 补充主 Page 与辅助 Page 的使用说明，避免把每个动作拆成独立 Session。
- [x] 运行目录契约测试，确认文档和模板一致。

### Task 4: 简单时间盒规则一致性

**Files:**
- Modify: `AGENTS.md`
- Modify: `workflow/testing/prompt.md`
- Modify: `workflow/testing/rules.md`
- Modify: `workflow/regression/prompt.md`
- Test: `tests/test_directory_contracts.py`

- [x] 检查现有规则是否统一为单操作最多重试 1 次、单测试用例 5 分钟、连续 60 秒无进展即暂停。
- [x] 修正仍使用旧阈值或模糊措辞的规则，不增加 watchdog 或复杂调度器。
- [x] 增加“报告当前测试用例、当前子步骤和等待原因”的要求。
- [x] 运行工作流契约测试，确认正式测试和回归测试规则一致。

### Task 5: 全量验证

**Files:**
- No production changes.

- [x] 运行完整 pytest，确认所有 AgentTest 测试通过。
- [x] 运行 Ruff check 和 format check。
- [x] 检查当前改动只涉及 AgentTest 脚手架、代码和测试，不启动浏览器、不访问业务测试地址。

## Review Notes

- 由于 AgentTest 当前不是独立测试运行器，时间盒规则属于 Agent 执行约束，不提供操作系统级强制终止。
- 业务打开新页签不是异常；异常是未区分主 Page 和辅助 Page、或每个测试用例无意中创建新 Session。
- 本项目禁止自动 Git 操作，因此计划中的提交步骤省略。
