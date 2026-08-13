# AgentTest v0.1 产品需求与实现规范

## 1. 产品定位

AgentTest 是一个面向现成 AI Agent 的轻量 Web 测试脚手架。

它不实现新的 Agent，而是通过本地 Markdown / YAML 文件沉淀测试资产，让 Codex、Claude Code 或其他 Agent 能够在真实业务项目中持续完成：

```text
原始需求 → 需求整理 → 可选分析 → 系统探索 → 测试点 → 人工审核
→ 正式测试 → Bug / Result / Report → 更新 Element Map / Memory
```

核心目标：

1. 轻量，容易安装和理解。
2. 测试资产可以长期积累，并可通过 Git 查看差异和历史。
3. 让现成 Agent 能够接手需求、探索系统并执行自动化测试。

Agent 是主要使用入口。用户可以只提供原始需求，由 Agent 反问并确认项目上下文后直接创建或定位资产；也可以主动使用 CLI 创建标准资产。CLI 是可选的规范化辅助工具，不是 Agent 接手项目或执行测试的强制前置步骤。

---

## 2. 当前版本范围

### 2.1 必须实现

- Python CLI：`doctor`、`create-project`、`create-system`、`create-version`。
- Project / System / Version 的目录脚手架。
- Pydantic v2 YAML Schema 校验。
- Python Playwright 薄封装，作为 Agent 没有可用浏览器时的标准兜底能力。
- 环境检查，包括 Python、依赖、Playwright、Chromium 和 `projects/` 写入能力。
- Markdown / YAML 模板和完整的项目规则文档。
- pytest 测试和 Ruff 配置。
- 一个极小的 Demo Project，帮助 Agent 和人理解资产结构。
- 根目录和主要资产目录使用 `requirement.md` 作为目录契约，约束目录职责、允许内容、文件职责、更新规则和禁止事项。
- 目录契约、README、docs 和模板等说明性 Markdown 文档统一使用中文；代码、CLI 命令、Schema 字段、资产固定文件名和 ID 保持约定的英文形式。

### 2.2 明确不实现

以下内容不属于 v0.1：

- 前端、Dashboard、用户系统、权限管理产品。
- 数据库、ORM、远程服务、复杂任务调度器。
- 自研 Agent Runtime、LLM Provider 封装或 OpenAI / Anthropic / Gemini SDK 集成。
- 复杂 RAG、向量数据库或复杂 Memory Engine。
- API、Mobile、Desktop Runner；v0.1 只提供 Web 测试的 Playwright 兜底能力。
- Git 自动化，包括自动创建分支、checkout、switch、commit、push、pull、merge、rebase、reset 或 stash。
- 自动上传文件、自动填写账号密码、凭据管理或 Credential Vault。
- 复杂抽象层，例如 plugin system、event bus、service container、repository pattern 或 DI framework。

“不实现权限系统”只表示 AgentTest 不提供用户、角色或权限管理产品；Agent 仍然必须在测试被测系统时验证角色、权限、数据可见性、操作限制和越权风险。

遵循 YAGNI：优先选择更轻、更直接、更容易让 Agent 理解和让用户查看 Git Diff 的方案。

---

## 3. 技术栈与仓库结构

### 3.1 技术栈

- Python `>= 3.13`
- uv
- Typer
- Pydantic v2
- PyYAML
- Playwright Python
- pytest
- Ruff

不要引入其他重量级框架或运行时依赖。

### 3.2 推荐结构

