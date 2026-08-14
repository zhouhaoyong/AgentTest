# AgentTest v0.1 产品需求与实现规范

## 1. 产品定位

AgentTest 是面向现成 AI Agent 的轻量文件化 Web 测试工作区。它本身不是 Agent，不实现 LLM、任务调度或测试管理后台。

用户可以在 Codex、Claude Desktop、Claude Code CLI、Hermes Agent、Reasonix 或其他能读写本地文件的 Agent 中直接输入需求。Agent 负责需求整理、系统探索、测试点设计、人工审核、浏览器测试和资产沉淀。

```text
原始需求 → 确认上下文 → 需求审查与用户澄清 → 需求整理 → 探索决策与按需系统探索 → 测试点
→ 人工审核 → 正式测试 → 脚本 / 建议版报告 → 回归测试
→ 更新 Element Map / Memory
```

核心原则：

- Markdown / YAML 是当前唯一事实来源。
- Agent 直接按目录契约和模板读写资产，不提供额外的资产创建命令。
- 不静默覆盖已有资产；已有 System 应复用并创建或选择新的 Version。
- Git 分支由用户自行管理，AgentTest 不执行 Git 操作。

## 2. 当前版本范围

### 2.1 必须实现

- Project / System / Version 的 Pydantic v2 YAML Schema。
- System 类型：`web`、`h5`、`app`、`miniapp`。
- System / Version 的 Playwright 测试环境配置，包括视口、设备、语言、时区和超时。
- Python Playwright 薄封装，作为 Agent 没有可用浏览器时的兜底能力。
- `workflow/` 公共脚手架：按用户流程聚合的 Prompt、模板、目录契约、规则和资产映射。
- Markdown / YAML 模板、目录契约、README、工作流和测试规则。
- `.agentest/context.yaml` 与 `.agentest/state.yaml` 的跨 Agent 状态约定，由 Agent 直接读写。
- 每个 Version 的 `test-scripts/` 和统一的 `report/report.md`；多个 System 一起测试时，使用 Project 下可选的联动范围目录保存同类资产。
- 一个平铺、可发现的 Demo：`docs/demo.md` 链接 `docs/examples/` 下的示例文件。
- pytest、Ruff 和架构边界测试。

### 2.2 明确不实现

- 额外的资产创建命令、环境诊断命令或自动生成目录的命令行入口。
- 前端、Dashboard、用户系统、数据库、远程服务和复杂任务调度器。
- 自研 Agent Runtime、LLM Provider、OpenAI / Anthropic SDK 或复杂 Memory Engine。
- 当前版本的 RAG 和向量数据库。未来只把经过筛选的高价值资产作为派生索引；测试报告和测试脚本说明默认不自动向量化。
- Native App / 小程序专用 Runner；`app`、`miniapp` 是系统身份分类，Playwright 兜底主要面向 Web / H5。
- 自动填写账号密码、凭据管理、Credential Vault、Storage State 管理、自动上传文件、自动安装浏览器或自动配置 MCP。
- Git 自动创建分支、commit、push、pull、merge、rebase、reset、stash 或其他历史操作。
- plugin system、event bus、service container、repository pattern 等复杂抽象。

## 3. 技术栈与仓库结构

### 3.1 技术栈

- Python `>= 3.13`
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
│   ├── test-points/
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
├── System
│   ├── system.yaml
│   ├── element-map/
│   ├── memory/
│   └── versions/
│       └── Version
└── integration-scopes/（可选）
    └── 联动范围
```

- 一个 Project 可以包含多个 System，一个 System 可以包含多个 Version。多个 System 必须一起验证时，Project 可增加 `integration-scopes/<scope>/`；它只保存该次联动测试资产。
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
  viewport:
    width: 1280
    height: 720
  device_scale_factor: 1
  is_mobile: false
  has_touch: false
  locale: zh-CN
  timezone_id: Asia/Shanghai
  action_timeout_ms: 5000
  navigation_timeout_ms: 30000
  login: manual
```

规则：

