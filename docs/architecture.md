# 架构说明

```text
Agent
  ↓
AGENTS.md + 最近的 requirement.md
  ↓
Project / System / Version Markdown 和 YAML 资产
  ↓
Agent 内置浏览器或 Python Playwright 兜底能力
  ↓
目标 Web 系统
```

AgentTest v0.1 使用本地 Markdown / YAML 文件作为事实来源。Git 可以保存历史，但 AgentTest 不自动执行 Git 操作。

## 代码分区

- `schemas/`：校验 Project、System、Version YAML。
- `scaffold/`：创建不覆盖已有数据的资产目录。
- `browser/`：启动默认 headed 的 Playwright 会话，并执行环境检查。
- `cli.py`：提供可选的环境检查和资产创建命令。

Agent 负责需求理解、系统探索、测试点生成、人工审核、正式测试以及长期资产更新。
