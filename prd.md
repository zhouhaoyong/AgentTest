# AgentTest v0.1 产品需求与实现规范

## 1. 产品定位

AgentTest 是面向现成 AI Agent 的轻量文件化 Web 测试工作区。它本身不是 Agent，不实现 LLM、任务调度或测试管理后台。

用户可以在 Codex、Claude Desktop、Claude Code CLI、Hermes Agent、Reasonix 或其他能读写本地文件的 Agent 中直接输入需求。Agent 负责需求整理、系统探索、测试用例设计、人工审核、浏览器测试和资产沉淀。

```text
原始需求 → 确认上下文 → 需求审查与用户澄清 → 需求整理 → 探索决策与按需系统探索 → 测试用例
→ 人工审核 → 正式测试 → 脚本 / 建议版报告 → 回归测试
→ 更新 Element Map / Memory
```

核心原则：

- Markdown / YAML 是当前唯一事实来源；Element Map 的结构化事实使用 YAML，Memory 使用固定章节的 Markdown。
- Agent 直接按目录契约和模板读写资产，不提供额外的资产创建命令。
- 不静默覆盖已有资产；已有 System 应复用并创建或选择新的 Version。
- Git 分支由用户自行管理，AgentTest 不执行 Git 操作。

## 2. 当前版本范围

### 2.1 必须实现

- Project / System / Version 的 Pydantic v2 YAML Schema；多端联动为 Version 内的轻量标记（`linked` / `linked_ends`），不再有独立 Integration Scope 资产。
- System 类型：`web`、`h5`、`app`、`miniapp`。
- System / Version 的 Playwright 测试环境配置，包括视口、设备、语言、时区和超时。
- Python Playwright 薄封装：统一用 Playwright 驱动系统 Chrome 的隔离（无痕）会话执行所有业务测试。
- `workflow/` 公共脚手架：按用户流程聚合的 Prompt、模板、目录契约、规则和资产映射。
- Markdown / YAML 模板、目录契约、README、工作流和测试规则。
- `.agentest/context.yaml` 与 `.agentest/state.yaml` 的跨 Agent 状态约定，由 Agent 直接读写。
- 每个 Version 的 `test-scripts/` 和统一的 `report/report.md`；正式测试后 `test-scripts/` 不能为空，并且脚本必须能在手动登录后重复运行当前范围；多个 System 一起测试时，在参与联动的 `version.yaml` 内用轻量标记登记联动关系，各端资产仍写在各自 Version 下。
- 一个平铺、可发现的 Demo：`docs/demo.md` 链接 `docs/examples/` 下的示例文件。
- pytest、Ruff 和架构边界测试。

### 2.2 明确不实现

- 额外的资产创建命令、环境诊断命令或自动生成目录的命令行入口。
- 前端、Dashboard、用户系统、数据库、远程服务和复杂任务调度器。
- 自研 Agent Runtime、LLM Provider、OpenAI / Anthropic SDK 或复杂 Memory Engine。
- 当前版本的 RAG 和向量数据库。未来只把经过筛选的高价值资产作为派生索引；测试报告和测试脚本说明默认不自动向量化。
- Native App / 小程序专用 Runner；`app`、`miniapp` 是系统身份分类，Playwright 驱动的 Chrome 会话主要面向 Web / H5。
- 自动填写账号密码、凭据管理、Credential Vault、Storage State 管理、自动上传文件、自动安装浏览器或自动配置外部浏览器连接。
- Git 自动创建分支、commit、push、pull、merge、rebase、reset、stash 或其他历史操作。
- plugin system、event bus、service container、repository pattern 等复杂抽象。

## 3. 技术栈与仓库结构

### 3.1 技术栈

- Python `>= 3.11`
- Pydantic v2
- PyYAML
- Playwright Python
- pytest
- Ruff

### 3.2 推荐结构

```text
AgentTest/
├── AGENTS.md
├── README.md
├── requirement.md
├── prd.md
├── pyproject.toml
├── workflow/
│   ├── README.md                  # 用户意图路由和工作流入口
│   ├── asset-map.md               # 公共模板到真实资产的映射
│   ├── intake/
│   ├── context/
│   ├── requirements/
│   ├── exploration/
│   ├── test-cases/
│   ├── testing/
│   ├── reporting/
│   └── regression/
├── docs/
│   ├── requirement.md
│   ├── architecture.md
│   ├── demo.md
│   └── examples/
├── src/agentest/
│   ├── __init__.py
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── requirement.md
│   │   └── session.py
│   └── schemas/
│       ├── __init__.py
│       ├── requirement.md
│       ├── common.py
│       ├── project.py
│       ├── system.py
│       ├── version.py
│       └── workspace.py
├── projects/
└── tests/
```

