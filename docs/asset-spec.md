# 资产规范

| 资产 | 位置 | 负责者 | 生命周期 |
| --- | --- | --- | --- |
| Project | `projects/<project>/` | Agent 或用户 | 创建一次，不静默覆盖 |
| System | `projects/<project>/systems/<system>/` | Agent 或用户 | 多个 Version 共享 |
| Version | `.../versions/<version>/` | Agent 或用户 | 一个测试范围，System 内 ID 唯一 |
| Requirement Source | `version/requirements/source.md` 和 `attachments/` | 用户 / Agent | 保存或登记原始来源 |
| Requirement | `version/requirements/requirement.md` | Agent / 人工 | 结构化并可人工修改 |
| Analysis | `version/analysis/analysis.md` | Agent / 人工 | 复杂需求可选 |
| Test Points | `version/test-points/test-points.md` | Agent / 人工 | 获得明确批准前为 Draft |
| Result | `version/run/result.md` | Agent | 最近一次正式测试 |
| Bugs | `version/bugs/bugs.md` | Agent / 人工 | 最近一次正式测试发现的问题 |
| Report | `version/report/report.md` | Agent / 人工 | 最近一次正式测试汇总 |
| Element Map | `system/element-map/` | Agent / 人工 | 可长期复用的界面知识 |
| Memory | `system/memory/` | Agent / 人工 | 可长期复用的系统知识 |

每个主要目录都有 `requirement.md` 目录契约。Version 的 `requirements/requirement.md` 同时包含目录契约和结构化业务需求，其他目录的 `requirement.md` 只描述目录边界。
