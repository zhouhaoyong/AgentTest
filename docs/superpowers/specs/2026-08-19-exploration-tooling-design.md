# 第二波：探索工具化设计

> **来源**：`问题清单与改造方案.md` P0/P1（Q1/Q6/Q11/Q4）与实施计划 `plans/2026-08-19-dogfood-reform-implementation-plan.md` 第二波 W2-1..5。
> **定位**：第一波把约束写进提示词/模板/静态校验；第二波把"靠自觉压不住"的部分下沉到**可被程序强制的工具**。
> **红线**：只新增 `src/agentest/`、`tests/`、`workflow/`、`docs/`；不动 `projects/` 业务资产；不自动 Git。
> **范式约束**：AgentTest 由自然语言/提示词驱动，不新增命令行入口或独立可执行程序。以下工具均为**纯库**，由提示词工作流按需调用。

## 背景问题（dogfood 实测）

探索暴力试错卡 36 分钟、逐次生成约 30 个一次性 JS 探测脚本。根因是：预算/收敛只有文字软约束、定位发现靠"生成脚本→run→再生成"。

## 模块总览

新增子包 `src/agentest/exploration/`，扩展 `schemas/workspace.py` 与 `asset_audit.py`。各模块尽量为**纯逻辑、可单测**；唯一需要浏览器的是发现工具，用 duck-typed page 做单测。

### W2-1 探索预算硬熔断 `exploration/budget.py`

纯状态机，不依赖浏览器。跟踪三类预算并给出结构化止损：

- **同目标重试**：对同一 `(entry_key)` 连续失败达 `max_retries_per_entry`（默认 3）即判该入口熔断。
- **无进展**：连续 `max_steps_without_progress`（默认 5）步没有"新事实"（`record_progress()` 未被调用）即整体止损。
- **总量兜底**：总步数上限 `max_total_steps`、可选墙钟时间上限 `max_seconds`（软兜底，硬超时仍由调度层负责）。

API：`ExplorationBudget(...)`；`start_entry(key)` / `record_attempt(key, *, success)` / `record_progress()` / `should_stop()->StopDecision`。`StopDecision(stop: bool, reason: str, detail: str)`——reason 取 `entry_retry_exhausted / no_progress / step_limit / time_limit`。到点直接 `stop=True`，调用方（提示词层或发现工具）据此停手并产出结构化上报，不靠自觉。

### W2-3 定位候选自动打分 `exploration/scoring.py`

纯逻辑，与 W1-3 静态校验共用启发式（模糊属性、选择器含中文、text 操作性括号），但用途不同：W1-3 在**入库期**拦截/告警，打分在**发现期**排序候选、把数据派生的降权标红。

- `score_locator(type, value, *, name=None) -> LocatorScore`。
- 基础分按类型优先级：testid(100) > role(90) > label(80) > 稳定属性 css(70) > text(50) > xpath(30)。
- 降权惩罚：css/xpath/testid 含中文自然语言、模糊属性匹配 `[class*=]`、text 夹带操作性括号、疑似动态值（纯数字/长十六进制/包含临时 class 特征）→ 扣分并置 `data_derived=True`、`warnings[]`。
- `LocatorScore(score:int, tier:str, data_derived:bool, warnings:list[str])`；tier ∈ `strong/ok/weak`。

### W2-2 单会话批量发现 `exploration/discovery.py`

在**一个**持续会话内一次评估多个候选定位，内部自带重试，替代"每试一次新脚本"。

- 输入：一个 page-like 对象（Playwright Page 或 duck-typed）+ `list[LocatorCandidate]`。
- `LocatorCandidate(id, type, value, name=None)`；`resolve_candidate(page, candidate)->ResolveResult(count:int, error:str|None)` 按类型 dispatch 到 `get_by_test_id/get_by_role/get_by_label/get_by_text/locator`。
- `discover(page, candidates, *, retries=1, budget=None)`：逐候选解析（失败按 `retries` 重试），合并 W2-3 打分，产出 `list[Discovery]` 并**排序**（先 found & unique，再按 score 降序）。可选传入 `ExplorationBudget`，每次解析计一次 attempt，预算触发即停并在结果里标注 `stopped_reason`。
- `Discovery(candidate, count, found, unique, score, tier, data_derived, warnings, error)`。
- 不写文件、不做副作用；把"选哪个定位入库"的判断留给调用方，但给出机器可读依据。

### W2-5 state.yaml 执行语义数据模型化 `schemas/workspace.py` + `asset_audit.py`

区分"执行过 vs 通过 vs 阻塞"，替代单一 `completed` 语义，且**向后兼容**：

- `WorkspaceState` 增可选 `test_case_results: dict[str, TestCaseOutcome]`，`TestCaseOutcome ∈ passed/failed/blocked/not_run`（"executed" 用 `completed_test_case_ids` 表示"已出结论"，不再另设枚举，避免与进度字段语义打架）。
- 校验（`asset_audit._check_state`）：results 的 key 必须在当前用例范围内；`completed_test_case_ids` 里的 id 若出现在 results，其结果必须是终态之一；results 里判 `passed` 的用例其 id 应在 `completed`。全部**可选**——不写 results 不报错，保持既有断点续跑与指纹逻辑不变。

## 测试策略

- budget/scoring：纯逻辑单测覆盖每条阈值与惩罚分支。
- discovery：duck-typed fake page（实现 `get_by_*`/`locator`，各返回带 `.count()` 的 fake locator）驱动，覆盖 found/unique/error/retry/budget-stop/排序。
- workspace/state：pydantic 往返 + asset_audit 一致性单测。
- 每模块落地即跑 `ruff check src tests` + `PYTHONPATH=src pytest -q`，全绿再下一项。

## 与第一波的衔接（提示词接线）

- `testing/prompt.md`：`state.yaml` 可选记 `test_case_results` 区分通过/阻塞。
- 说明：W2-1/2/3 三个探索工具当前为纯库存、未接入任何提示词（避免每次测试多读软约束白耗 token，将来上 harness 再启用）；W2-5 已接入 `asset_audit`。

## 撤案记录

原计划的 W2-4"固定入口 CLI（`agentest` 命令）"已于 2026-08-19 永久撤案：AgentTest 由自然语言/提示词驱动，塞命令行入口背离范式；Skill / MCP / settings 白名单同样否决。授权弹窗问题保持现状不处理。**后续不要再提议做 CLI / 固定入口 / 降授权白名单。**
