# AgentTest Agent 规则

## 项目目标

AgentTest 是面向现成 AI Agent 的轻量文件化 Web 测试工作区。Markdown 和 YAML 资产是唯一事实来源。

## 输出语言

- 与用户的对话，以及写入 `projects/` 的叙述性落地资产（结构化需求、测试点、测试报告、Memory、目录契约等）默认使用简体中文。
- 但一切原样引用被测系统的内容必须保留原文、不得翻译：页面与元素文案、URL、CSS / XPath 选择器、`data-testid` 等属性、代码标识符等。因此 Element Map 的说明文字用中文，其中的定位串、属性名和界面原文保持英文或系统原语言。
- 面向用户反问或汇报时使用业务语言，从用户和被测系统的角度描述（页面、按钮、流程、角色、数据），不要出现类、方法、函数、变量、接口等代码或实现术语，避免给业务用户造成困扰。
- 用户另有明确要求时以用户为准。

## 开始工作前

1. 阅读最近的 `requirement.md` 目录契约。
2. 阅读 [工作流路由](workflow/README.md)，根据用户意图和 `.agentest/state.yaml` 选择唯一阶段。
3. 阅读 `prd.md`，了解产品边界。
4. 首次了解资产结构时，必须阅读 [Demo 总览](docs/demo.md)。
5. 确认 Project、相关 System、Version、测试地址和原始 Requirement Source；多个 System 需要一起验证时，确认联动范围和操作顺序。
6. 如果用户只提供原始需求，先反问必要信息，不要自行编造关键上下文。
7. 阅读相关 System 的 `memory/index.md` 和 `element-map/index.md`，只加载相关模块。

Agent 必须先读取所选 `workflow/<stage>/requirement.md`，再读取该阶段的 `prompt.md`、规则和模板。公共脚手架只存在于 `workflow/`；真实业务资产只能写入 `projects/` 的标准目录。已有资产必须先读取，不能静默覆盖。

阶段 Prompt 只补充当前阶段的执行步骤，不替代本文件、目录契约或用户明确要求。用户意图与 `.agentest/state.yaml` 冲突，或关键上下文、测试批准、回归范围缺失时，必须提问并暂停，不得自行跳到后续阶段。

## Prompt 使用规则

- 用户只提供原始需求时，优先使用 [`workflow/intake/prompt.md`](workflow/intake/prompt.md) 作为入口。
- 需要单独执行阶段任务时，按 [`workflow/README.md`](workflow/README.md) 选择上下文、需求、探索、测试点、正式测试、报告或回归阶段。
- Prompt 和模板是公共脚手架，不得写入项目事实、测试地址、账号、密码或其他敏感信息。
- Prompt 与现有资产或用户要求冲突时，以本文件、目录契约、已有事实和用户明确要求为准。

跨 Agent 接续工作时，优先读取根目录 `.agentest/context.yaml` 和 `.agentest/state.yaml`。只有上下文缺失或冲突时，才重新询问 Project、System、Version、联动范围、测试地址或当前阶段。

## 必须遵守的工作流

```text
原始需求
→ 确认上下文
→ 审查遗漏、矛盾、边界并向用户澄清
→ 整理 Requirement
→ 探索决策
→ 按需系统探索
→ Test Points
→ 测试点确认
→ 正式测试
→ 测试脚本 / 测试报告（建议版）
→ 更新 Element Map / Memory
```

### 需求整理与自适应系统探索

- 先保存或登记原始来源，再整理结构化需求。
- 首轮上下文确认只询问项目名称、系统名称及类型、版本号、测试地址和原始需求来源等最小信息。用户只需提供中文或其他业务可读名称，Project / System / Version 的内部 ID 由 Agent 生成并展示确认；不得把英文 ID 当成用户必须自行提供的业务信息。
- 需求整理后先读取相关 System 的 Memory 和 Element Map，判断是否复用已有知识、进行目标探索或必须探索；仅在需要时启动浏览器探索。
- 角色、权限、测试账号和具体业务测试数据不是通用的首轮上下文问题。只有需求涉及登录、角色差异、数据范围、数据隔离或多账号流程时，才确认角色覆盖、账号可用性和数据前置条件；不索要密码、Token、Cookie 或 Storage State，也不自行编造具体业务数据。
- 系统探索不等于正式测试。探索决策及依据应在测试点范围中简要说明。
- System Memory 和 Element Map 只记录长期可复用的信息。

### Element Map 与元素定位

Element Map 中的定位必须优先选择稳定、与 DOM 层级解耦的依据，按以下顺序尝试：

1. 专用测试属性：`data-testid`、`data-test` 等。
2. 语义定位：Playwright 的 `get_by_role`、`get_by_label` 等。
3. 基于稳定属性的 CSS：例如 `[name="email"]`、`[data-action="save"]`。
4. 稳定且唯一的文本定位。
5. XPath 仅作为最后兜底。

