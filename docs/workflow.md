# Agent 工作流

```text
原始需求
↓
确认 Project / System / Version / 测试地址 / 来源
↓
保存来源并整理 Requirement
↓
可选 Analysis
↓
读取相关 Memory 和 Element Map 索引
↓
探索目标系统
↓
生成 Test Points
↓
停止：等待人工审核
↓
执行已批准的测试点
↓
更新 Result / Bugs / Report
↓
更新长期有效的 Element Map / Memory
```

用户不需要使用 CLI。当上下文缺失时，Agent 应提出必要问题，而不是编造正式资产信息。

系统探索不是正式测试。需要登录时由用户手动完成；Agent 暂停，用户登录后明确确认，Agent 才能继续。

正式测试必须根据需求评估功能、完整业务流和角色 / 权限行为。多个账号使用隔离会话。测试点必须获得明确批准后才能正式测试。