根目录、主要源码目录、文档目录、每个工作流阶段、项目资产目录和测试目录都必须有 `requirement.md` 目录契约。目录契约至少说明职责、允许内容、文件职责、更新规则、禁止事项和阅读策略。

## 4. 资产模型

### 4.1 层级关系

```text
Project
└── System
    ├── system.yaml
    ├── element-map/
    ├── memory/
    └── versions/
        └── Version
            └── version.yaml（含 linked / linked_ends 轻量联动标记）
```

- 一个 Project 可以包含多个 System，一个 System 可以包含多个 Version。多个 System 必须一起验证时，不再新建独立联动目录，而是在参与联动的 `version.yaml` 内用 `linked` / `linked_ends` 登记联动关系；各端资产仍写在各自 Version 下。
- System ID 在 Project 内唯一，Version ID 在 System 内唯一。
- Version 是测试资产目录，不是 Git 分支。
- Project、System、Version ID 必须匹配 `^[A-Za-z0-9._-]+$`。
- `name` 是面向用户的业务名称，`id` 是目录安全的内部关联标识；首轮由用户提供业务可读名称，Agent 根据名称生成 ID 并展示映射确认，不要求用户自行提供英文 ID。

### 4.2 Project

路径：`projects/<project-name>/project.yaml`。

```yaml
id: contact-platform
name: 通讯录平台
description: ""
```

`id` 非空且目录安全，`name` 非空，`description` 可为空。

### 4.3 System

路径：`projects/<project-name>/systems/<system-name>/system.yaml`。

```yaml
id: contact-web
name: 通讯录 Web
type: web
base_url: https://test.example.com
description: ""
test_environment:
  maximize: true          # web 默认真实最大化；viewport 仅作无头/回退尺寸
  viewport:
    width: 1920
    height: 1080
  device_scale_factor: 1
  is_mobile: false
  has_touch: false
  locale: zh-CN
  timezone_id: Asia/Shanghai
  action_timeout_ms: 10000
  navigation_timeout_ms: 30000
  login: manual
```

规则：

- `type` 只能是 `web`、`h5`、`app`、`miniapp`。
- System ID 只需是目录安全串（`^[A-Za-z0-9._-]+$`），系统类型由 `type` 字段承载，不强制在 ID 里带类型后缀；如需区分同业务的不同端，可自行用不同名字，例如 `gumai-pc`、`gumai-h5`。
- `web` 默认真实最大化窗口（`--start-maximized` + `no_viewport`；`viewport` 仅作无头或回退尺寸，默认 `1920x1080`）；`h5`、`app`、`miniapp` 默认使用 `393x852`（iPhone 14 Pro）、移动端标识和触摸能力。默认操作超时为 `10000` 毫秒。所有正式测试统一使用内置隔离浏览器（由 Playwright 驱动系统 Google Chrome 的无痕 / 隔离会话），不再区分"优先 / 其次"两级后端。
- `base_url` 可以为空；登录方式固定为 `manual`。
- YAML、代码和测试产物都不得保存账号、密码、Token、Cookie 或 Storage State。

### 4.4 Version

路径：`projects/<project-name>/systems/<system-name>/versions/<version-name>/version.yaml`。

```yaml
id: v0.0.1
name: v0.0.1
test_url: ""
description: ""
test_environment: null
```

Version 可以在 `test_environment` 中填写本次测试与 System 默认值不同的字段。最终环境继承 System 默认值，再应用 Version 覆盖。测试地址优先级为 Version `test_url`，其次 System `base_url`，两者都为空时必须询问用户。

### 4.5 Version 资产

```text
versions/<version-name>/
├── version.yaml
├── requirement.md
├── requirements/
│   ├── source.md
│   ├── requirement.md
│   ├── YYYYMMDD_V<版本号>_<system-id>.md
│   └── attachments/requirement.md
├── test-cases/test-cases.md
├── test-scripts/
├── evidence/
└── report/report.md
```

`test-scripts/` 保存当前 Version 可重复执行的测试脚本，正式测试开始时先批量生成脚本骨架，结束前实际运行并记录关联 Test Case、前置条件、手动登录方式和运行命令；已确认需求发生变化时应及时调整相关脚本。`evidence/` 保存本次测试的 Bug 证据（截图、Trace、HAR、录像等），报告中的 Bug 以相对路径引用，证据不得包含凭据等敏感信息；`report/report.md` 统一保存最近一次正式测试或回归测试的建议版报告，包含测试用例结果、Bug、风险、未测试内容和测试建议。