```text
AgentTest/
├── AGENTS.md
├── README.md
├── requirement.md
├── pyproject.toml
├── .gitignore
├── .python-version
├── docs/
│   ├── requirement.md
│   ├── architecture.md
│   ├── workflow.md
│   ├── asset-spec.md
│   ├── testing-rules.md
│   └── examples/demo-project/
├── src/agentest/
│   ├── __init__.py
│   ├── cli.py
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── doctor.py
│   ├── scaffold/
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── system.py
│   │   └── version.py
│   └── schemas/
│       ├── __init__.py
│       ├── project.py
│       ├── system.py
│       └── version.py
├── templates/
│   ├── requirement.md
│   ├── project.yaml
│   ├── system.yaml
│   ├── version.yaml
│   ├── analysis.md
│   ├── test-points.md
│   ├── bugs.md
│   ├── result.md
│   ├── report.md
│   ├── element-map-index.md
│   └── memory-index.md
├── projects/
│   ├── requirement.md
│   └── .gitkeep
└── tests/
    ├── requirement.md
    ├── test_scaffold_project.py
    ├── test_scaffold_system.py
    ├── test_scaffold_version.py
    ├── test_schemas.py
    └── test_browser_config.py
```

允许按照 Python 工程习惯做小幅调整，但不得改变产品边界和核心资产模型。

### 3.3 目录契约

`requirement.md` 是目录契约文件，不是普通说明文档。根目录和主要目录必须有自己的 `requirement.md`，至少包括：

- 目录职责（Purpose）：目录负责什么。
- 允许内容（Allowed Contents）：允许哪些文件和子目录。
- 文件职责（File Responsibilities）：文件分别负责什么。
- 更新规则（Update Rules）：谁可以在什么场景下修改。
- 禁止事项（Prohibited）：禁止放什么、禁止做什么。
- 阅读策略（Read Strategy）：Agent 应先读什么，再按需读什么。

目录契约适用于：仓库根目录、`docs/` 及其示例目录、`src/`、`src/agentest/` 及其代码子目录、`templates/`、`projects/`、`tests/`、Project 目录、System 目录、System 的 `element-map/`、`memory/`、`versions/` 和 Version 目录。没有业务文件的目录也必须保留 `requirement.md` 或其他明确占位文件，不能依靠空目录表达结构。

业务 Version 的 `requirements/requirement.md` 同时承担“需求目录契约”和“结构化业务需求”职责；其他目录的 `requirement.md` 只承担目录契约职责。叶子资产目录可以继承最近父级的目录契约，不要求为每一个结果文件单独创建契约文件。

### 3.4 文件命名规则

- 目录契约固定命名为 `requirement.md`；仓库根目录的用户指南仍使用 `README.md`，两者职责不同。
- Project、System、Version 配置固定命名为 `project.yaml`、`system.yaml`、`version.yaml`。
- Version 资产固定命名为 `source.md`、`requirement.md`、`analysis.md`、`test-points.md`、`result.md`、`bugs.md`、`report.md`。
- Element Map / Memory 模块文件使用小写英文和连字符，例如 `contact-list.yaml`、`permission.md`，文件名应与模块 ID 对应。
- Python 源码和测试文件使用 `snake_case`，测试文件使用 `test_<subject>.py`。
- 不使用同义重复文件名，不用日期或随机数替代稳定资产名称；历史由 Git 保留。

---

## 4. 资产模型

### 4.1 层级关系

```text
Project
└── System
    └── Version
```

- `projects/` 下可以有多个 Project。
- 一个 Project 可以有多个 System。
- 一个 System 可以有多个 Version。
- System ID 在所属 Project 内唯一。
- Version ID 在所属 System 内唯一。
- Version 是文件夹，不是 Git 分支。
- System 和 Version 不对应 Git 分支；业务测试分支仅是用户自行管理的工作方式。
- 不强制 SemVer。

Project、System、Version ID 都必须是非空目录安全字符串，建议使用：

```regex
^[A-Za-z0-9._-]+$
```

允许的 Version 示例：`v1.2.3`、`2026.08`、`R15`、`Sprint-20`、`release-0812`。

### 4.2 Project

路径：`projects/<project_id>/project.yaml`

最小内容：

```yaml
id: contact-platform
name: 通讯录平台
description: ""
```

Schema 至少验证：

