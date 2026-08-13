# 仓库目录契约

## 目录职责

本目录包含 AgentTest v0.1 脚手架和文件化测试资产。

## 允许内容

- `AGENTS.md`：Agent 在仓库中工作的强制规则。
- `prd.md`：产品需求和实现约束。
- `README.md`：面向用户的安装和使用说明。
- `docs/`：架构、工作流、资产和测试规范。
- `src/agentest/`：Python 包实现。
- `templates/`：创建资产时使用的源模板。
- `projects/`：用户自己的 Project / System / Version 测试资产。
- `tests/`：脚手架自动化测试。
- `pyproject.toml`、`.python-version`、`.gitignore`：项目配置。
- 本文件：仓库目录契约。

## 文件职责

源码负责实现能力，模板负责创建初始资产，`projects/` 负责保存真实业务测试资产，文档负责解释规则。

## 更新规则

修改实现或测试规则前先阅读 `prd.md` 和 `AGENTS.md`。业务测试资产必须放在 `projects/`，不得放进源码或模板。

## 禁止事项

- 不添加数据库、前端、Agent Runtime、LLM SDK 集成或 Git 自动化。
- 不保存凭据或测试密码。
- 不静默覆盖 Project、System、Version 或用户资产。

## 阅读策略

先读本文件和 `AGENTS.md`，再根据当前任务阅读对应子目录的 `requirement.md` 和相关文件。