### 4.6 多端联动（轻量标记）

多端联动不再使用独立目录或 `scope.yaml`，而是在参与联动的 `version.yaml` 内声明：

- `linked`：布尔值，是否与其他端联动，默认 `false`。
- `linked_ends`：`linked=true` 时至少声明一项，每项用 `system_id`（必填，目录安全 ID）、可选 `version_id`（省略表示引用该系统当前范围内的版本）和可选 `note` 指向另一个端。

联动端只登记"和谁联动"，不复制其地址或环境；被引用端的测试地址仍以其自身 `version.yaml` 为唯一事实源。Schema 只校验 `version.yaml` 自身结构（`linked` 与 `linked_ends` 的一致性、引用 ID 合法且不重复），是否真实存在被引用端由资产校验在读取目录时确认。各端的需求、测试用例、脚本、证据、报告仍写在各自 Version 下，长期 Element Map 和 Memory 保留在各自 System 下。

## 5. Agent 工作流

### 5.1 确认上下文

Agent 首先读取最近的 `requirement.md`、`AGENTS.md`、`prd.md`、Demo 总览，以及 `.agentest/context.yaml` 和 `.agentest/state.yaml`（如果存在）。

首轮先确认基础信息，并根据原始需求列出编号的待确认问题。基础信息包括：

- Project 中文名称。
- System 名称和系统类型；多个 System 一起测试时，确认参与系统、对应 Version、地址和操作顺序。
- Version 名称或版本号；已有 System 不得重建，通常创建新 Version 并按用户要求升版本号。
- 测试地址。
- 原始需求来源。

Agent 根据业务名称生成 Project、System、Version 的内部 ID，并展示映射供用户确认。需求涉及角色、权限、测试账号、业务数据、写操作或边界时，相关问题必须在同一轮以“待确认需求 1、待确认需求 2……”编号提出；没有待确认问题时不展示该区块。

如果用户只提供原始需求，Agent 必须反问缺失的关键上下文，不得自行编造。用户可以直接修改 YAML；Agent 下一次工作以文件内容为准。

### 5.2 整理需求与探索

先保存或登记 `requirements/source.md`，再审查需求的遗漏、矛盾、边界和可测试性；需要时向用户提出问题并给出建议方案。用户澄清后，生成 `requirements/YYYYMMDD_V<版本号>_<system-id>.md`；`requirements/requirement.md` 只作为目录契约。统计、指标或汇总需求还要确认口径、时间范围、筛选条件和可参考的数据来源。

系统探索用于理解页面、业务路径、模块和关键元素，不等于正式测试。需求整理后，Agent 先依据当前需求与 System Memory / Element Map 的覆盖度，选择复用已有知识、目标探索或必须探索；仅在需要时启动浏览器探索。业务期望与当前页面实现必须分开记录；页面没有对应按钮不代表需求无效，页面存在功能也不代表它自动属于本次需求。Agent 可以按需更新 System 级 Element Map / Memory，但只记录长期可复用的信息。

正式测试结束后，继续在同一份结构化需求文档中补充“测试后的实现说明”，但不得覆盖原始需求或未经用户确认改变业务目标或需求范围。

浏览器：全流程统一使用内置隔离浏览器（由 Playwright 驱动系统 Google Chrome 的无痕会话），不再区分"优先 / 其次"两级后端。禁止使用 Edge、Playwright bundled Chromium。禁止复用用户当前已打开的浏览器窗口、Tab、Profile 或地址；必须使用新建的隔离 Chrome 会话。无法确认隔离或没有可用 Chrome 能力时，先询问用户是否需要 Agent 协助安装或启用，未确认前绝不打开用户现有浏览器。每次 Playwright 启动前执行本地环境 pre-flight 检查（操作系统、系统 Chrome、Playwright 可用性等）。

### 5.3 测试用例确认规则

Agent 在当前 Version 的 `test-cases/test-cases.md` 生成测试用例后必须停止。真实业务资产路径是 `projects/<project-name>/systems/<system-name>/versions/<version-name>/test-cases/test-cases.md`；不得在项目根目录直接创建 `test-cases/`。多端联动只在参与联动的 `version.yaml` 用轻量标记登记，不新建独立联动目录。测试用例确认只表示范围获批，只有用户明确说“开始正式测试”或等价表达，才能继续进入正式测试。

测试用例应根据需求评估：

