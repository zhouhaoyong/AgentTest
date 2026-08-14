# 上下文提问分层改造实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 调整 AgentTest 公共脚手架，使首轮只确认最小测试上下文，ID 由 Agent 建议生成，角色/账号/测试数据按需求后置确认。

**Architecture:** 不新增运行时能力，继续由 Markdown/YAML 作为唯一事实来源。通过阶段 Prompt 明确上下文、需求澄清和正式测试的边界，并用静态契约测试保护首轮提问和凭据规则。

**Tech Stack:** Markdown、Python pytest、现有 AgentTest 工作流资产。

## Global Constraints

- 用户对话和 `projects/` 叙述性资产默认使用简体中文。
- ID 只作为目录安全、稳定关联标识，不是业务用户 ID、英文名或 Git 分支名。
- 不索要、保存或自动填写密码、Token、Cookie、Storage State。
- 不执行 Git 操作；提交、切换测试分支和合并由用户执行。
- 不修改 Project / System / Version Schema、测试点审批、浏览器测试和报告格式。

---

### Task 1: 锁定首轮提问和后置准备的失败契约

**Files:**
- Modify: `tests/test_directory_contracts.py`
- Test: `tests/test_directory_contracts.py`

- [ ] **Step 1: 写出失败测试**

新增两个静态契约测试：

```python
def test_context_prompt_asks_for_business_context_and_agent_generated_ids() -> None:
    content = (root / "workflow" / "context" / "prompt.md").read_text(encoding="utf-8")
assert "用户只需提供业务可读名称" in content
assert "Agent 根据名称生成目录安全 ID" in content
assert "测试账号" in content
assert "不是通用的上下文问题" in content


def test_requirements_prompt_defers_roles_accounts_and_data_until_relevant() -> None:
    content = (root / "workflow" / "requirements" / "prompt.md").read_text(encoding="utf-8")
    assert "只有需求涉及登录、角色、权限或数据隔离时" in content
    assert "不索要密码、Token、Cookie 或 Storage State" in content
```

- [ ] **Step 2: 运行聚焦测试，确认按预期失败**

运行：

```text
pytest tests/test_directory_contracts.py -k "context_prompt or requirements_prompt_defers" -q
```

预期：失败，因为现有 Prompt 尚未包含新的提问分层契约。

### Task 2: 修改上下文和需求阶段 Prompt

**Files:**
- Modify: `workflow/context/prompt.md`
- Modify: `workflow/requirements/prompt.md`
- Modify: `workflow/intake/prompt.md`

- [ ] **Step 1: 调整上下文 Prompt**

在上下文决策中明确首轮只询问 Project、System、Version、测试地址、原始需求来源和必要的联动范围；明确用户提供中文或业务可读名称，Agent 生成并展示目录安全 ID 映射；明确不在此阶段通用询问账号、角色和具体业务测试数据。

- [ ] **Step 2: 调整需求 Prompt**

在需求审查后增加条件分支：只有需求涉及登录、角色、权限、数据范围、数据隔离或多账号流程时，才确认角色覆盖、账号可用性和数据前置条件；禁止索要凭据；不得自行编造具体业务数据。

- [ ] **Step 3: 调整 intake Prompt**

让原始需求入口明确上下文阶段只收集最小信息，并将权限、账号和数据问题交给需求整理阶段按需判断。

- [ ] **Step 4: 运行新增聚焦测试**

运行：

```text
pytest tests/test_directory_contracts.py -k "context_prompt or requirements_prompt_defers" -q
```

预期：新增测试通过。

### Task 3: 同步全局规则、用户文档和设计说明

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `prd.md`
- Modify: `docs/superpowers/specs/2026-08-14-context-questioning-design.md`

- [ ] **Step 1: 更新全局上下文确认规则**

说明 Project/System/Version 的业务名称优先，ID 可由 Agent 生成并待用户确认；角色、权限、账号和业务数据仅在需求相关时后置确认。

- [ ] **Step 2: 更新用户使用说明和产品规范**

将首轮示例改为“项目名称、系统、版本、测试地址、需求来源”，移除用户必须提供英文 ID 或首轮测试账号的暗示，并保留 ID 的目录安全用途说明。

- [ ] **Step 3: 检查设计文档与实现契约一致**

确认设计文档没有未实现的行为描述，也没有把账号或角色变成通用首轮问题。

### Task 4: 完整验证

**Files:**
- Test: `tests/test_directory_contracts.py`
- Test: `tests/`

- [ ] **Step 1: 运行完整 pytest**

运行：`pytest -q`

- [ ] **Step 2: 运行 Ruff**

运行：`ruff check src tests`

- [ ] **Step 3: 搜索过期提问措辞**

运行：

```text
rg -n -S "Project 名称及 ID|System 名称、ID|测试账号角色|英文名|用户提供.*ID" AGENTS.md README.md prd.md workflow docs
```

确认没有把用户必须提供英文 ID、账号或角色作为首轮上下文要求的残留表述；Schema 和示例中的结构化 `id` 字段不属于过期提问措辞。
