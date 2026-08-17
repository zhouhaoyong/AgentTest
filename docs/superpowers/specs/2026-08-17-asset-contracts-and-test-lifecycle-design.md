# AgentTest 资产契约与测试生命周期设计

## 目标

让 AgentTest 产出的 Element Map、Memory 和 Test Script 能被后续 Agent 直接复用，并让正式测试结果、需求澄清和浏览器生命周期具备可审计的一致性。

## 设计决策

### 1. Element Map

Element Map 采用 YAML 作为模块事实源，保留 Markdown 索引仅用于人工导航。每个模块 YAML 记录页面、入口、元素、定位器、备用定位、稳定性依据、行为、预期状态、验证 Version 和视口。禁止把账号、动态数量和一次性页面状态作为定位依据。

### 2. Memory

Memory 继续使用 Markdown，但按稳定主题组织。每条事实必须说明验证 Version、长期用途和稳定事实。一次性账号、样本 UID、单轮缺数、截图和执行流水账只留在 Version 报告，不进入 System Memory。

### 3. Test Script

正式测试必须先生成脚本骨架，再调试定位器和前置数据，测试后实际运行脚本并在报告记录脚本路径与运行方式。脚本使用全新 Google Chrome 会话，登录仍由用户手动完成，不保存凭据或 Storage State。

### 4. 测试结果与澄清

测试用例新增“执行覆盖”字段：`完整`、`部分`、`未执行`。只有覆盖完整时才能使用 PASS 或 FAIL；部分执行必须使用 BLOCKED，未执行使用 BLOCKED 或 NOT RUN。批准后若改变步骤、预期或范围，必须重新确认并更新范围指纹；测试后澄清只作为实现说明记录，不能掩盖原始执行差异。

### 5. 浏览器生命周期

正式测试脚本通过 `BrowserSession` 上下文管理器运行，测试结束或异常时自动关闭所有页面、Context、Browser 和 Playwright。Agent 不询问用户是否关闭；只有用户明确要求保留现场时才暂时保留。

## 兼容性与边界

- 不引入 Agent Runtime、数据库、凭据管理或远程服务。
- Markdown / YAML 仍是唯一事实来源。
- 不修改既有业务 Project；本次只改公共脚手架、校验能力、模板和示例规范。
- Element Map 的 YAML 结构用于机器读取，不能替代业务需求和测试用例范围。

## 验收标准

- 新 Element Map 模板明确 YAML 模块字段和稳定定位要求。
- Memory 模板明确长期事实与一次性测试信息边界。
- 正式测试模板和规则要求脚本先行、脚本可运行、脚本不含凭据。
- 静态审计能识别缺少脚本、无效执行覆盖、结果与覆盖不一致、非法 Element Map YAML 和不完整 Memory 模块。
- BrowserSession 上下文退出时释放所有资源，并有单元测试保护。
- 现有 pytest 与 Ruff 验证通过。
