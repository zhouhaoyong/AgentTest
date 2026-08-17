# AgentTest

AgentTest 是一个面向现成 AI Agent 的轻量 Web 测试工作区。它本身不是 Agent，也不绑定某一个 Agent，而是用 Markdown 和 YAML 保存整个测试过程与配置，让 Codex、Claude Desktop、Claude Code CLI、Hermes Agent、Reasonix 或其他能读写本地文件的 Agent 可以接续之前的工作，不必重复询问全部上下文。

其中 Markdown 保存需求、测试点、脚本说明、报告、Memory 和 Element Map 等可阅读资产；YAML 保存 Project、System、Version、测试环境和跨 Agent 状态等结构化配置。

## 如何开始工作？

AgentTest 不是一个可运行的程序，而是一套供 Agent 读写的文件工作区——你**通过与 Agent 对话**来推进测试，由 Agent 按目录契约和模板创建、更新资产。本节按顺序照做即可跑通一次完整测试，并尽量帮你避开常见误区。

**前置条件**

- 一个能读写本地文件的 Agent（Codex、Claude Desktop、Claude Code CLI、Hermes Agent、Reasonix 等）。
- 可选：Python `>= 3.11` 环境，仅当 Agent 没有内置 Chrome、需要 Python Playwright 兜底时才需要。Google Chrome 是否安装由你和当前 Agent 的环境决定，AgentTest 不自动安装。

**整体流程一览**

```text
原始需求
→ 确认基础信息
→ 第一轮需求质疑与编号追问
→ 需求整理
→ 探索决策与按需系统探索
→ 测试点设计
→ 人工确认测试点        ← 必经的暂停点
→ 浏览器测试
→ 测试报告（测试点结果、Bug、回归信息、风险和建议）
→ 修复后的回归测试
→ 沉淀 Element Map / Memory
```

**详细步骤**

1. **建分支。** 从 `master` 创建业务分支 `feature/<project-name>`（例如 `feature/gumai`），`<project-name>` 使用小写字母、数字和连字符。AgentTest 不会自动执行任何 Git 操作，切分支由你手动完成。
2. **打开项目。** 在你的 Agent 中打开本项目目录。Agent 会先读取 `.agentest/context.yaml` 和 `.agentest/state.yaml`（如存在）以接续之前的上下文。
3. **直接输入原始需求。** 不需要特殊命令，用自然语言说明你要测什么即可。
4. **确认上下文（新项目的关键一步）。** 如果是全新项目、上下文缺失，Agent 会**逐项跟你确认后再落地配置，缺什么问什么，不会自行编造**：

   - Project 名称（建议英文或拼音短名，中文也可）；
   - System 名称与**系统类型**（如 web、h5 / 移动端）；
   - Version **版本号**（给两种示例：`2026.08.01` 或 `v1.0.0`；提醒 Version 是测试资产目录，不是 Git 分支）；
   - **测试地址**：出于数据安全，建议使用测试环境，并确认它不是未经允许的生产环境；
   - **原始需求来源**；
   - 多个 System 一起验证时，再确认参与系统和操作顺序。

   用户不需要自行准备英文 ID。Agent 会根据业务名称生成目录安全 ID，展示 `name → id` 映射供确认；ID 只用于目录和资产关联，不是被测系统的业务用户 ID。首轮会先确认基础信息，再根据需求列出编号的“待确认需求”；没有待确认项时不展示该区块。你可以按“基础信息 1”“待确认需求 1”回复，避免答复错位。

   如果 System 已存在，Agent 会复用它，只新建或选择一个新的 Version，不会静默覆盖已有资产。