- `id` 非空且符合目录安全规则。
- `name` 非空。
- `description` 可以为空。

### 4.3 System

路径：`projects/<project_id>/systems/<system_id>/system.yaml`

最小内容：

```yaml
id: contact-web
name: 通讯录 Web
type: web
base_url: https://test.example.com
description: ""
```

规则：

- v0.1 主要支持 `type: web`。
- Schema 可以保留普通字符串 `type`，但不实现其他类型的 Runner。
- `base_url` 可以为空，测试地址可以由用户在 Agent 交互中临时提供。
- System ID 在 Project 内重复时必须拒绝创建。

### 4.4 Version

路径：`projects/<project_id>/systems/<system_id>/versions/<version_id>/version.yaml`

最小内容：

```yaml
id: v0.0.1
name: v0.0.1
test_url: ""
description: ""
```

规则：

- Version ID 在当前 System 内重复时必须拒绝创建。
- `test_url` 可以为空，并覆盖 `system.yaml` 的 `base_url`。
- 如果两个地址都有，Version 的 `test_url` 优先。
- 不实现复杂发布状态机。

### 4.5 Version 资产结构

创建 Version 时必须生成：

```text
versions/<version_id>/
├── version.yaml
├── requirement.md
├── requirements/
│   ├── source.md
│   ├── requirement.md
│   └── attachments/
│       └── requirement.md
├── analysis/
│   ├── analysis.md
│   └── requirement.md
├── test-points/
│   ├── test-points.md
│   └── requirement.md
├── run/
│   ├── result.md
│   └── requirement.md
├── bugs/
│   ├── bugs.md
│   └── requirement.md
└── report/
    ├── report.md
    └── requirement.md
```

`run/result.md` 和 `report/report.md` 表示当前 Version 最近一次正式测试的结果，不要求 v0.1 保存独立的 `run-001`、`run-002` 历史目录；Git 历史负责保留文件变化。

---

## 5. Agent 工作流

完整工作流必须写入根目录 `AGENTS.md`，并在 `docs/workflow.md` 中展开说明。

### Phase 1：接收原始需求并确认上下文

用户可能只提供一段原始需求，也可能同时提供 Project、System、Version、测试地址或附件。

Agent 必须：

1. 识别已知信息和缺失信息。
2. 对缺失的 Project、System、Version、测试地址或需求来源进行必要反问。
3. 不在关键上下文不明确时默默编造正式资产信息。
4. 确认后定位或创建 Project、System 和 Version。
5. 校验 ID 唯一性。
6. 保存或登记原始 Requirement Source。
7. 先读取相关 System 的 `memory/index.md` 和 `element-map/index.md`。
8. 根据索引判断需要哪些模块，只读取相关模块文件；禁止默认加载整个 Memory 或 Element Map。

Agent 可以直接按标准目录和模板创建资产，不要求用户先执行 CLI。若目标资产已存在，Agent 必须先读取并判断是继续编辑、创建新 Version，还是请求用户确认，不得静默覆盖。

### Phase 2：需求整理

Agent 生成或更新：

- `requirements/source.md`：记录原始文本、链接和附件路径。
- `requirements/requirement.md`：结构化需求。

需求来源可能是文本、Markdown、HTML、URL、图片、PDF、Word、Excel、视频、原型、API 文档或多种来源组合。AgentTest 不要求为每种格式实现 Parser；用户提供什么就保存或登记什么，是否能理解由当前 Agent 能力决定。

`requirement.md` 应保持稳定章节和 Requirement ID：

```markdown
# Requirement
## Metadata
- Project:
- System:
- Version:
- Status: Draft
## Background
## Goal
## Scope
## Functional Requirements
### REQ-001
## Business Rules
## Constraints
## Open Questions
```

### Phase 3：可选需求分析

简单需求可以不生成有效分析，复杂需求才需要更新 `analysis/analysis.md`。建议章节：

