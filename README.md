# AgentTest

AgentTest 是一个面向现成 AI Agent 的轻量 Web 测试工作区。

它本身不是 Agent，也不绑定某一个 Agent。你可以使用 Codex、Claude Desktop、Claude Code CLI、Hermes Agent、Reasonix 或其他能够读写本地文件的 Agent，完成需求整理、测试点设计、浏览器测试和测试结果沉淀。

AgentTest 使用 Markdown 和 YAML 保存测试过程与配置，让不同 Agent 可以接续之前的工作，而不需要重复询问全部上下文。Markdown 主要保存需求、测试点、脚本说明、报告、Memory 和 Element Map 等可阅读资产；YAML 主要保存 Project、System、Version、测试环境和跨 Agent 状态等结构化配置。结构化需求本身使用 Markdown，并按简洁的产品 PRD 组织。

## 项目背景

AgentTest的测试工作会经历：

```text
原始需求
→ 需求审查与用户澄清
→ 需求整理
→ 系统探索
→ 测试点设计
→ 人工确认测试点
→ 浏览器测试
→ 测试报告（包含测试点结果、Bug、回归信息和建议）
→ 修复后的回归测试
→ 沉淀 Element Map / Memory
```

AgentTest 将这些过程保存为文件：

```text
.agentest/                         # 跨 Agent 的当前上下文和状态
workflow/                          # 按用户流程聚合的公共 Prompt、模板和规则
projects/<project-name>/           # Project
└── systems/<system-name>/         # System
    ├── element-map/               # 可复用的页面元素信息
    ├── memory/                    # 可复用的系统知识
    └── versions/<version-name>/   # 一次测试范围及其结果
```

每个 Version 可以保存需求来源、结构化需求、测试点、测试脚本和一份统一的测试报告。报告集中记录测试点结果、Bug、回归信息、风险和建议；System 级的 Element Map 和 Memory 可以在不同 Version 之间复用。

### Element Map 是什么

Element Map 是 System 级的页面元素地图，记录测试真正使用、后续可复用的页面元素和定位方式，例如：

- 页面和 URL pattern
- 按钮、输入框、表格、菜单等元素
- 元素的业务含义
- 稳定的 locator 策略

沉淀 Element Map 后，后续 Agent 可以直接复用已验证的页面知识，减少重复探索、重复沟通和定位错误。它不追求记录全部 DOM，只记录有长期复用价值的元素。

元素定位按稳定性优先：

1. 专用测试属性：`data-testid`、`data-test`。
2. 语义定位：`get_by_role`、`get_by_label`。
3. 基于稳定属性的 CSS Selector。
4. 稳定且唯一的文本定位。
5. XPath 仅作为最后兜底。

应避免动态 class、深层 DOM 路径、`nth-child`、数组下标、坐标和浏览器临时生成的定位值。Element Map 应记录主定位、可选备用定位、稳定性依据和最后验证的 Version。

### Memory 是什么

Memory 是 System 级的长期知识，记录未来版本测试仍然有价值的信息，例如：

- 稳定的业务规则
- 角色和权限关系
- 测试前置条件和数据依赖
- 页面或模块之间的关系
- 已验证的重要系统行为
- 长期有效的测试经验和已知限制

Memory 不保存一次性聊天、临时推理、测试流水账、完整 Session 日志或任何凭据。

## 分支命名规范

建议每次测试工作从 `master` 创建一个业务分支：

```text
feature/<project-name>
```

例如：

```text
feature/gumai
```

其中 `<project-name>` 使用适合 Git 的短名称，例如小写字母、数字和连字符。Version 是测试资产目录，不是 Git 分支。

AgentTest 不自动创建、切换、合并或提交 Git 分支。分支创建和测试完成后的合并由用户自行决定。

如果 `master` 在工作期间有更新，建议先将 `master` 合并到当前 `feature/<project-name>` 工作分支，解决冲突后重新执行受影响的测试。禁止将其他分支直接合并到 `master`；最终进入 `master` 应通过用户确认的 Pull Request 或受保护分支流程完成。

