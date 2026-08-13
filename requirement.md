# 仓库目录契约

## 目录职责

本目录包含 AgentTest v0.1 文件化测试工作区和测试资产规范。

## 允许内容

- `AGENTS.md`：Agent 在仓库中工作的强制规则。
- `prd.md`：产品需求和实现约束。
- `README.md`：面向用户的安装和使用说明。
- `docs/`：架构、Demo、示例和改造设计。
- `workflow/`：按用户工作流聚合的公共 Prompt、模板、规则和资产映射。
- `src/agentest/`：Python 包实现。
- `.agentest/`：跨 Agent 共享的当前工作上下文和状态。
- `projects/`：用户自己的 Project / System / Version 测试资产。
- `tests/`：Schema、浏览器配置和架构边界自动化测试。
- `pyproject.toml`、`.python-version`、`.gitignore`：项目配置。
- 本文件：仓库目录契约。

## 文件职责

源码负责实现能力，`workflow/` 负责保存公共 Prompt、模板、规则和资产映射，`projects/` 负责保存真实业务测试资产，`.agentest/` 负责保存当前工作上下文和状态，文档负责解释架构和 Demo。

## 更新规则

修改实现或测试规则前先阅读 `prd.md`、`AGENTS.md` 和 `workflow/README.md`。业务测试资产必须放在 `projects/`，不得放进源码、公共工作流或模板。

## 禁止事项

- 不添加额外的资产创建命令、数据库、前端、Agent Runtime、LLM SDK 集成或 Git 自动化。
- 不保存凭据或测试密码。
- 不静默覆盖 Project、System、Version 或用户资产。

## 阅读策略

先读本文件和 `AGENTS.md`，再根据用户意图阅读 `workflow/README.md` 与对应阶段契约。未来向量数据库只能作为高价值资产的派生索引，不能替代本地 Markdown / YAML 事实来源。