```markdown
# Requirement Analysis
## Key Flows
## Boundary Conditions
## Permissions / Roles
## Dependencies
## Risks
## Ambiguities
## Suggested Test Focus
```

### Phase 4：系统探索

在生成测试点前，Agent 可以探索目标系统，以理解页面、业务路径、相关模块和关键元素。探索不是正式测试。

浏览器优先级：

1. 当前 Agent 已内置的浏览器能力。
2. AgentTest 的 Python Playwright helper。
3. Playwright MCP 只能作为用户同意后的可选增强，不能成为核心依赖。

探索阶段可以按需更新 System 级 Element Map / Memory，但只记录有长期复用价值的信息。

### Phase 5：生成测试点并停止

Agent 基于 Requirement、可选 Analysis、探索结果、相关 Memory 和 Element Map 生成：

```text
test-points/test-points.md
```

每个测试点必须有稳定 ID，例如 `TP-001`，并包含优先级、关联 Requirement、前置条件、步骤和预期结果。

```markdown
# Test Points
Status: Draft
---
## TP-001 正常添加联系人
- Priority: P0
- Requirement: REQ-001
- Status: Draft
### Preconditions
- ...
### Steps
1. ...
### Expected
- ...
```

生成测试点后必须停止，等待用户审核。用户可以直接修改、删除、增加测试点或调整优先级。

### Phase 6：人工审核 Gate

只有用户明确表达以下含义之一，Agent 才能进入正式测试：

- 测试点确认。
- 测试点没问题。
- 可以开始测试。
- 开始测试。
- 按照这些测试点执行。

“看看”“继续分析”“优化一下”“还有没有遗漏”等不视为批准。未经明确批准，禁止正式测试。

### Phase 7：正式测试

Agent 必须按 Approved Test Points 执行，不擅自扩大到与需求无关的大范围测试。若需求涉及多角色、多权限或关键业务流，不能只验证单个页面的表面功能后宣称完成。

正式测试应根据实际需求覆盖以下维度：

#### 功能

- 核心功能和正常路径。
- 正常、边界和非法输入。
- 校验规则、错误提示和异常处理。
- 状态变化、数据保存、结果展示和持久性。

#### 业务流

- 业务起点和前置条件。
- 主流程和关键分支。
- 成功路径和失败路径。
- 跨页面 / 跨模块衔接。
- 流程中断、恢复和后置结果。

#### 权限与角色

- 不同角色的页面和数据可见性。
- 操作可用性和数据范围。
- 角色之间的数据隔离。
- 受限功能的直接访问。
- 越权操作和越权数据访问。

不要求无关需求机械覆盖所有维度，但 Agent 必须在测试点或分析中说明判断结果。未覆盖、未执行或被阻塞的维度必须记录原因。

多账号或多角色测试必须使用隔离的 Browser Context / Session；不得通过复用未清理会话、切换文字或假设结果代替验证。

测试执行规则：

1. 优先使用 Agent 内置浏览器，否则使用 Python Playwright。
2. Python Playwright 默认 `headless=False`，让用户看到测试过程。
3. 目标系统需要登录时，暂停后续操作并提示用户手动登录。
4. 用户明确确认登录完成后，才能继续。
5. 不保存密码，不自动填写凭据，不实现账号管理。
6. 记录每个 Test Point 的 PASS / FAIL / BLOCKED / NOT RUN 结果和说明。
7. 发现功能缺陷、业务流阻断、权限绕过或数据越权时，记录 Bug 或风险，并关联测试点、测试维度和复现信息。

### Phase 8：测试结束

更新：

```text
run/result.md
bugs/bugs.md
report/report.md
```

根据长期复用价值按需更新：

```text
system/element-map/
system/memory/
```

最后向用户说明测试结果、Bug 数量、主要风险、未覆盖内容和更新的资产。不要自动执行 Git 操作。

---

## 6. 测试资产规范

### 6.1 Element Map