- 功能测试：正常、边界、非法输入、校验、错误、状态、持久化和页面重新进入后的状态。
- 业务流程测试：前置条件、主流程、分支、失败路径、中断恢复、跨页面 / 跨模块衔接和后置结果；业务数据通过页面行为验证其保存、流转或展示，不默认要求直接访问数据库。
- 角色与权限测试：角色可见性、操作权限、数据范围、数据隔离、受限访问和越权风险。

未覆盖或被阻塞的维度必须写明原因。

### 5.4 正式测试与回归

测试用例确认只表示范围获批，不等于正式测试启动；只有用户明确说“开始正式测试”或等价表达后才能打开浏览器。正式测试只执行已批准的 Test Cases，不自动扩大范围。开始后先批量生成脚本并按页面 / 业务流程分组调试定位器和前置数据；正式执行时同组测试用例复用同一个隔离浏览器会话，但仍以测试用例为结果、报告和断点续跑的最小单位。测试用例文件中的每个测试用例同时记录`测试状态`（`未测试` / `已测试`）、`执行覆盖`（`完整` / `部分` / `未执行`）和`测试结果`（`PASS` / `FAIL` / `BLOCKED` / `NOT RUN`）；只有覆盖完整才能判定 PASS/FAIL，部分覆盖必须 BLOCKED，未执行使用 BLOCKED/NOT RUN。执行字段不属于批准范围指纹。每完成一个测试用例立即更新其执行字段，并同步写入报告和进度状态。执行中发现需求解释、步骤、预期、前置条件或范围变化时，必须暂停、重新确认并更新批准指纹后再继续。单个操作最多重试 1 次；单个测试用例超过 5 分钟或连续 60 秒没有可观察进展，自动暂停并报告当前测试用例、当前子步骤和等待原因，记录为 `BLOCKED` / `NOT RUN`。多个 System 时按测试用例顺序操作并核对最终结果；数据有延迟时等待可观察结果和写明的最长时间。点击后判断当前页变化、新页面、外部页面或下载，再继续操作。统计、指标或汇总需求在相同口径、时间范围和筛选条件下与参考数据比较；没有参考数据时记录 `BLOCKED`。测试结束或异常退出时先保存证据和状态，再自动关闭所有浏览器资源，不询问用户是否关闭。

遇到登录页时，Agent 必须暂停并提示用户手动输入账号密码。用户明确确认登录完成后才能继续。不同账号或角色必须使用独立浏览器会话。

测试结束后：

1. 复用或补充当前 Version 的 `test-scripts/`。
2. 更新唯一的 `report/report.md`，包含本次范围、脚本、测试用例结果、结果汇总、Bug、回归、未测试内容、风险和测试建议；Bug 修复后的回归重新执行当前 Version 最终测试用例集合，结果汇总只统计本次执行，回归结果与历史结果分开记录。
3. 根据本次已验证结果，按需更新当前 Version 的测试用例、结构化需求中的“测试后的实现说明”，以及 System 级 `element-map/` 和 `memory/`；只沉淀正确、稳定、可复用的事实，不写入推测或临时现象。
4. 向用户汇报结果，不执行 Git 操作。

## 6. Playwright 测试环境

### 6.1 配置位置

- System `system.yaml`：长期默认环境。
- Version `version.yaml`：本次测试的差异覆盖。
- Agent 探索可补充可观察信息，但关键上下文和测试地址必须由用户确认。
- 用户可以直接修改 YAML，文件是最终事实来源。

### 6.2 常见属性

- `maximize`：为 `true` 时使用真实最大化窗口（`--start-maximized` + `no_viewport`），此时忽略固定 `viewport`；web 默认 `true`。
- `viewport.width` / `viewport.height`：测试尺寸；`maximize` 为 `true` 时仅作无头/回退尺寸。
- `device_scale_factor`：设备像素比。
- `is_mobile`：移动端浏览器行为。
- `has_touch`：触摸能力。
- `locale`：语言和格式。
- `timezone_id`：时区。
- `action_timeout_ms` / `navigation_timeout_ms`：操作和导航超时。
- `login: manual`：固定表示登录必须由用户完成。

当前不扩展多浏览器和兼容性测试矩阵。

## 7. 长期资产与 RAG 边界

### 7.1 Element Map

Element Map 是 System 级页面元素地图，使用 `element-map/index.yaml` 和 `modules/*.yaml` 作为事实源，记录测试实际使用且后续可能复用的页面、入口、URL pattern、状态、按钮、输入框、表格、菜单、业务含义、主/备用 locator、稳定性依据、操作后的状态、验证 Version、验证视口和脚本引用。它不记录完整 DOM。

