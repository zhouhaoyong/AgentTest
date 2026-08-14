# 上下文确认 Prompt

你正在确认或选择真实 Project、System、Version、测试地址和原始需求来源；必要时确认多个 System 的联动范围。

## 进入条件

- 用户要求创建、选择或确认测试上下文，或原始需求流程尚未具备完整上下文。

## 必读资料

1. 根目录 `AGENTS.md`、`requirement.md` 和 [`workflow/README.md`](../README.md)。
2. `.agentest/context.yaml` 与 `.agentest/state.yaml`，如存在。
3. `projects/` 及目标 Project、System、Version 的目录契约与 YAML；首次了解仓库时读取 `docs/demo.md`。

## 决策与执行

1. 首轮只确认最小测试上下文：Project 中文名称、要测试的 System 名称和系统类型、Version 版本号或名称、测试地址、原始需求或需求来源。只有确实涉及多个 System 联动时，才确认参与系统、对应 Version、地址和操作顺序。
2. 用户只需提供业务可读名称，中文名称可以直接使用。Agent 根据名称生成目录安全 ID，并展示 `name → id` 映射供用户确认；ID 是内部目录和资产关联标识，不是被测系统里的用户 ID、英文名或 Git 分支名。若 ID 冲突、含义不清或用户不接受，再请用户调整。
3. 生成 ID 时遵守现有约束：Project、System、Version ID 只能使用目录安全字符；System ID 仍须以系统类型结尾。Version 是测试资产目录，不是 Git 分支。
4. 角色、权限、测试账号和具体业务测试数据不是通用的上下文问题。上下文阶段不预设角色覆盖范围，不索要账号密码，也不要求用户先整理业务数据；这些内容由需求阶段按本次需求判断是否需要。
5. 优先复用不冲突的 `.agentest/` 与既有 YAML 事实；已有 System 必须复用，不能静默覆盖。
6. 确认每个测试地址不是未经用户确认的生产环境；System 配置保存默认环境，Version 仅保存差异字段。联动范围只列出已确认的 System、Version 和地址。

首轮建议使用日常语言提问：“请提供项目名称、系统名称及类型、版本号、测试地址和原始需求。ID 由我根据名称生成并展示确认；如果需求涉及角色权限或特定测试数据，后续再按需确认。”

## 允许写入的位置

- 新建或更新的业务上下文只能写入 `projects/...` 标准目录；联动范围写入 `projects/<project>/integration-scopes/<scope>/`。
- 跨 Agent 接续所需的最小上下文只能写入 `.agentest/context.yaml` 与 `.agentest/state.yaml`。

## 交付物与移交方向

- 上下文确认后更新最小必要状态并移交 `requirements/`。
- 如果用户只要求管理上下文，向用户说明已确认或待确认的信息后结束。

## 强制停止条件

- 缺失或冲突的关键上下文一次性列出后暂停；不得编造 Project、System、Version、联动范围、地址、角色或权限。
- 不保存凭据，不执行正式测试。