Element Map 属于 System，不属于 Version，不为每个 Version 复制。

```text
element-map/
├── index.md
└── modules/
    ├── contact-list.yaml
    └── add-contact.yaml
```

`index.md` 必须简短，只列模块、文件路径和一句话用途。模块文件只记录测试真正用到、未来大概率复用或有助于 Agent 理解系统的元素，不记录全部 DOM。

模块内容可以包括：模块名、页面、URL pattern、元素 ID、语义和 locator 策略。

读取策略：先读 `index.md`，判断相关模块，再按需读取模块文件。

### 6.2 System Memory

Memory 属于 System，不同 System 独立，不为每个 Version 完整复制。

```text
memory/
├── index.md
└── modules/
    ├── contact.md
    └── permission.md
```

只记录长期稳定的业务规则、系统行为、常用前置关系、已验证的重要规律、长期测试经验和模块关系。

不要记录一次性聊天、临时推理、流水账、完整思考过程或当前 Session 的全部操作。

读取策略与 Element Map 相同：先读索引，再按需读取模块。

### 6.3 Bug List

路径：`bugs/bugs.md`。只记录当前 Version 最近一次正式测试发现的问题。

每个 Bug 应有稳定 ID，并至少包含严重程度、关联 Test Point、状态、复现步骤、实际结果、预期结果和备注。

```markdown
# Bugs
## BUG-001 添加联系人失败
- Severity: Major
- Related Test Point: TP-003
- Test Dimension: Functional
- Status: Open
### Steps
1. ...
### Actual
...
### Expected
...
### Notes
...
```

### 6.4 Test Result

路径：`run/result.md`。记录当前 Version 最近一次正式测试的详细结果：

```markdown
# Test Result
## Summary
- Passed:
- Failed:
- Blocked:
- Not Run:
## Results
### TP-001
- Result: PASS
- Notes:
```

### 6.5 Test Report

路径：`report/report.md`。记录当前 Version 最近一次正式测试的简洁汇总：

```markdown
# Test Report
## Scope
## Overall Result
## Test Point Summary
## Bug Summary
## Not Tested
## Risks
## Conclusion
```

---

## 7. CLI 规范

CLI 是可选辅助工具，不是主要测试交互入口。

Agent 和 CLI 创建资产时必须遵循同一套 ID 规则、Schema、模板、目录结构和防覆盖规则。

### 7.1 `AgentTest doctor`

检查：

- Python 是否满足 3.13+。
- AgentTest 依赖是否可导入。
- Playwright Python 是否可导入。
- Chromium 是否已安装。
- Chromium 是否能启动。
- `projects/` 是否可写。

Chromium 未安装时只提示：

```bash
uv run playwright install chromium
```

不得自动下载或安装浏览器。

### 7.2 `AgentTest create-project`

示例：

```bash
AgentTest create-project contact-platform --name "通讯录平台"
```

创建 `projects/contact-platform/project.yaml` 和 `systems/`。目标已存在时拒绝并返回清晰错误，不覆盖任何文件。

### 7.3 `AgentTest create-system`

示例：

```bash
AgentTest create-system contact-platform contact-web --name "通讯录 Web"
```

创建 `system.yaml`、`element-map/index.md`、`element-map/modules/`、`memory/index.md`、`memory/modules/` 和 `versions/`。Project 不存在或 System ID 重复时拒绝创建。

### 7.4 `AgentTest create-version`

示例：

```bash
AgentTest create-version contact-platform contact-web v0.0.1
```

创建第 4.5 节定义的完整 Version 模板。Project / System 不存在、Version ID 非法或 Version 已存在时拒绝创建，不覆盖已有数据。

---

## 8. Browser Helper 规范

实现一个薄的 `BrowserSession`，不重新封装 Playwright 的全部 API：