5. **澄清需求。** Agent 审查需求的遗漏、矛盾、边界和开放问题，向你提问并给出建议；你澄清后，它整理出结构化需求（`requirements/YYYYMMDD_V<版本号>_<system-id>.md`，简洁 PRD 形式）。
6. **探索决策与按需探索。** Agent 先审查并确认需求，再依据该 System 的 Memory / Element Map 覆盖度决定复用已有知识还是启动浏览器做目标探索；探索不等于正式测试。首次探索一个还没有 Element Map 的系统时，只要打开浏览器就开始记录，探索结束即产出第一版 Element Map 供本次测试直接复用。
7. **生成测试点后停下（必经暂停点）。** Agent 生成 `test-points/test-points.md` 后**必须停止等待你审核**。测试点确认只表示范围获批，不会启动浏览器；只有你明确说“开始正式测试”或等价表达，才会继续。 “看看”“继续分析”或只说“测试点确认”都不算启动。
8. **批量准备后执行已批准的测试点。** 你明确要求开始后，Agent 先一次性生成脚本骨架，再按页面 / 业务流程分组调试定位器和前置数据；正式执行时同组测试点复用同一个隔离 Chrome 会话，但仍按测试点记录结果，不在每个点击动作后重新规划和写文件。Agent 只执行已批准的测试点，不自动扩大范围。内置浏览器只有确认使用 Chrome 时才可使用；否则使用能创建新 Chrome 无痕会话的 Playwright 能力。没有可用 Chrome 能力时，Agent 会先询问是否需要协助安装或启用，未确认前不会打开你现有的浏览器。需要登录时会暂停，由你手动登录并确认后再继续；不同账号或角色使用隔离的浏览器会话，且绝不保存账号、密码、Token、Cookie 等凭据。
9. **出报告。** 测试结束后，Agent 在测试点中更新`未测试` / `已测试`及 `PASS` / `FAIL` / `BLOCKED` / `NOT RUN`；实际执行并完成结果记录才标为`已测试`，被环境、登录或读取问题阻塞则保留`未测试`。单个操作最多重试 1 次；单个测试点超过 5 分钟或连续 60 秒没有可观察进展，自动暂停并报告当前测试点和等待原因。随后生成统一的 `report/report.md`，记录每个测试点、Bug、结果汇总、风险和建议；同时核对需求文档里的页面、按钮、列表等名称是否与真实页面一致，必要时更新需求文档。
10. **回归与沉淀。** Bug 修复且你确认后，让 Agent 重新执行当前 Version 最终测试点集合的完整回归（联动需求则执行当前联动范围的完整集合）；长期可复用的信息再沉淀到 System 级 Element Map / Memory。

想看一份真实资产长什么样，见 [Demo 总览](docs/demo.md)；想深入了解 Agent 内部如何按阶段路由，见 [`workflow/README.md`](workflow/README.md)。

## 核心概念

### 资产层级：Project / System / Version

AgentTest 把测试资产组织成三层，并按目录保存：

```text
.agentest/                         # 跨 Agent 的当前上下文和状态
workflow/                          # 按用户流程聚合的公共 Prompt、模板和规则
projects/<project-name>/           # Project
├── systems/<system-name>/         # System
│   ├── element-map/               # 可复用的页面元素信息
│   ├── memory/                    # 可复用的系统知识
│   └── versions/<version-name>/   # 一次测试范围及其结果
└── integration-scopes/<scope>/    # 可选：多个 System 一起测试的资产
```

一个 Project 可包含多个 System，一个 System 可包含多个 Version。每个 Version 保存需求来源、结构化需求、测试点、测试脚本和一份统一的测试报告；System 级的 Element Map 和 Memory 可在不同 Version 之间复用。只有当一个需求需要多个 System 一起验证时，才创建 `integration-scopes/<scope>/`；长期知识仍保留在各自 System 下。Version 是测试资产目录，不是 Git 分支。

### Element Map

Element Map 是 System 级的页面元素地图，记录测试真正使用、后续可复用的页面元素和定位方式，例如页面、按钮、输入框、表格、菜单等元素及其业务含义，并记录验证时的视口/窗口尺寸（响应式布局会随窗口变化）。沉淀之后，后续测试可以直接复用已验证的页面知识，减少重复探索、重复沟通和定位错误。它不追求记录全部页面结构，只保留有长期复用价值的元素。

### Memory

Memory 是 System 级的长期知识，记录未来版本测试仍然有价值的信息，例如稳定的业务规则、角色和权限关系、测试前置条件和数据依赖、页面或模块之间的关系、已验证的重要系统行为，以及长期有效的测试经验和已知限制。

Memory 不保存一次性聊天、临时推理、测试流水账、完整 Session 日志或任何凭据。

## 资产结构

