# CLAUDE.md

本文件用于让 Claude 系 Agent（Claude Desktop、Claude Code 等）冷启动时正确进入 AgentTest 工作流。

**开始任何工作前，必须先阅读 [`AGENTS.md`](AGENTS.md) 和 [`workflow/README.md`](workflow/README.md)，并严格按其中的工作流与规则执行。** 二者是本项目的权威约定，本文件只做指路，不覆盖它们。

几条最关键的红线（细则以 `AGENTS.md` 为准）：

- 用户只提供原始需求时，先反问缺失的关键上下文（Project、System、Version、测试地址、需求来源），不要自行编造。
- 生成测试用例后必须停止，等待用户明确确认后才能开始正式测试；只执行已批准的测试用例。
- 不保存任何凭据，不自动执行 Git 操作，不静默覆盖已有资产。
- 真实业务资产只写入 `projects/`，公共脚手架只在 `workflow/`。