```python
class BrowserSession:
    def __init__(self, headless: bool = False, slow_mo: int = 0) -> None: ...
    def start(self) -> "BrowserSession": ...
    def new_page(self): ...
    def goto(self, url: str): ...
    def close(self) -> None: ...
```

应支持上下文管理器：

```python
with BrowserSession(headless=False) as browser:
    page = browser.new_page()
    page.goto("http://localhost:3000")
```

要求：

- 默认 `headless` 必须为 `False`。
- 显式传入 `headless=True` 时使用无头模式。
- 支持 `slow_mo`。
- Agent 可以直接使用原生 Playwright Page 对象。
- 多角色测试优先创建独立 Browser Context。

---

## 9. 安全与 Git 约束

AgentTest 可能运行在真实测试环境，必须遵守：

- 不自动删除项目资产。
- 不覆盖已有 Project / System / Version。
- 不自动上传文件。
- 不自动填写账号密码。
- 不自动扩大测试范围。
- 未经用户批准的 Test Points 不得正式测试。
- 未经用户明确指令不得执行任何 Git 命令。
- 不自动创建分支、commit、push、merge 或其他 Git 历史操作。
- 用户可以自行选择业务测试分支，推荐命名为 `feature/<project_name>`；System / Version 不是分支。

---

## 10. 文档要求

必须创建：

- `AGENTS.md`：短而强约束，说明 Agent 工作流、人工 Gate、浏览器登录、功能/业务流/权限测试、资产读取策略和 Git 禁止事项。
- `requirement.md`：根目录契约，约束仓库目录和文件职责；主要子目录也必须有对应的目录契约。
- `README.md`：面向实际用户，说明定位、安装、CLI、Agent 使用方式和测试资产。
- `docs/architecture.md`：Agent、规则、资产、Playwright 的关系。
- `docs/workflow.md`：完整工作流。
- `docs/asset-spec.md`：每种资产的位置、层级、更新者和生命周期。
- `docs/testing-rules.md`：测试点 Gate、功能/业务流/权限测试、headed 默认、手工登录、会话隔离和范围约束。
- `docs/examples/demo-project/`：极小示例，不用于正式测试。

`AGENTS.md` 不应重复整份 PRD，也不应写成百科全书；它只保留 Agent 每次接手时必须执行的规则。

---

## 11. 测试与验收标准

### 11.1 Scaffold

pytest 至少覆盖：

- 能创建 Project。
- 重复 Project 被拒绝且不覆盖。
- 能创建 System。
- 同 Project 重复 System ID 被拒绝。
- 能创建 Version。
- 同 System 重复 Version ID 被拒绝。
- 不同 System 可以存在相同 Version ID。
- 非法 Project / System / Version ID 被拒绝。
- 创建失败时不留下部分覆盖的已有资产。

### 11.2 Schema

- 合法 Project YAML 可验证。
- 合法 System YAML 可验证。
- 合法 Version YAML 可验证。
- 缺少必填字段、空名称或非法 ID 时验证失败。
- `base_url`、`test_url` 和 `description` 可以为空，符合各自规则。

### 11.3 Browser

- `BrowserSession().headless is False`。
- 显式 `headless=True` 生效。
- `slow_mo` 可配置。
- 上下文管理器会启动并关闭资源；不能要求测试环境必须已经安装 Chromium 才能通过配置测试。

### 11.4 Architecture Guard

依赖和源码静态检查不得引入：

- FastAPI
- SQLAlchemy
- MySQL Driver
- SQLite ORM
- OpenAI SDK
- Anthropic SDK
- LangChain
- LlamaIndex

### 11.5 Agent 测试覆盖

当需求涉及相应内容时，测试点和正式测试必须覆盖：

- 功能正确性、边界行为和异常行为。
- 完整业务流、关键分支和流程衔接。
- 角色、权限、数据可见性、操作限制和越权风险。

不同角色必须使用隔离会话。没有覆盖的维度必须说明原因；如果只执行页面可见性或单个操作，不能宣称整个需求已完成正式测试。