- `type` 只能是 `web`、`h5`、`app`、`miniapp`。
- System ID 必须以对应类型结尾，例如 `contact-web`、`contact-h5`、`contact-app`、`contact-miniapp`。
- `web` 默认视口为 `1280x720`；`h5`、`app`、`miniapp` 默认使用 `390x844`、移动端标识和触摸能力。
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
│   ├── YYYYMMDD_V<版本号>_<system-or-scope-id>.md
│   └── attachments/requirement.md
├── test-points/test-points.md
├── test-scripts/
└── report/report.md
```

`test-scripts/` 保存当前 Version 或联动范围内可重复执行的测试脚本，已确认需求发生变化时应及时调整相关脚本；`report/report.md` 统一保存最近一次正式测试或回归测试的建议版报告，包含测试点结果、Bug、风险、未测试内容和测试建议。

### 4.6 联动范围

路径：`projects/<project-name>/integration-scopes/<scope-name>/scope.yaml`。

联动范围只在一个需求需要多个 System 一起验证时创建。`scope.yaml` 按操作顺序列出参与的 System、Version 和已确认测试地址；该目录使用与 Version 相同的 `requirements/`、`test-points/`、`test-scripts/`、`report/` 结构。长期 Element Map 和 Memory 继续保留在各自 System 下。

## 5. Agent 工作流

### 5.1 确认上下文

Agent 首先读取最近的 `requirement.md`、`AGENTS.md`、`prd.md`、Demo 总览，以及 `.agentest/context.yaml` 和 `.agentest/state.yaml`（如果存在）。

首轮必须确认：

- Project 中文名称。
- System 名称和系统类型；多个 System 一起测试时，确认参与系统、对应 Version、地址和操作顺序。
- Version 名称或版本号；已有 System 不得重建，通常创建新 Version 并按用户要求升版本号。
- 测试地址。
- 原始需求来源。

Agent 根据业务名称生成 Project、System、Version 的内部 ID，并展示映射供用户确认。角色、权限、测试账号和具体测试数据只有在需求整理阶段判断确有必要时才确认，不属于所有项目的首轮必答项。

如果用户只提供原始需求，Agent 必须反问缺失的关键上下文，不得自行编造。用户可以直接修改 YAML；Agent 下一次工作以文件内容为准。

### 5.2 整理需求与探索

先保存或登记 `requirements/source.md`，再审查需求的遗漏、矛盾、边界和可测试性；需要时向用户提出问题并给出建议方案。用户澄清后，生成 `requirements/YYYYMMDD_V<版本号>_<system-or-scope-id>.md`；`requirements/requirement.md` 只作为目录契约。统计、指标或汇总需求还要确认口径、时间范围、筛选条件和可参考的数据来源。

系统探索用于理解页面、业务路径、模块和关键元素，不等于正式测试。需求整理后，Agent 先依据当前需求与 System Memory / Element Map 的覆盖度，选择复用已有知识、目标探索或必须探索；仅在需要时启动浏览器探索。业务期望与当前页面实现必须分开记录；页面没有对应按钮不代表需求无效，页面存在功能也不代表它自动属于本次需求。Agent 可以按需更新 System 级 Element Map / Memory，但只记录长期可复用的信息。

正式测试结束后，继续在同一份结构化需求文档中补充“测试后的实现说明”，但不得覆盖原始需求或未经用户确认改变业务目标或需求范围。

浏览器优先级：当前 Agent 的内置浏览器，其次 Python Playwright；Playwright MCP 只能在用户同意后作为可选增强，不是项目核心依赖。

### 5.3 测试点确认规则

Agent 在当前 Version 或联动范围的 `test-points/test-points.md` 生成测试点后必须停止。真实业务资产路径是 `projects/<project-name>/systems/<system-name>/versions/<version-name>/test-points/test-points.md`，或 `projects/<project-name>/integration-scopes/<scope-name>/test-points/test-points.md`；不得在项目根目录直接创建 `test-points/`。只有用户明确表示“测试点确认”“可以开始测试”“按照这些测试点执行”等含义，才能继续。

测试点应根据需求评估：

- 功能测试：正常、边界、非法输入、校验、错误、状态、持久化和页面重新进入后的状态。
- 业务流程测试：前置条件、主流程、分支、失败路径、中断恢复、跨页面 / 跨模块衔接和后置结果；业务数据通过页面行为验证其保存、流转或展示，不默认要求直接访问数据库。
- 角色与权限测试：角色可见性、操作权限、数据范围、数据隔离、受限访问和越权风险。

未覆盖或被阻塞的维度必须写明原因。

### 5.4 正式测试与回归

正式测试只执行已批准的 Test Points，不自动扩大范围。多个 System 时按测试点顺序操作并核对最终结果；数据有延迟时等待可观察结果和写明的最长时间。点击后判断当前页变化、新页面、外部页面或下载，再继续操作。统计、指标或汇总需求在相同口径、时间范围和筛选条件下与参考数据比较；没有参考数据时记录 `BLOCKED`。每个测试点记录 `PASS`、`FAIL`、`BLOCKED` 或 `NOT RUN`。

遇到登录页时，Agent 必须暂停并提示用户手动输入账号密码。用户明确确认登录完成后才能继续。不同账号或角色必须使用独立浏览器会话。

测试结束后：

1. 复用或补充当前 Version 的 `test-scripts/`。
2. 更新唯一的 `report/report.md`，包含本次范围、脚本、测试点结果、结果汇总、Bug、回归、未测试内容、风险和测试建议；Bug 修复后的回归重新执行当前 Version 或联动范围最终测试点集合，结果汇总只统计本次执行，回归结果与历史结果分开记录。
3. 只有长期可复用的知识才更新 System 级 `element-map/` 和 `memory/`。
4. 向用户汇报结果，不执行 Git 操作。

## 6. Playwright 测试环境

### 6.1 配置位置

- System `system.yaml`：长期默认环境。
- Version `version.yaml`：本次测试的差异覆盖。
- Agent 探索可补充可观察信息，但关键上下文和测试地址必须由用户确认。
- 用户可以直接修改 YAML，文件是最终事实来源。

### 6.2 常见属性

- `viewport.width` / `viewport.height`：测试尺寸。
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

Element Map 是 System 级页面元素地图，记录测试实际使用且后续可能复用的页面、URL pattern、按钮、输入框、表格、菜单、业务含义和稳定 locator。它不记录完整 DOM。

定位策略按稳定性优先：专用测试属性（如 `data-testid`）优先，其次是 Playwright 语义定位（如 `get_by_role`、`get_by_label`），再其次是基于稳定属性的 CSS Selector，然后是稳定且唯一的文本定位，XPath 仅作为最后兜底。禁止依赖动态 class、深层 DOM 路径、`nth-child`、数组下标、坐标或浏览器临时生成的定位值。

Element Map 应记录主定位、可选备用定位、稳定性依据和最后验证的 Version。

先读 `element-map/index.md`，再按当前任务读取相关模块。只沉淀长期有价值的元素。

### 7.2 Memory

Memory 是 System 级长期知识，记录稳定业务规则、角色权限关系、测试前置条件、数据依赖、模块关系、已验证的重要行为、长期测试经验和已知限制。

不记录一次性聊天、临时推理、完整 Session 日志、测试流水账或任何凭据。

### 7.3 向量数据库

当前 Markdown / YAML 文件是唯一事实来源。未来向量数据库只保存经过筛选的高价值 Markdown 派生索引，例如结构化需求中的稳定业务规则、角色权限关系和稳定测试点，供不同 Agent 通过 RAG 检索历史知识。Element Map 不默认整体进入向量数据库，只有经过验证、脱离具体页面细节且确有跨版本复用价值的内容，才考虑整理后建立索引。

测试报告和测试脚本说明默认不进入向量数据库；如果未来发现某类报告或脚本内容具有稳定复用价值，也必须先筛选、脱敏并明确索引规则。任何向量索引都不能替代本地文件。

## 8. BrowserSession

`BrowserSession` 是薄封装，只负责启动、创建页面、跳转和关闭，并把 `TestEnvironment` 映射为 Playwright Browser Context 配置。默认 `headless=False`，支持 `slow_mo` 和上下文管理器；页面对象仍使用原生 Playwright API。

它不负责登录、凭据管理、保存 Cookie / Storage State、安装 Chromium 或配置 MCP。

## 9. 安全与 Git 约束

- 不保存或自动填写密码、Token、Cookie、Storage State 或其他凭据。
- 敏感信息不得进入代码、测试脚本、YAML、Markdown、报告、Memory、Element Map、日志、截图、Trace、HAR 或视频。
- 不自动上传文件、删除资产、覆盖已有资产或扩大测试范围。
- 未经 Test Point 明确批准不得正式测试。
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

验收时还要人工确认：Agent 能发现 `docs/demo.md`，能先读取上下文，能在测试点后暂停，遇到登录能等待用户手动操作，并能输出一份包含 Bug、测试点结果和建议的统一测试报告。

## 11. 文档要求

- `AGENTS.md`：每次接手必须遵守的工作流、人工确认、登录和安全规则。
- `README.md`：项目背景、Element Map、Memory、分支命名、Agent 使用方式、资产结构和 RAG 边界。
- `workflow/README.md` 及各阶段 Prompt：不同 Agent 可复用的意图路由、阶段执行指引和同目录模板，不保存具体项目事实。
- `docs/architecture.md`：Agent、资产、浏览器和未来派生索引的关系。
- `workflow/asset-map.md`：真实资产位置、层级、更新者和生命周期。
- `workflow/testing/rules.md`：测试覆盖、测试点确认、headed、手工登录、会话隔离和安全规则。
- `docs/demo.md` 与 `docs/examples/`：平铺且可发现的示例。

文档和模板必须与代码 Schema、目录契约和安全规则保持一致.
