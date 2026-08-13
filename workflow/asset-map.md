# 公共模板与真实资产映射

`workflow/` 中的模板只用于创建资产，不能替代或承载真实项目事实。创建后的文件必须放入以下位置。

| 阶段 | 公共模板 | 最终真实资产位置 |
| --- | --- | --- |
| 上下文 | `context/template-project.yaml` | `projects/<project>/project.yaml` |
| 上下文 | `context/template-system.yaml` | `projects/<project>/systems/<system>/system.yaml` |
| 上下文 | `context/template-version.yaml` | `projects/<project>/systems/<system>/versions/<version>/version.yaml` |
| 上下文 | 目录契约模板 | 对应 Project / System / Version 目录的 `requirement.md` |
| 需求 | `requirements/template-source.md` | `versions/<version>/requirements/source.md` |
| 需求 | `requirements/template-structured-requirement.md` | `versions/<version>/requirements/YYYYMMDD_V<版本号>_<system-id>.md` |
| 分析 | `analysis/template-analysis.md` | `versions/<version>/analysis/analysis.md`，仅复杂需求 |
| 探索 | Element Map / Memory 模板 | `systems/<system>/element-map/` 或 `memory/` |
| 测试点 | `test-points/template-test-points.md` | `versions/<version>/test-points/test-points.md` |
| 正式测试 | `testing/template-test-script.py` | `versions/<version>/test-scripts/<test-area>.py` |
| 报告 | `reporting/template-report.md` | `versions/<version>/report/report.md` |

所有 `requirements/`、`analysis/`、`test-points/`、`test-scripts/` 与 `report/` 都是 Version 级目录；Element Map 和 Memory 是 System 级目录。不得把真实资产写入 `workflow/`，也不得在项目根目录创建测试点或报告目录。