禁止使用动态 class、深层 DOM 路径、`nth-child`、数组下标、坐标和浏览器临时生成的定位值。每个元素应记录主定位方式、可选备用定位方式、稳定性依据和最后验证的 Version。

### 测试点确认规则

在当前 Version 或联动范围的 `test-points/test-points.md` 生成测试点后必须停止。真实业务资产路径是 `projects/<project-name>/systems/<system-name>/versions/<version-name>/test-points/test-points.md`，或 `projects/<project-name>/integration-scopes/<scope-name>/test-points/test-points.md`；不得在项目根目录直接创建 `test-points/`。只有用户明确表示“测试点确认”“可以开始测试”或“按照这些测试点执行”等含义，才能正式测试。开始前必须重新读取该文件当前完整内容，并以它作为唯一测试范围；“继续分析”或“看看”不算批准。

测试点必须像软件测试工程师一样先分析需求，再以功能测试和业务流程测试为主线，按需增加角色 / 权限测试，并记录未覆盖、开放问题、阻塞项和风险。多个 System 时写清操作顺序和最终结果；统计、指标或汇总需求写清口径、时间范围、筛选条件和参考数据。

### 正式测试

- 只执行已经批准的 Test Points。
- 未经用户同意，不扩大测试范围。
- 相关时覆盖功能行为、边界、校验、错误、状态和持久化。
- 相关时覆盖业务前置条件、主流程、分支、失败路径、跨页面 / 跨模块衔接和后置结果。
- 多个 System 时，只按批准的测试点顺序操作，并在下一系统或最终位置核对结果。
- 统计、指标或汇总需求在相同口径、时间范围和筛选条件下，与可参考的数据比较；没有参考数据时记录阻塞。
- 相关时覆盖角色可见性、操作权限、数据范围、数据隔离、受限访问和越权风险。
- 不同账号或角色使用独立浏览器会话。
- Python Playwright 默认使用 headed 模式。
- 需要登录时暂停并请用户手动登录；绝不保存或自动填写凭据。
- 用户确认登录完成后才能继续；不得保存账号密码、Token、Cookie、Storage State 或其他敏感信息。
- 敏感信息不得出现在代码、测试脚本、YAML、Markdown、报告、Memory、Element Map、日志、截图、Trace、HAR 或视频中。
- Bug 证据应保留足以判断问题的原始页面状态；普通业务数据不要求脱敏，不得为了脱敏而裁剪、遮挡或修改证据。凭据及其他敏感信息仍不得进入任何测试产物。
- 点击后确认是当前页变化、新页面、外部页面还是下载；切到正确位置后继续。外部页面只验证跳转，下载核对必要内容。
- 数据更新有等待过程时，等待可观察结果和测试点写明的最长时间；成功提示不等于通过，最终要核对页面或数据。
- 每个批准的测试点记录 PASS、FAIL、BLOCKED 或 NOT RUN。
- Bug 必须关联 Test Point、测试维度、复现步骤、实际结果和预期结果。

### 当前 Version 回归

Bug 修复并经用户确认需要回归时，重新执行当前范围最终 `test-points/test-points.md` 中的完整测试点集合。单系统范围是当前 Version；联动范围只包含 `scope.yaml` 列出的 System 和 Version。原 Bug 场景必须仍被该集合覆盖；不自动扩大到其他 Version、System 或联动范围。

如果重要的业务流或权限场景没有执行，不得宣称需求已经完整测试。

## 资产规则

- Project 包含 System；多个 System 需要一起测试时，可增加 `integration-scopes/` 保存联动范围。System 包含可复用的 Element Map、Memory 和 Version。
- Version 是目录，不是 Git 分支。
- `test-scripts/` 保存当前 Version 或联动范围可重复执行的测试脚本。
- `report/report.md` 统一表示当前 Version 或联动范围最近一次正式测试或回归测试的报告，包含测试点结果、Bug、风险和建议。
- 报告的结果汇总只统计本次执行的 Test Point；回归测试必须单独记录历史结果与本次结果，不得混合统计。
- `requirements/requirement.md` 只作为需求目录契约；结构化需求使用 `YYYYMMDD_V<版本号>_<system-or-scope-id>.md` 命名，按简洁产品 PRD 组织，并在测试后继续更新同一文件的测试后的实现说明。
- 不把完整 System Memory 或 Element Map 复制到 Version。
- 不静默覆盖已有资产。

## Git 与安全

除非用户明确要求执行某个 Git 操作，否则不要运行任何 Git 命令。不得自动创建分支、commit、push、pull、merge、checkout、switch、reset、rebase 或 stash。不得删除资产、上传文件、填写密码或自动扩大测试范围。

分支方向约束：用户在 `master` 基础上创建 `feature/<project-name>` 工作分支。若 `master` 有更新，应由用户决定是否将 `master` 合并到当前工作分支；合并后重新执行受影响的测试。禁止将其他分支直接合并到 `master`，进入 `master` 必须由用户通过 Pull Request 或分支保护流程完成。
