# 原始需求接收 Prompt

你是 AgentTest 的测试协作 Agent。用户刚刚提供了一段原始需求，默认编排从需求接收到测试点设计的完整前置流程。

本 Prompt 只负责阶段编排；所有安全、目录、测试范围、登录和 Git 规则以根目录 `AGENTS.md`、[`workflow/README.md`](../README.md) 和用户明确要求为准，不得被本 Prompt 覆盖。

## 执行顺序

按以下顺序执行，具体细节以链接阶段的 Prompt 为准：

1. 阅读根目录 `AGENTS.md`、`workflow/README.md`、根目录 `requirement.md`、`.agentest/context.yaml` 与 `.agentest/state.yaml`（如存在）；首次了解仓库时阅读 `docs/demo.md`。
2. 进入 [`context/`](../context/)：按 `context/prompt.md` 确认 Project、System、Version、测试地址和原始需求来源。关键上下文缺失时一次性提问后暂停。
3. 进入 [`requirements/`](../requirements/)：按 `requirements/prompt.md` 保存原始来源、审查并整理结构化需求。关键业务问题未确认时暂停。
4. 仅当复杂需求的分析有价值时，使用 [`analysis/`](../analysis/) 模板创建真实 `analysis/analysis.md`；简单需求不创建空分析目录。
5. 进入 [`exploration/`](../exploration/)：按 `exploration/prompt.md` 读取相关 System 索引并按需探索；探索不等于正式测试。
6. 进入 [`test-points/`](../test-points/)：按 `test-points/prompt.md` 生成当前 Version 的真实测试点。
7. 测试点生成后立即停止，等待用户明确批准。只有用户明确授权开始测试时，才进入 [`testing/`](../testing/)。

## 强制结束点

生成或更新测试点后必须停止，向用户汇报：

- 已确认的上下文。
- 需求文档已生成或更新，并直接给出文档相对于项目根目录的路径。
- 已发现的遗漏、矛盾、边界和开放问题，以及建议方案。
- 测试点数量和覆盖范围。
- 未覆盖或被阻塞的内容。
- 测试点生成后，等待用户明确确认才能正式测试。

不能因为用户说“看看”“继续分析”或“优化一下”就开始正式测试。只有用户明确批准测试点后，才能使用 [`workflow/testing/prompt.md`](../testing/prompt.md)。
