# AgentTest Agent 规则

## 项目目标

AgentTest 是面向现成 AI Agent 的轻量文件化 Web 测试脚手架。Markdown 和 YAML 资产是唯一事实来源。

## 开始工作前

1. 阅读最近的 `requirement.md` 目录契约。
2. 阅读 `prd.md`，了解产品边界。
3. 确认 Project、System、Version、测试地址和原始 Requirement Source。
4. 如果用户只提供原始需求，先反问必要信息，不要自行编造关键上下文。
5. 阅读相关 System 的 `memory/index.md` 和 `element-map/index.md`，只加载相关模块。

CLI 是可选工具。Agent 可以直接创建相同的标准资产，但必须使用相同的模板和“不覆盖已有文件”规则。

## 必须遵守的工作流

```text
原始需求
→ 确认上下文
→ 整理 Requirement
→ 可选 Analysis
→ 系统探索
→ Test Points
→ 人工审核 Gate
→ 正式测试
→ Result / Bugs / Report
→ 更新 Element Map / Memory
```

### 需求整理与系统探索

- 先保存或登记原始来源，再整理结构化需求。
- 只有复杂需求才生成有价值的 Analysis。
- 系统探索不等于正式测试。
- System Memory 和 Element Map 只记录长期可复用的信息。

### 测试点 Gate

生成 `test-points/test-points.md` 后必须停止。只有用户明确表示“测试点确认”“可以开始测试”或“按照这些测试点执行”等含义，才能正式测试。“继续分析”或“看看”不算批准。

测试点必须根据需求评估功能、业务流和权限 / 角色覆盖，并记录未覆盖或被阻塞的维度。

### 正式测试

- 只执行已经批准的 Test Points。
- 未经用户同意，不扩大测试范围。
- 相关时覆盖功能行为、边界、校验、错误、状态和持久化。
- 相关时覆盖业务前置条件、主流程、分支、失败路径、跨页面 / 跨模块衔接和后置结果。
- 相关时覆盖角色可见性、操作权限、数据范围、数据隔离、受限访问和越权风险。
- 不同账号或角色使用隔离的 Browser Context / Session。
- Python Playwright 默认使用 headed 模式。
- 需要登录时暂停并请用户手动登录；绝不保存或自动填写凭据。
- 每个批准的测试点记录 PASS、FAIL、BLOCKED 或 NOT RUN。
- Bug 必须关联 Test Point、测试维度、复现步骤、实际结果和预期结果。

如果重要的业务流或权限场景没有执行，不得宣称需求已经完整测试。

## 资产规则

- Project 包含 System；System 包含可复用的 Element Map、Memory 和 Version。
- Version 是目录，不是 Git 分支。
- `run/result.md`、`bugs/bugs.md` 和 `report/report.md` 表示该 Version 最近一次正式测试。
- 不把完整 System Memory 或 Element Map 复制到 Version。
- 不静默覆盖已有资产。

## Git 与安全

除非用户明确要求执行某个 Git 操作，否则不要运行任何 Git 命令。不得自动创建分支、commit、push、pull、merge、checkout、switch、reset、rebase 或 stash。不得删除资产、上传文件、填写密码或自动扩大测试范围。
