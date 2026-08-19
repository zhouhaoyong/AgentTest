# Dogfood 复盘改造实施计划（2026-08-19）

> **来源**：根目录 `问题清单与改造方案.md`（基于 dogfood gumai/gumai-pc/2026.08.01 实测复盘）。
> **原则**：改造以**工具层强制为主、提示词为辅**；纯文字软约束已被 dogfood 证明压不住暴力试错。
> **分两波**：第一波是提示词/模板/数据模型 + `asset_audit` 校验增强（低风险、可立即回归）；第二波是"新建能力"（探索硬熔断代码化、单会话批量发现、定位自动打分、state 执行语义），需单独设计。
> **回归口径**：每完成一批跑 `ruff check src tests` + `PYTHONPATH=src pytest -q`，全绿再进下一批。

---

## 第一波：提示词 / 模板 / 数据模型 + 校验增强

### W1-1 元素地图索引升级（Q2 / Q14 / Q1 粒度）

- **文件**：`workflow/exploration/template-element-map-index.yaml`、`src/agentest/asset_audit.py`、`tests/test_asset_audit.py`、`docs/examples/element-map.yaml`（若为 index 样例）、dogfood 不动（只改脚手架）。
- **改法**：
  - index 模块字段扩为 `module_id`（沿用现 `id`，保持兼容）`/ title / file / routes[] / entry / covers[] / requirement_keywords[] / last_verified_version`；顶部新增可选 `global` 段（全局导航壳/登录入口/公共弹窗）。
  - `asset_audit._audit_element_map`：强校验仍只卡 `id`(或 `module_id`)、`file`；`purpose` 放宽为可选（被 `title`/`covers` 取代），新增字段全部可选、不拦截；`global` 段若存在做基本形状校验。
  - 更新对应单测：新增字段通过、缺核心字段拦截、`global` 段解析。
- **粒度**：在 `exploration/prompt.md` 增一条粒度规则（见 W1-2），index 模板注释写明"一个导航入口/独立页面 = 一个模块，子 Tab/弹窗/列表进 pages/states"。

### W1-2 探索提示词：范围锚定前置 + 无关模块结构化记录 + 数据vs元素（Q1 / Q15 / Q5 / Q6）

- **文件**：`workflow/exploration/prompt.md`、`workflow/exploration/template-element-map-module.yaml`。
- **改法**：
  - **范围锚定前置**（Q1）：把"探索预算与范围锚定"里的"先锚定范围"提为**探索第一步强制产出**——先输出「需求点→目标模块→入口」清单作为收敛锚点（不加人工确认闸门）。
  - **无关模块记录**（Q15）：改现第 29 行"不进也不记入"为——凡实际探到/路过的模块，一律用**同一套结构化模块模板完整记录**，格式不打折；范围纪律体现在"不主动绕路深挖无关模块"，而非"无关就少记"。
  - **模块粒度**（Q1）：新增一句"模块粒度锚定到导航入口/独立页面；子 Tab、弹窗、列表作为该模块 pages/states，不下切成新模块"。
  - **数据vs元素**（Q5/Q6）：在"只要打开浏览器就开始记录 Element Map"一节补：①元素地图只定位**结构**（地标/容器/行模板）用稳定属性，具体数据用运行时参数筛选，不把值烧进 locator；②按属性来源判别（标记契约=元素；回显业务内容=数据；"稳定文本"降权）；③数据敏感项标 `unverified`/待复核；④换一组数据仍成立才算结构。模块模板注释里同步这套分级与 `unverified` 约定。

### W1-3 元素地图定位质量校验（Q5）

- **文件**：`src/agentest/asset_audit.py`、`tests/test_asset_audit.py`。
- **改法**：`_audit_element_map_module` 对 `locator.primary` 增加**质量降级校验**（新 issue code，如 `weak_element_locator`）：
  - 占位/非机器可用值（含"（点击…）""标题区"等中文描述、或明显是自然语言而非选择器）→ 拦截或标警。
  - 模糊匹配（`[class*=`、`[class^=`、通配 `*`）在 `primary` 中→降级警告，建议移入 `fallback` 或补 `unverified`。
  - `type: text` 作为唯一 primary 且 value 是动态业务文案→提示降权（软告警，不硬拦，避免误伤稳定文案）。
  - 标注 `unverified: true` 的元素不计入"缺失定位"拦截，但汇总提示"待补验"。
- **注意**：先做成**告警级**（不 break 现有 dogfood 资产的回归），核心占位串（如 dogfood 的 `order-open`）做成拦截级。测试覆盖两档。