## 工作方式：直接与 Agent 对话

这是推荐的日常使用方式。

1. 从 `master` 创建业务分支，例如 `feature/gumai`。
2. 在 Codex、Claude Desktop、Claude Code CLI、Hermes Agent 或 Reasonix 中打开项目。
3. 直接输入原始需求，Agent 按目录契约和模板创建或更新资产。
4. Agent 读取 `.agentest/context.yaml` 和 `.agentest/state.yaml`。
5. 如果上下文缺失，Agent 只询问必要信息：Project、System、Version、测试地址和需求来源。
6. 如果 System 已存在，则复用 System，并创建或选择新的 Version。
7. Agent 审查需求遗漏、矛盾、边界和开放问题，向你提出问题并给出建议方案。
8. 你澄清后，Agent 补全结构化需求并生成测试点。
9. 测试点生成后，Agent 必须停止，等待你明确确认。
10. 你确认后，Agent 使用内置浏览器或 Playwright 执行已批准的测试点。
11. 测试结束后，Agent 复用或补充测试脚本，并生成一份测试报告（建议版），统一记录测试点结果、Bug、回归信息、风险和后续建议。
12. Bug 修复后，要求 Agent 按相关测试点进行回归测试。
13. 长期可复用的信息再沉淀到 Element Map / Memory。

需要登录时，Agent 必须暂停，由用户手动完成登录并明确确认后才能继续；不同账号或角色应使用隔离的浏览器会话。

### 工作流脚手架

[`workflow/README.md`](workflow/README.md) 是公共脚手架的唯一入口。Agent 接到任务后，先根据用户意图与 `.agentest/state.yaml` 选择唯一阶段；该阶段的目录将 Prompt、模板、规则和目录契约放在一起，避免跨目录查找。

默认入口是 [`workflow/intake/prompt.md`](workflow/intake/prompt.md)：用户只提供原始需求时，Agent 依次确认上下文、登记并整理需求、按需探索和生成测试点，然后在测试点确认环节暂停。需要单独执行阶段任务时，可按需进入：

- [`workflow/context/`](workflow/context/)：确认或选择 Project、System、Version、测试地址和来源。
- [`workflow/requirements/`](workflow/requirements/)：审查、澄清并整理结构化需求。
- [`workflow/exploration/`](workflow/exploration/)：系统探索与长期 Element Map / Memory 沉淀。
- [`workflow/test-points/`](workflow/test-points/)：生成或更新测试点，生成后必须暂停。
- [`workflow/testing/`](workflow/testing/)：执行已批准的测试点。
- [`workflow/reporting/`](workflow/reporting/)：生成或更新统一的测试报告（建议版）。
- [`workflow/regression/`](workflow/regression/)：复用脚本执行 Bug 修复后的回归测试。

`workflow/` 只保存公共脚手架；真实需求、测试点、脚本、报告、Element Map 和 Memory 必须继续写入 `projects/`。公共 Prompt 不能替代 `AGENTS.md`、目录 `requirement.md`、已有资产或用户明确要求；发生冲突时，以它们为准。完整位置见 [`workflow/asset-map.md`](workflow/asset-map.md)。

### 测试环境配置

System 的 `system.yaml` 配置系统类型、地址和 Playwright 默认环境；Version 的 `version.yaml` 只记录本次测试地址和必要的环境覆盖。常见配置包括视口宽高、设备像素比、移动端标识、触摸能力、语言、时区、操作超时和导航超时。登录字段固定为 `manual`，不支持在配置中保存账号密码。

Agent 的处理顺序是：先读取已有配置，再通过探索补充可观察到的信息；测试地址、系统类型、登录方式等关键上下文必须向用户确认，不能自行编造。用户也可以直接修改 YAML，Agent 下一次工作时以文件内容为准。