### 11.6 验收场景

#### Scenario A：创建 Project

```bash
uv run AgentTest create-project contact-platform --name "通讯录平台"
```

成功生成：

```text
projects/contact-platform/project.yaml
projects/contact-platform/systems/
```

#### Scenario B：创建 System

```bash
uv run AgentTest create-system contact-platform contact-web --name "通讯录 Web"
```

成功生成：

```text
projects/contact-platform/systems/contact-web/system.yaml
projects/contact-platform/systems/contact-web/element-map/index.md
projects/contact-platform/systems/contact-web/element-map/modules/
projects/contact-platform/systems/contact-web/memory/index.md
projects/contact-platform/systems/contact-web/memory/modules/
projects/contact-platform/systems/contact-web/versions/
```

#### Scenario C：创建 Version

```bash
uv run AgentTest create-version contact-platform contact-web v0.0.1
```

成功生成第 4.5 节列出的所有文件和目录。

#### Scenario D：拒绝重复 Version

再次执行同一命令时返回明确错误，不覆盖已有数据。

#### Scenario E：Browser

以下代码可用，且默认以 headed 模式启动：

```python
with BrowserSession(headless=False) as browser:
    page = browser.new_page()
    page.goto("http://localhost:3000")
```

#### Scenario F：Agent 接手原始需求

Agent 读到 `AGENTS.md` 后应知道：用户不必先执行 CLI；当用户只提供原始需求时，应先确认 Project、System、Version、测试地址和需求来源，再创建或定位资产。

#### Scenario G：Agent 测试阶段

Agent 应遵循：

```text
识别需求范围
↓
覆盖功能、业务流、权限 / 角色
↓
生成测试点
↓
停止并等待人工批准
↓
按批准的测试点和隔离会话执行
↓
记录结果、Bug、风险和未覆盖原因
```

---

## 12. README 必须说明

README 至少包含：

### AgentTest 是什么

> AgentTest 是一个面向现成 AI Agent 的轻量测试脚手架，通过结构化文件和 Git 持续沉淀 Project / System / Version 的测试资产，并使用 Python Playwright 支撑 Web 自动化测试。

### 安装

```bash
uv sync
```

### 安装 Chromium

```bash
uv run playwright install chromium
```

### 环境检查

```bash
uv run AgentTest doctor
```

### 创建资产

```bash
uv run AgentTest create-project contact-platform --name "通讯录平台"
uv run AgentTest create-system contact-platform contact-web --name "通讯录 Web"
uv run AgentTest create-version contact-platform contact-web v0.0.1
```

### Agent 使用方式

README 必须说明：

1. 用户不必先使用 CLI。
2. 用户可以直接把原始需求交给 Agent。
3. Agent 应先确认 Project / System / Version / 测试地址和需求来源。
4. 需要登录时由用户手动完成。
5. Agent 生成测试点后必须等待人工审核。
6. 只有明确批准后，Agent 才能正式测试。
7. 正式测试应根据需求覆盖功能、业务流和权限。
8. 查看 `run/`、`bugs/`、`report/`、Element Map 和 Memory 资产。

---

## 13. 实现与最终汇报要求

实现顺序：

1. 检查当前文件，不运行 Git 命令。
2. 创建 v0.1 scaffold。
3. 先写测试，再实现代码。
4. 运行 Ruff。
5. 运行 pytest。
6. 环境允许时运行 `doctor`。
7. Chromium 缺失时只让 doctor 正确提示安装命令，不改变架构。

最终汇报必须包含：

1. 创建的主要文件。
2. 最终目录结构。
3. CLI 命令。
4. 安装和 Chromium 安装方法。
5. `doctor`、Project、System、Version 的使用方式。
6. Agent 开始第一个真实项目的方法。
7. pytest 结果。
8. Ruff 结果。
9. 明确未实现的内容。

禁止自动 commit、创建分支、merge 或 push。