### W1-4 测试脚本模板：运行时发现数据 + 写操作脚本 + 按模块归组（Q2 / Q4 / Q12）

- **文件**：`workflow/testing/template-test-script.py`、`workflow/testing/prompt.md`、`workflow/testing/rules.md`、`src/agentest/asset_audit.py`（脚本元数据校验）、`tests/test_asset_audit.py`。
- **改法**：
  - **运行时发现数据**（Q2）：模板与规则明确——脚本不硬编码具体业务 id（订单号/UID 等）；改为运行时按条件发现（"查询一个已逾期且含接单用户的订单"）；确需固定样本抽到显式 fixture/数据契约并标"依赖数据前置"。
  - **写操作脚本**（Q4）：写操作用例也要产出**真实可复跑脚本**（前置数据准备→执行→断言回显→必要时幂等），不留"只读骨架"；写操作需在已确认测试环境+授权前提下。
  - **按模块归组**（Q12）：规则固化——一个元素地图模块/功能域对应一个脚本文件，用例作为其中测试函数；公共连接器单独成文件。
  - `asset_audit._check_test_scripts`：可选增强，脚本元数据校验里补"是否含硬编码可疑业务 id"的软告警（谨慎，避免误报）。

### W1-5 数据自愈规则（Q3）

- **文件**：`workflow/testing/prompt.md`、`workflow/testing/rules.md`、`workflow/regression/prompt.md`。
- **改法**：数据缺口触发"自愈优先"：先在授权+测试环境前提下尝试造**本需求相关**数据（测通讯录只造好友申请一类）；设**步数/次数熔断**，到点造不出立即停手，回给用户结构化的"数据前置清单"（缺什么/卡在哪/需哪端联动配合），并把脚本留成"数据就绪即可直接跑"的完整形态。区分"环境数据缺口（非 Bug）"与"功能缺陷"。测试环境数据不清理、不需每次授权。

### W1-6 执行与沉淀分离 + 不重复跑（Q7 / Q13）

- **文件**：`workflow/testing/prompt.md`、`workflow/testing/rules.md`、`workflow/reporting/prompt.md`。
- **改法**：
  - 明确"一次执行得结论；脚本是复现载体，默认**不额外重跑**，除非发起回归或用户明确要求"。删除/改写 rules.md 第 19 行"正式结束前至少实际运行一次脚本"这类会诱发"临时会话跑一遍+脚本再跑一遍"双执行的措辞。
  - 若选"以脚本执行为准"，报告必须在脚本跑绿后再定稿，杜绝"报告先行、脚本后红"。

### W1-7 前后端归因 + F12（Q9）

- **文件**：`workflow/testing/prompt.md`、`workflow/testing/rules.md`。
- **改法**：新增**异常触发的诊断步骤**（非常态开启）——遇报错/异常/断言失败时读取 Console 报错 + Network 状态码/响应体归因：4xx+响应体提示缺参→前端传参；5xx/后端错误码→后端；前端渲染异常→前端。归因结论写入 Bug 记录。

### W1-8 报告模板：结论先行 + 去掉"交付前自检"版面（Q8）

- **文件**：`workflow/reporting/template-report.md`、`workflow/reporting/prompt.md`、`src/agentest/asset_audit.py`（若汇总解析依赖章节位置）、`tests/test_asset_audit.py`。
- **改法**：
  - 模板顶部新增"结论摘要"区（一句话结论 + 汇总数字 + 是否可宣称通过），明细表下沉；删除可见的 §10"交付前自检"章节。
  - `reporting/prompt.md` 保留自检为**出报告前的内部静默闸门**（现 step 7 已是内部核对，措辞改为"不写进报告正文"）。真正 load-bearing 的两项（汇总算术自洽、无凭据泄露）由 agent 静默执行。
  - 校验兼容：`asset_audit._check_report` 按表头名解析、按 label 解析汇总，不依赖 §编号，故移动/删章节不影响校验（已确认现实现是按名解析，低风险；跑测试确认）。

### W1-9 加载策略 / token 经济（Q13）

- **文件**：`workflow/exploration/prompt.md`、`workflow/testing/prompt.md`、`workflow/regression/prompt.md`（必读资料段）。
- **改法**：明确"系统级资产（元素地图/Memory）跨版本复用、版本级资产（用例/报告）按版本隔离"；回归/新版本按 index 只加载相关模块，不整包灌；日常靠"结论先行"摘要读报告。

### W1-10（可选）state.yaml 语义澄清（Q4）