Python Playwright 需要的运行依赖可用项目环境安装；Chromium 是否安装由当前 Agent 和用户环境决定，Agent 不自动安装或配置 MCP。

## 资产说明

```text
projects/<project-name>/
└── systems/<system-name>/
    ├── system.yaml
    ├── element-map/
    ├── memory/
    └── versions/<version-name>/
        ├── version.yaml
        ├── requirements/
        │   ├── requirement.md
        │   ├── source.md
        │   └── YYYYMMDD_V<版本号>_<system-id>.md
        ├── analysis/
        ├── test-points/
        ├── test-scripts/
        └── report/
```

主要文件职责：

- `requirements/source.md`：原始需求来源。
- `requirements/requirement.md`：需求目录契约。
- `requirements/YYYYMMDD_V<版本号>_<system-id>.md`：最终结构化需求，以简洁的产品 PRD 形式保存；测试后继续在同一文件补充测试后的实现说明。
- `test-points/test-points.md`：当前 Version 下按功能测试、业务流程测试和按需增加的角色 / 权限测试组织的测试范围，并记录未覆盖、开放问题、阻塞项和风险；经过人工审核后才能执行。
- `test-scripts/`：按 Test Point 沉淀的测试脚本，至少支持当前 Version 内的重复测试；需求变更后及时调整，用于正式测试和 Bug 修复后的回归测试。
- `report/report.md`：测试报告（建议版），统一记录本次测试范围、脚本、测试点结果、结果汇总、Bug、回归、未测试 / 阻塞内容、风险、建议和结论；回归结果与历史结果分开统计。
- `element-map/`：长期可复用的页面元素和定位信息。
- `memory/`：长期可复用的业务规则和系统知识。

### 当前事实来源与未来 RAG

当前 Markdown 和 YAML 文件是唯一事实来源。未来如果接入向量数据库，它只能作为经过筛选、脱敏和结构化整理后的 Markdown 知识索引，不能替代本地文件，也不能直接把 YAML 配置或全部历史文件写入向量库。

优先考虑进入向量数据库的，是跨项目或跨版本仍然有效、能帮助 Agent 做判断的高价值知识：

- 结构化需求中的稳定业务规则。
- System Memory 中的长期有效知识。
- 已确认的角色、权限和数据关系。
- 稳定、可复用且经过验证的测试点。

Element Map 不默认整体向量化。元素定位高度依赖具体页面和版本，原始 Element Map 可能与不精确需求产生歧义；未来只有经过筛选、验证并脱离一次性页面细节的通用知识，才考虑整理成 Markdown 后建立索引。测试报告和测试脚本说明默认不进入向量数据库。

## 测试规则与边界

- 测试点未经用户明确确认，不得开始正式测试。
- 正式测试只执行已批准的测试点，不自动扩大范围。
- 测试脚本应关联稳定的 Test Point ID，不保存密码或临时探索代码。
- 系统 ID 必须体现系统类型，例如 `gumai-web`、`gumai-h5`、`gumai-app`、`gumai-miniapp`。
- 相关需求应覆盖功能、业务流和权限 / 角色场景。
- 测试报告必须记录每个测试点的 `PASS`、`FAIL`、`BLOCKED` 或 `NOT RUN`。
- 不保存密码、Token、Cookie、Storage State 或其他凭据；敏感信息也不得进入代码、脚本、YAML、Markdown、报告、截图、Trace、HAR 或视频。
- 不自动安装或配置 MCP；是否使用 MCP 由用户和当前 Agent 环境决定。
- 不添加数据库、前端、Agent Runtime 或 LLM SDK。

详细规则见：

- [AGENTS.md](AGENTS.md)
- [工作流入口](workflow/README.md)
- [公共模板与真实资产映射](workflow/asset-map.md)
- [Demo 总览](docs/demo.md)
- [prd.md](prd.md)
- [正式测试规则](workflow/testing/rules.md)
