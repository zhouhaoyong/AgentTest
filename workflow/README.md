# AgentTest 工作流

`workflow/` 是 AgentTest 公共脚手架的唯一入口。接到任务后，先读取本文件，再结合用户意图与 `.agentest/state.yaml` 选择一个阶段；随后读取阶段的 `requirement.md` 与 `prompt.md`。阶段 Prompt 只说明如何执行。真实资产写到 `projects/<project>/systems/<system>/versions/<version>/`。多个 System 一起测试（多端联动）时，不再新建独立联动目录，而是在参与联动的 `version.yaml` 内用轻量标记（`linked` / `linked_ends`）登记"和谁联动"，被引用端的地址仍以其自身 `version.yaml` 为准。

## 用户意图路由

| 用户意图或当前状态 | 进入阶段 | 允许产物与停止条件 |
| --- | --- | --- |
| 仅提供原始需求 | [`intake/`](intake/) | 编排上下文、需求、探索决策、按需探索和测试用例；测试用例完成后必须停止等待批准。 |
| 创建、选择或确认 Project / System / Version / 是否端联动 / 地址 | [`context/`](context/) | 只更新必要 YAML、目录契约和 `.agentest/` 最小状态。 |
| 整理、澄清或更新需求 | [`requirements/`](requirements/) | 更新当前 Version 的 `requirements/`；整理后需用户明确确认需求，再进入后续阶段；不执行测试。 |
| 探索页面、更新 Element Map 或 Memory | [`exploration/`](exploration/) | 只探索与当前需求相关内容；不当作正式测试。 |
| 设计或更新测试用例 | [`test-cases/`](test-cases/) | 更新当前 Version 的 `test-cases/test-cases.md` 后必须等待批准。 |
| 用户明确说“开始正式测试” | [`testing/`](testing/) | 先批量生成脚本并分组调试，再执行已批准测试用例；测试阶段只记录原始结果，不做汇总排版。测试用例确认本身不启动测试。 |
| 仅要求整理报告 | [`reporting/`](reporting/) | 只把测试阶段的原始结果汇总排版到 `report/report.md`，不得补测。 |
| 已确认修复 Bug 且要求回归 | [`regression/`](regression/) | 执行当前 Version 最终测试用例的完整集合，并记录独立的本次结果。 |

若用户意图与 `.agentest/state.yaml` 冲突，或关键上下文、测试批准、回归范围缺失，必须提问并暂停，不得自行跳到后续阶段。

## 工作流顺序

```text
原始需求
→ 基础信息确认
→ 第一轮需求质疑与待确认问题
→ 需求整理
→ 需求人工确认
→ 探索决策
→ 按需系统探索
→ 测试用例
→ 等待人工批准
→ 用户明确开始正式测试
→ 批量生成脚本 / 分组调试
→ 分组执行测试用例（记录原始结果）
→ 实际运行测试脚本并关闭浏览器
→ 报告汇总排版
→ Element Map / Memory 更新
```

需求整理前，Agent 先把待确认问题编号并集中询问；需求问题未清空不得进入页面探索。需求整理完成后需用户明确确认需求，才能进入探索与测试用例。需求确认后，Agent 依据当前需求与 System Memory / Element Map 的覆盖度选择复用已有知识、目标探索或必须探索；探索不等于正式测试。全流程统一使用内置隔离浏览器（由 Playwright 驱动系统 Chrome 的无痕会话），禁止复用用户当前已打开的浏览器窗口、Tab、Profile 或地址；无法确认隔离时先询问是否协助安装或启用，绝不打开用户现有浏览器。登录始终由用户手动完成；敏感凭据不得进入任何资产或测试产物。测试用例必须获得明确批准后才可进入 `testing/`，并以当前文件完整内容为准；脚本只在用户明确开始正式测试后才批量生成。

## 公共脚手架与真实资产

- `workflow/`：公共 Prompt、模板、规则和说明，不保存业务事实。
- `.agentest/`：可接续的当前上下文与阶段状态。
- `projects/`：真实 Project / System / Version、需求、测试用例、脚本、报告和可复用知识的唯一位置；多端联动通过 `version.yaml` 的轻量标记记录，不再有独立联动目录。System 的 Element Map 使用 YAML 事实源；Memory 使用固定章节 Markdown。
- `docs/`：架构、Demo、示例与改造设计；Demo 不代表真实测试资产。

完整模板与最终资产位置见 [资产映射](asset-map.md)。
