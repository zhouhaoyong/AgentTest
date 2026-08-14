# 上下文确认 Prompt

你正在确认或选择真实 Project、System、Version、测试地址和原始需求来源；必要时确认多个 System 的联动范围。

## 进入条件

- 用户要求创建、选择或确认测试上下文，或原始需求流程尚未具备完整上下文。

## 必读资料

1. 根目录 `AGENTS.md`、`requirement.md` 和 [`workflow/README.md`](../README.md)。
2. `.agentest/context.yaml` 与 `.agentest/state.yaml`，如存在。
3. `projects/` 及目标 Project、System、Version 的目录契约与 YAML；首次了解仓库时读取 `docs/demo.md`。

## 决策与执行

1. 单系统需求：确认 Project、System、Version、测试地址和原始需求来源。多个系统一起验证时：确认每个 System、对应 Version、测试地址和操作顺序，并创建 Project 下的联动范围。
2. 优先复用不冲突的 `.agentest/` 与既有 YAML 事实；已有 System 必须复用，不能静默覆盖。
3. 确认每个测试地址不是未经用户确认的生产环境；System 配置保存默认环境，Version 仅保存差异字段。联动范围只列出已确认的 System、Version 和地址。

## 允许写入的位置

- 新建或更新的业务上下文只能写入 `projects/...` 标准目录；联动范围写入 `projects/<project>/integration-scopes/<scope>/`。
- 跨 Agent 接续所需的最小上下文只能写入 `.agentest/context.yaml` 与 `.agentest/state.yaml`。

## 交付物与移交方向

- 上下文确认后更新最小必要状态并移交 `requirements/`。
- 如果用户只要求管理上下文，向用户说明已确认或待确认的信息后结束。

## 强制停止条件

- 缺失或冲突的关键上下文一次性列出后暂停；不得编造 Project、System、Version、联动范围、地址、角色或权限。
- 不保存凭据，不执行正式测试。
