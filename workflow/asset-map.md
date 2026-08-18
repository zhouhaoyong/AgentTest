# 公共模板与真实资产映射

`workflow/` 中的模板只用于创建资产，不能替代或承载真实项目事实。创建后的文件必须放入以下位置。

| 阶段 | 公共模板 | 最终真实资产位置 |
| --- | --- | --- |
| 上下文 | `context/template-project.yaml` | `projects/<project>/project.yaml` |
| 上下文 | `context/template-system.yaml` | `projects/<project>/systems/<system>/system.yaml` |
| 上下文 | `context/template-version.yaml` | `projects/<project>/systems/<system>/versions/<version>/version.yaml`（含 `linked` / `linked_ends` 多端联动轻量标记） |
| 上下文 | 目录契约模板 | 对应 Project / System / Version 目录的 `requirement.md` |
| 需求 | `requirements/template-source.md` | `versions/<version>/requirements/source.md` |
| 需求 | `requirements/template-structured-requirement.md` | `requirements/YYYYMMDD_V<版本号>_<system-id>.md` |
| 探索 | Element Map YAML / Memory Markdown 模板 | `systems/<system>/element-map/` 或 `memory/` |
| 测试用例 | `test-cases/template-test-cases.md` | `versions/<version>/test-cases/test-cases.md` |
| 正式测试 | `testing/template-test-script.py` | `versions/<version>/test-scripts/<test-area>.py` |
| 报告 | `reporting/template-report.md` | `versions/<version>/report/report.md` |

`requirements/`、`test-cases/`、`test-scripts/`、`evidence/` 与 `report/` 都是 Version 级目录；多端联动不新建独立目录，只在参与联动的 `version.yaml` 用 `linked` / `linked_ends` 登记联动关系，各端资产仍写在各自 Version 下。`evidence/` 保存 Bug 证据（截图 / Trace / HAR 等），无独立模板，测试时按需创建，证据不得包含凭据。Element Map 始终使用 System 级 `index.yaml` 与模块 YAML；Memory 使用 System 级索引和固定章节 Markdown。不得把真实资产写入 `workflow/`，也不得在项目根目录创建测试用例或报告目录。
