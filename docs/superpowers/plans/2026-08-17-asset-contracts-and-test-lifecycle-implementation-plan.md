# AgentTest 资产契约与测试生命周期实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完善 AgentTest 的结构化资产、可重复测试脚本、结果一致性校验和浏览器自动清理能力。

**Architecture:** Element Map 使用 YAML 模块作为机器可读事实源，Memory 使用带固定章节的 Markdown 长期知识，Version 测试脚本通过 BrowserSession 上下文管理器运行。asset_audit 增加 System 级资产和测试执行完整性校验，workflow 文档与模板作为 Agent 的行为约束。

**Tech Stack:** Python 3.11、PyYAML、Pydantic v2、Playwright、pytest、Ruff、Markdown/YAML。

## Global Constraints

- Markdown / YAML 是唯一事实来源；真实业务资产只写入 `projects/`。
- 不保存密码、Token、Cookie、Storage State 或具体登录账号。
- 正式测试统一使用 Google Chrome 和全新隔离会话。
- 用户未明确要求时不执行 Git 操作。
- PASS 只能表示完整执行且结果符合预期；部分执行必须 BLOCKED。

---

### Task 1: 增加结构化资产和执行覆盖的失败测试

**Files:**
- Modify: `tests/test_asset_audit.py`
- Modify: `tests/test_test_cases.py`

- [x] 增加 Element Map YAML 合法/非法结构审计测试。
- [x] 增加 Memory 固定章节缺失审计测试。
- [x] 增加 `执行覆盖：部分` 配 `PASS` 时必须报错的测试。
- [x] 增加 `测试状态：未测试` 配 `PASS` 时必须报错的测试。
- [x] 运行目标测试，确认新增断言先失败后通过。

### Task 2: 实现 System 资产与结果一致性审计

**Files:**
- Modify: `src/agentest/asset_audit.py`
- Modify: `src/agentest/test_cases.py`

- [x] 扩展执行字段，加入 `执行覆盖`，并保留在范围指纹排除列表中。
- [x] 校验 `完整/部分/未执行` 与 `PASS/FAIL/BLOCKED/NOT RUN` 的组合。
- [x] 新增 `audit_system_assets(system_root)`，校验 `element-map/index.yaml`、模块 YAML 和 Memory 固定章节。
- [x] 对 Element Map 检查模块 ID、页面、入口、元素、主定位、稳定性依据、验证 Version、验证视口。
- [x] 对 Memory 检查 `验证 Version`、`长期用途`、`稳定事实` 章节，并拒绝凭据关键词。
- [x] 运行 Task 1 的测试，确认全部通过。

### Task 3: 更新 Element Map / Memory 公共模板和文档

**Files:**
- Create: `workflow/exploration/template-element-map-index.yaml`
- Create: `workflow/exploration/template-element-map-module.yaml`
- Create: `workflow/exploration/template-memory-module.md`
- Modify: `workflow/exploration/requirement.md`
- Modify: `workflow/exploration/prompt.md`
- Modify: `workflow/exploration/template-element-map-directory-requirement.md`
- Modify: `workflow/exploration/template-element-map-index.md`
- Modify: `workflow/exploration/template-modules-directory-requirement.md`
- Modify: `workflow/exploration/template-memory-index.md`
- Modify: `workflow/exploration/template-memory-directory-requirement.md`
- Modify: `workflow/asset-map.md`
- Modify: `README.md`
- Modify: `prd.md`
- Modify: `AGENTS.md`

- [x] 将 YAML Element Map 定义为模块事实源，并保留 Markdown 索引的导航职责。
- [x] 为模块模板补齐入口、页面、元素、定位、稳定性、行为、验证 Version 和视口字段。
- [x] 为 Memory 模板补齐稳定事实章节和一次性信息禁入规则。
- [x] 明确动态数量、账号、UID、临时 class 不得作为定位依据。

### Task 4: 更新 Test Script、测试用例、报告和澄清规则

**Files:**
- Modify: `workflow/testing/prompt.md`
- Modify: `workflow/testing/rules.md`
- Modify: `workflow/testing/requirement.md`
- Modify: `workflow/testing/template-test-script.py`
- Modify: `workflow/testing/template-test-scripts-directory-requirement.md`
- Modify: `workflow/test-cases/prompt.md`
- Modify: `workflow/test-cases/template-test-cases.md`
- Modify: `workflow/reporting/prompt.md`
- Modify: `workflow/reporting/template-report.md`
- Modify: `workflow/README.md`

- [x] 明确测试用例批准后先生成脚本骨架，再调试和执行。
- [x] 要求脚本记录关联 Test Case ID、前置条件、手动登录、运行方式和失败证据。
- [x] 在测试用例模板增加 `执行覆盖`。
- [x] 明确复合测试用例拆分或逐子场景记录，不得用 PASS 覆盖未执行场景。
- [x] 明确需求澄清改变范围时重新确认和重算指纹。
- [x] 明确正式测试结束不询问用户，默认关闭浏览器会话。

### Task 5: 强化 BrowserSession 生命周期测试与实现

**Files:**
- Modify: `src/agentest/browser/session.py`
- Modify: `tests/test_browser_config.py`

- [x] 先增加测试，验证上下文管理器在测试异常时仍关闭 Context、Browser 和 Playwright。
- [x] 运行测试确认新增测试失败或无法证明目标行为。
- [x] 保持关闭操作幂等，确保 Context 关闭异常时仍释放 Browser 和 Playwright。
- [x] 运行浏览器单元测试确认通过。

### Task 6: 完整验证和文档一致性检查

**Files:**
- Modify: `docs/demo.md`
- Modify: `docs/examples/element-map.md`
- Modify: `docs/examples/memory.md`
- Modify: `docs/examples/test-cases.md`
- Modify: `docs/examples/test-script.py`
- Modify: `docs/examples/report.md`

- [x] 更新 Demo 和示例以体现 YAML Element Map、Memory 章节、脚本运行方式和执行覆盖。
- [x] 运行 `pytest -q`。
- [x] 运行 `ruff check src tests`。
- [x] 运行 `ruff format --check src tests`。
- [x] 运行 `python -m compileall src tests`。
- [x] 复核未调用 Git，且改动只发生在当前工作区。
