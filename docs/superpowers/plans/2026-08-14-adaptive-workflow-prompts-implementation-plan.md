# 自适应探索与 Prompt 收敛 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将探索改为由当前需求与既有知识决定的分支，明确用户授权语义，收敛 Prompt 与模板，并把回归定义为当前 Version 全量测试。

**Architecture:** `workflow/requirements` 触发探索决策，按当前 System 的 Memory / Element Map 覆盖度进入 `exploration` 或 `test-cases`。测试用例文件是当前测试范围的唯一文件事实，用户自然语言授权后由 `testing` 重新读取它。静态测试保护这些脚手架约束，`WorkspaceState` 只保留阶段接续职责。

**Tech Stack:** Python 3.13、pytest、Pydantic v2、Markdown。

## Global Constraints

- Markdown / YAML 是唯一事实来源；真实业务资产仅写入 `projects/`。
- 不新增 CLI、数据库、前端、Agent Runtime、LLM SDK 或 Git 自动化。
- 正式测试需要用户明确授权，登录继续由用户手动完成。
- 不执行 Git 操作；本次在当前工作区内完成。

---

### Task 1: 锁定公共脚手架的新行为

**Files:**
- Modify: `tests/test_directory_contracts.py`
- Modify: `tests/test_schemas.py`

**Interfaces:**
- Consumes: 公共 Prompt、模板、示例与 `WorkspaceState`。
- Produces: 对探索决策、测试用例授权语义和全量回归语义的自动化保护。

- [ ] **Step 1: 写入失败的工作流一致性测试**

  在 `test_directory_contracts.py` 新增测试，读取相关 Markdown 并断言：

  ```python
  assert "探索决策" in requirements_prompt
  assert "复用已有知识" in exploration_prompt
  assert "当前 Version 的完整测试用例集合" in regression_prompt
  assert "状态：Draft" not in test_cases_template
  assert "状态：Draft" not in test_cases_prompt
  ```

- [ ] **Step 2: 写入失败的 WorkspaceState 测试**

  在 `test_schemas.py` 导入 `WorkspaceState`，断言序列化结果只有阶段、上下文、待办问题和浏览器偏好，不包含独立授权标记：

  ```python
  state = WorkspaceState()
  assert "test_cases_approved" not in state.model_dump()
  ```

- [ ] **Step 3: 运行定向测试并确认失败原因正确**

  运行：`python -m pytest tests/test_directory_contracts.py tests/test_schemas.py -q`。

  预期：因旧的直接测试用例跳转、`Draft` 标记、旧回归描述及 `test_cases_approved` 字段失败。

### Task 2: 实现探索决策与当前 Version 全量回归

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `prd.md`
- Modify: `workflow/README.md`
- Modify: `workflow/intake/prompt.md`
- Modify: `workflow/requirements/prompt.md`
- Modify: `workflow/exploration/requirement.md`
- Modify: `workflow/exploration/prompt.md`
- Modify: `workflow/regression/requirement.md`
- Modify: `workflow/regression/prompt.md`
- Modify: `workflow/reporting/prompt.md`
- Modify: `workflow/reporting/template-report.md`

**Interfaces:**
- Consumes: 当前 Version 结构化需求、System Memory 与 Element Map 索引。
- Produces: 复用、目标探索或必须探索的明确分支；当前 Version 的完整回归范围。

- [ ] **Step 1: 更新全局路由与用户文档**

  将固定的“需求整理 → 系统探索 → 测试用例”表述替换为“需求整理 → 探索决策 → 按需探索 → 测试用例”，说明探索不是新增阶段且不属于正式测试。

- [ ] **Step 2: 在探索 Prompt 定义三个决策结果**

  明确复用已有知识、目标探索和必须探索的判定依据、允许行为、写入范围与移交规则；要求在测试用例范围中记录决策与依据。

- [ ] **Step 3: 让 intake 与 requirements 路由到决策结果**

  `intake` 通过 `requirements` 后进入探索决策；`requirements` 不再无条件跳转 `test-cases`，而是读取相关索引后进入 `exploration` 或 `test-cases`。

- [ ] **Step 4: 将回归范围改为当前 Version 全量集合**

  `regression` 与报告 Prompt / 模板声明：回归执行当前 Version 最终 `test-cases.md` 的完整集合；本次结果独立统计，历史结果仅供比较。

### Task 3: 收敛测试用例授权与 Prompt 模板职责

**Files:**
- Modify: `.agentest/requirement.md`
- Modify: `src/agentest/schemas/workspace.py`
- Modify: `workflow/test-cases/prompt.md`
- Modify: `workflow/test-cases/template-test-cases.md`
- Modify: `workflow/test-cases/template-directory-requirement.md`
- Modify: `workflow/testing/prompt.md`
- Modify: `workflow/testing/rules.md`
- Modify: `docs/examples/test-cases.md`
- Modify: `docs/examples/report.md`

**Interfaces:**
- Consumes: 用户明确自然语言授权与当前 Version 的完整测试用例文件。
- Produces: 无 `Draft` / `Approved` 伪状态的测试用例；只表示工作阶段的 `WorkspaceState`；报告中的当前 Version 全量回归说明。

- [ ] **Step 1: 删除独立批准状态与过期 Draft 文本**

  移除 `WorkspaceState.test_cases_approved`，并从测试用例 Prompt、模板和 Demo 中移除文档级与单测试用例级的 `状态：Draft`。

- [ ] **Step 2: 删除 Prompt 内嵌测试用例模板**

  保留 `template-test-cases.md` 作为唯一完整模板；`test-cases/prompt.md` 改为引用它并只保留阶段执行规则。

- [ ] **Step 3: 统一测试用例、测试与报告的授权表述**

  明确用户一句话授权后，`testing` 在执行前重新读取当前文件，严格按最终文件测试；报告只记录结果，不反写测试用例批准状态。

- [ ] **Step 4: 运行定向测试并确认通过**

  运行：`python -m pytest tests/test_directory_contracts.py tests/test_schemas.py -q`。

### Task 4: 校验与收尾

**Files:**
- Verify: `tests/`
- Verify: `workflow/`
- Verify: `src/agentest/schemas/workspace.py`

- [ ] **Step 1: 运行完整测试套件**

  运行：`python -m pytest -q`。

- [ ] **Step 2: 运行静态检查**

  运行：`python -m ruff check src tests`。

- [ ] **Step 3: 扫描过期语义与重复模板**

  运行：`rg -n "test_cases_approved|状态：Draft|按相关测试用例进行回归" AGENTS.md README.md prd.md docs workflow src tests`。

  预期：无生产脚手架中的过期授权或回归语义；`状态：Draft` 与 `test_cases_approved` 不再出现。

## Plan Review

- 覆盖检查：四项任务分别覆盖探索决策、用户授权、Prompt/模板收敛、当前 Version 全量回归及验证。
- 一致性检查：所有阶段仍以 `AGENTS.md` 的安全规则为准；未引入新的运行时能力或 Git 操作。
- 范围检查：只调整公共脚手架、示例、状态 schema 与对应静态测试。
