# 架构说明

```text
Agent
  ↓
AGENTS.md + 最近的 requirement.md
  ↓
Project / System / Version Markdown 和 YAML 资产
  ↓
Python Playwright 驱动的隔离 Chrome 会话（系统 Google Chrome 无痕）
  ↓
目标 Web 系统

未来可选：筛选高价值资产 → 向量数据库派生索引 → RAG 检索
```

AgentTest v0.1 使用本地 Markdown / YAML 文件作为事实来源。Git 可以保存历史，但 AgentTest 不自动执行 Git 操作。
向量数据库只作为未来的派生检索索引，不替代本地文件；测试报告和测试脚本说明默认不进入索引。

## 代码分区

- `schemas/`：校验 Project、System、Version 及跨 Agent 上下文 YAML。
- `browser/`：按 System / Version 测试环境启动默认 headed 的隔离 Chrome 会话（`session.py`），并在启动前做本地环境 pre-flight（`preflight.py`）。
- `exploration/`：探索期纯逻辑工具——预算硬熔断、定位稳定性打分、单会话批量发现与会话协调，可脱离真实浏览器单测。
- `test_cases.py`：批准范围指纹与关键覆盖约束解析。
- `asset_audit.py`：Version 资产的只读结构一致性审计。
- `workflow_gates.py`：测试用例确认 / 正式测试启动 / 报告交付三道只读闸门。

Agent 负责需求理解、系统探索、测试用例生成、人工审核、正式测试以及长期资产更新。
