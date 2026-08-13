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

未来可选：筛选高价值资产 → 向量数据库派生索引 → RAG 检索
```

AgentTest v0.1 使用本地 Markdown / YAML 文件作为事实来源。Git 可以保存历史，但 AgentTest 不自动执行 Git 操作。
向量数据库只作为未来的派生检索索引，不替代本地文件；测试报告和测试脚本说明默认不进入索引。

## 代码分区

- `schemas/`：校验 Project、System、Version YAML。
- `browser/`：按 System / Version 测试环境启动默认 headed 的 Playwright 会话。

Agent 负责需求理解、系统探索、测试点生成、人工审核、正式测试以及长期资产更新。