```text
projects/<project-name>/
├── systems/<system-name>/
│   ├── system.yaml
│   ├── element-map/
│   ├── memory/
│   └── versions/<version-name>/
│       ├── version.yaml
│       ├── requirements/
│       │   ├── requirement.md
│       │   ├── source.md
│       │   └── YYYYMMDD_V<版本号>_<system-id>.md
│       ├── test-points/
│       ├── test-scripts/
│       ├── evidence/
│       └── report/
└── integration-scopes/<scope>/     # 仅多个 System 一起测试时创建
    ├── scope.yaml
    ├── requirements/
    ├── test-points/
    ├── test-scripts/
    ├── evidence/
    └── report/
```

主要产物：

- `requirements/`：原始需求来源，以及最终整理出的结构化需求（简洁 PRD 形式）。
- `test-points/test-points.md`：本次的测试范围，经你人工确认后才会执行；测试后保留每个测试点的执行状态、结果和证据引用。范围指纹不包含这些执行字段。
- `test-scripts/` 与 `report/`：可复用的测试脚本，以及一份统一的测试报告（含测试点结果、Bug、风险和建议）。
- `evidence/`：本次测试的 Bug 证据（截图、Trace、HAR 等），报告中的 Bug 以相对路径引用；证据不含任何凭据。
- `element-map/` 与 `memory/`：System 级、可跨版本复用的页面元素与业务知识。

## 配置与环境

System 的 `system.yaml` 保存系统类型、测试地址和默认运行环境；Version 的 `version.yaml` 只记录本次测试地址和必要的差异。登录方式固定为手动，AgentTest 不会在配置里保存任何账号密码。你随时可以直接修改这些 YAML，Agent 下一次工作时以文件内容为准。

所有正式测试使用 Google Chrome。内置隔离浏览器只有确认使用 Chrome 时才优先；否则使用能创建新 Chrome 无痕会话的 Playwright 能力。每次启动 Python Playwright 前都会执行 Chrome pre-flight 检查；如果无法确认隔离，Agent 必须停止；如果能力缺失，Agent 会先询问是否需要协助安装或启用，不会自动使用 Edge、bundled Chromium，也不复用用户当前打开的浏览器。视口按系统类型自动选择：web 使用真实最大化窗口，H5 / 移动端使用移动端视口（如 iPhone 14 Pro）；操作默认超时为 10 秒，可在 `system.yaml` 中按需覆盖。

## 安全与边界（对你的保证）

- **你明确启动后才会真跑**：测试点必须先经你确认范围，再由你明确说“开始正式测试”，Agent 才会打开浏览器；之后只执行已批准的测试点，不会自动扩大范围。
- **绝不保存你的凭据**：不会保存账号、密码、Token、Cookie 或其他敏感信息，它们也不会写进任何文件、报告或截图。
- **只用隔离 Chrome**：禁止复用用户当前已打开的浏览器窗口、Tab、Profile 或地址；必须使用新建的隔离 Chrome 会话，既隔离登录态，也避免缓存造成误判。
- **不自动动 Git**：不会自动创建、切换、提交或合并分支，所有 Git 操作都由你决定。

更完整的规则见 [AGENTS.md](AGENTS.md) 与 [正式测试规则](workflow/testing/rules.md)。

## 分支命名

建议每次测试工作从 `master` 创建一个业务分支：

```text
feature/<project-name>
```

例如 `feature/gumai`。其中 `<project-name>` 使用适合 Git 的短名称（小写字母、数字和连字符）。

AgentTest 不自动创建、切换、合并或提交 Git 分支。如果 `master` 在工作期间有更新，建议先将 `master` 合并到当前工作分支，解决冲突后重新执行受影响的测试。禁止将其他分支直接合并到 `master`；最终进入 `master` 应通过用户确认的 Pull Request 或受保护分支流程完成。

## 相关文档

- [Demo 总览](docs/demo.md)：一份平铺、可发现的示例资产，想看真实资产长什么样可从这里开始。

以下面向 Agent 与开发者：[AGENTS.md](AGENTS.md)（工作流、人工确认、登录与安全规则）、[工作流入口](workflow/README.md)、[公共模板与真实资产映射](workflow/asset-map.md)、[prd.md](prd.md)、[架构说明](docs/architecture.md)、[正式测试规则](workflow/testing/rules.md)。
