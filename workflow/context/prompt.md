# 上下文确认 Prompt

你正在执行 AgentTest 的上下文确认阶段。目标是确认或选择真实 Project、System、Version、测试地址和原始需求来源，并只在这些事实确认后创建或更新必要资产。

## 前置阅读

1. 根目录 `AGENTS.md`、`requirement.md` 和 [`workflow/README.md`](../README.md)。
2. `.agentest/context.yaml` 与 `.agentest/state.yaml`，如果存在。
3. 目标 `projects/` 目录和已存在的目标 Project / System / Version 目录契约与 YAML。
4. 首次了解仓库时阅读 `docs/demo.md`。

## 必须确认

- Project 名称和 ID。
- System 名称、ID、类型（`web`、`h5`、`app` 或 `miniapp`）。
- Version 名称和 ID。
- 测试地址，以及它不是未经确认的生产环境。
- 原始需求来源。

## 执行规则

1. 优先复用 `.agentest/` 和已有 YAML 中已经明确且不冲突的事实，不重复询问。
2. 已有 System 必须先读取并复用；按用户意图选择已有 Version 或创建新的 Version，绝不静默覆盖。
3. 缺失或冲突的关键上下文一次性列出问题后暂停，不得自行编造 Project、System、Version、地址、角色或权限。
4. 新建资产时只使用本目录相邻的 `template-*`；生成后的真实文件只写入 `projects/...` 和 `.agentest/...`。
5. `system.yaml` 的测试环境是 System 默认配置；`version.yaml` 只记录本次差异字段。不得保存凭据。
6. 上下文确认后更新 `.agentest/context.yaml` 与 `.agentest/state.yaml` 的最小必要字段，再移交 `requirements/`；若用户只要求上下文管理，在此阶段结束。