定位策略按稳定性优先：专用测试属性（如 `data-testid`）优先，其次是 Playwright 语义定位（如 `get_by_role`、`get_by_label`），再其次是基于稳定属性的 CSS Selector，然后是稳定且唯一的文本定位，XPath 仅作为最后兜底。禁止依赖动态 class、深层 DOM 路径、`nth-child`、数组下标、坐标或浏览器临时生成的定位值。

Element Map 应记录主定位、可选备用定位、稳定性依据、操作后的预期状态、最后验证的 Version 和视口；账号、UID、动态数量、动态 class、深层 DOM 路径和坐标不得作为定位依据。

先读 `element-map/index.yaml`，必要时读 `index.md` 摘要，再按当前任务读取相关 YAML 模块。只沉淀长期有价值的元素。

### 7.2 Memory

Memory 是 System 级长期知识，记录稳定业务规则、角色权限关系、测试前置条件、数据依赖、模块关系、已验证的重要行为、长期测试经验和已知限制。每个模块必须包含验证 Version、长期用途和稳定事实。

不记录一次性聊天、临时推理、完整 Session 日志、测试流水账、账号、UID、一次性样本缺口或任何凭据。

### 7.3 向量数据库

当前 Markdown / YAML 文件是唯一事实来源。未来向量数据库只保存经过筛选的高价值 Markdown 派生索引，例如结构化需求中的稳定业务规则、角色权限关系和稳定测试用例，供不同 Agent 通过 RAG 检索历史知识。Element Map 不默认整体进入向量数据库，只有经过验证、脱离具体页面细节且确有跨版本复用价值的内容，才考虑整理后建立索引。

测试报告和测试脚本说明默认不进入向量数据库；如果未来发现某类报告或脚本内容具有稳定复用价值，也必须先筛选、脱敏并明确索引规则。任何向量索引都不能替代本地文件。

## 8. BrowserSession

`BrowserSession` 是薄封装，只负责启动、创建页面、跳转和关闭，并把 `TestEnvironment` 映射为 Playwright Browser Context 配置。默认 `headless=False`，支持 `slow_mo` 和上下文管理器；页面对象仍使用原生 Playwright API。

它不负责登录、凭据管理、保存 Cookie / Storage State、安装 Google Chrome 或配置外部浏览器连接。

## 9. 安全与 Git 约束

- 不保存或自动填写密码、Token、Cookie、Storage State 或其他凭据。
- 敏感信息不得进入代码、测试脚本、YAML、Markdown、报告、Memory、Element Map、日志、截图、Trace、HAR 或视频。
- 不自动上传文件、删除资产、覆盖已有资产或扩大测试范围。
- 未经 Test Case 明确批准不得正式测试。
- 未经用户明确指令不得执行任何 Git 命令。
- 推荐业务分支为 `feature/<project-name>`，但分支由用户自行创建和管理。
- `master` 有更新时，建议将 `master` 合并到当前工作分支并重新执行受影响的测试。
- 禁止将其他分支直接合并到 `master`；进入 `master` 通过用户确认的 Pull Request 或受保护分支流程完成。

## 10. 测试与验收

pytest 至少覆盖：

- Project / System / Version Schema 的合法数据和非法 ID。
- System 类型枚举和 ID 类型后缀规则。
- Web 与移动类型的默认测试环境。
- Version 环境覆盖继承 System 默认值的规则。
- BrowserSession 默认 headed 和显式配置。
- 不引入数据库、Agent Runtime、LLM SDK 或其他越界依赖。
- Demo 单入口可发现，示例文件位于 `docs/examples/` 平级目录。

验收时还要人工确认：Agent 能发现 `docs/demo.md`，能先读取上下文，能在测试用例后暂停，遇到登录能等待用户手动操作，并能输出一份包含 Bug、测试用例结果和建议的统一测试报告。

## 11. 文档要求

- `AGENTS.md`：每次接手必须遵守的工作流、人工确认、登录和安全规则。
- `README.md`：项目背景、Element Map、Memory、分支命名、Agent 使用方式、资产结构和 RAG 边界。
- `workflow/README.md` 及各阶段 Prompt：不同 Agent 可复用的意图路由、阶段执行指引和同目录模板，不保存具体项目事实。
- `docs/architecture.md`：Agent、资产、浏览器和未来派生索引的关系。
- `workflow/asset-map.md`：真实资产位置、层级、更新者和生命周期。
- `workflow/testing/rules.md`：测试覆盖、测试用例确认、headed、手工登录、会话隔离和安全规则。
- `docs/demo.md` 与 `docs/examples/`：平铺且可发现的示例。

文档和模板必须与代码 Schema、目录契约和安全规则保持一致.