- **文件**：`workflow/testing/prompt.md`、`workflow/testing/rules.md`、（如落到数据模型）`src/agentest/asset_audit.py._check_state` + 测试。
- **改法**：区分 `executed`/`passed`/`blocked`，不用单一 `completed` 概括"执行过 vs 通过/可复现"。**先做提示词澄清**（低风险）；改数据模型字段放到第二波与工具一起，避免破坏现有指纹/续跑逻辑。

---

## 第二波：新建能力（需单独设计，先出 spec 再实现）

> 这些在现有代码里无对应模块，属"造新工具"，各自应在 `docs/superpowers/specs/` 出设计、`plans/` 出实现计划，再编码+测试+回归。此处只登记范围与目标。

### W2-1 探索硬熔断代码化（Q1）
把"同一入口重试≤N、连续无新事实即停、单模块步数/时间上限"从 prompt 软约束下沉到可被程序强制的机制（探索会话状态机 + 预算计数）。目标：到点直接停，不靠自觉。

### W2-2 单会话批量发现工具（Q11）
一个持续隔离浏览器会话内一次跑完多个候选定位、内部自带重试，替代"每试一次新脚本"。压弹窗、降 token、缓解跨会话数据态漂移。

### W2-3 定位候选自动打分（Q6 机械化）
发现工具对每个候选定位自动标注类型（test-id/role/文本/位置）+ 稳定性分，数据派生降权标红，把"结构 vs 数据"判别从模型自觉搬进工具。与 W1-3 的静态校验互补（一个在发现期，一个在入库期）。

### W2-4 ~~固定入口命令 / MCP 降授权（Q10）~~ 已永久撤案（2026-08-19）
AgentTest 由自然语言/提示词驱动，塞命令行入口 / Skill / MCP / settings 白名单均背离范式，全部否决。授权弹窗问题（Q10）保持现状不处理。**后续不要再提议做 CLI / 固定入口 / 降授权白名单。**

### W2-5 state.yaml 执行语义数据模型化（Q4 承接 W1-10）

---

## 排期与检查点

1. ~~W1-1 → W1-2 → W1-3（元素地图簇）~~ **已完成**，回归全绿。
2. ~~W1-4 → W1-5 → W1-6 → W1-7（测试/脚本簇）~~ **已完成**，回归全绿。
3. ~~W1-8 → W1-9 → W1-10（报告/加载/状态）~~ **已完成**，回归全绿。
4. ~~第一波整体回归全绿 + 更新 `问题清单与改造方案.md` 各条"状态"~~ **已完成**（102 passed，2026-08-19）。
5. ~~第二波 W2-1/2/3/5 代码化 + 测试~~ **已完成**（W2-1 budget / W2-2 discovery / W2-3 scoring 为纯库存、未接线；W2-5 已接入 asset_audit）。W2-4 CLI **永久撤案**。

## 第一波实施落点（2026-08-19，已回归全绿）

- 元素地图：`workflow/exploration/template-element-map-index.yaml`（新 schema + global 段 + 粒度注释）、`template-element-map-module.yaml`（结构 vs 数据分级 + `unverified` 约定 + 存根示例）、`src/agentest/asset_audit.py`（模块必填放宽为 id+file、`global` 形状校验、`weak_element_locator` 三规则、`unverified` 跳过）、`tests/test_asset_audit.py`（新增 3 组单测）、`docs/examples/element-map.yaml`（同步新 schema）。
- 探索：`workflow/exploration/prompt.md`（范围锚定前置为第一步、模块粒度、无关模块结构化记录、结构 vs 数据规则、加载策略）。
- 测试/脚本：`workflow/testing/prompt.md`、`rules.md`、`template-test-script.py`（按模块归组、运行时发现数据、写操作真实脚本、数据自愈+熔断、前后端归因、一次执行得结论不重复跑、completed 语义澄清、加载策略）。
- 回归：`workflow/regression/prompt.md`（引用上述执行细则 + 加载策略）。
- 报告：`workflow/reporting/template-report.md`（结论摘要先行、Bug 归因字段、删可见交付前自检）、`workflow/reporting/prompt.md`（自检改内部静默闸门、以脚本为准须跑绿再定稿）、`docs/examples/report.md`（同步）。
- 未触碰 dogfood `projects/` 业务资产；未做 Git 操作。

## 约束（沿用 AGENTS.md 红线）

- 只改 `workflow/`、`src/`、`tests/`、`docs/` 脚手架与校验；**不动 dogfood 的 `projects/` 业务资产**。
- 不保存凭据、不自动 Git、不静默覆盖既有资产。
- 每批改完必须回归全绿再继续。
