# AgentTest 工作流

`workflow/` 是 AgentTest 公共脚手架的唯一入口。接到任务后，先读取本文件，再结合用户意图与 `.agentest/state.yaml` 选择一个阶段；随后读取阶段的 `requirement.md` 与 `prompt.md`。阶段 Prompt 只说明如何执行。单系统真实资产写到 `projects/<project>/systems/<system>/versions/<version>/`；多个 System 一起测试时，联动资产写到 `projects/<project>/integration-scopes/<scope>/`。

## 用户意图路由

| 用户意图或当前状态 | 进入阶段 | 允许产物与停止条件 |
| --- | --- | --- |
| 仅提供原始需求 | [`intake/`](intake/) | 编排上下文、需求、探索决策、按需探索和测试点；测试点完成后必须停止等待批准。 |
| 创建、选择或确认 Project / System / Version / 联动范围 / 地址 | [`context/`](context/) | 只更新必要 YAML、目录契约和 `.agentest/` 最小状态。 |
| 整理、澄清或更新需求 | [`requirements/`](requirements/) | 更新当前 Version 或联动范围的 `requirements/`；不执行测试。 |
| 探索页面、更新 Element Map 或 Memory | [`exploration/`](exploration/) | 只探索与当前需求相关内容；不当作正式测试。 |
| 设计或更新测试点 | [`test-points/`](test-points/) | 更新当前 Version 或联动范围的 `test-points/test-points.md` 后必须等待批准。 |
| 用户明确确认测试点或要求开始测试 | [`testing/`](testing/) | 只执行已批准测试点，随后更新脚本、报告和长期知识。 |
| 仅要求整理报告 | [`reporting/`](reporting/) | 只更新 `report/report.md`，不得补测。 |
| 已确认修复 Bug 且要求回归 | [`regression/`](regression/) | 执行当前 Version 或联动范围最终测试点的完整集合，并记录独立的本次结果。 |

若用户意图与 `.agentest/state.yaml` 冲突，或关键上下文、测试批准、回归范围缺失，必须提问并暂停，不得自行跳到后续阶段。

## 工作流顺序

```text
原始需求
→ 上下文确认
→ 需求整理
→ 探索决策
→ 按需系统探索
→ 测试点
→ 等待人工批准
→ 正式测试
→ 脚本 / 报告
→ Element Map / Memory 更新
```

需求整理后，Agent 依据当前需求与 System Memory / Element Map 的覆盖度选择复用已有知识、目标探索或必须探索；探索不等于正式测试。登录始终由用户手动完成；敏感凭据不得进入任何资产或测试产物。测试点必须获得明确批准后才可进入 `testing/`，并以当前文件完整内容为准。

## 公共脚手架与真实资产

- `workflow/`：公共 Prompt、模板、规则和说明，不保存业务事实。
- `.agentest/`：可接续的当前上下文与阶段状态。
- `projects/`：真实 Project / System / Version、联动范围、需求、测试点、脚本、报告和可复用知识的唯一位置。
- `docs/`：架构、Demo、示例与改造设计；Demo 不代表真实测试资产。

完整模板与最终资产位置见 [资产映射](asset-map.md)。
