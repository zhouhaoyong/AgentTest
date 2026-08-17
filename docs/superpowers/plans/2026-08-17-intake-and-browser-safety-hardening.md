# 需求入口与浏览器安全流程加固实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 Agent 在第一轮同时完成上下文确认、需求质疑和测试前置条件收集，并在任何页面操作前选择隔离浏览器，避免复用用户已有登录态，同时收紧上下文状态和资产写入边界。

**Architecture:** 继续以 Markdown / YAML 作为唯一事实来源，不新增数据库、Agent Runtime 或浏览器连接服务。需求入口由 `intake`、`context`、`requirements` 三个阶段共同形成“第一轮集中澄清 → 结构化需求 → 页面事实探索”的门禁；浏览器由宿主 Agent 优先使用内置隔离浏览器，无法使用时才调用现有 `BrowserSession`，任何无法证明隔离的浏览器都直接停止。

**Tech Stack:** Markdown、YAML、Python 3.11+、Pydantic v2、Playwright Python、pytest、Ruff。

## Global Constraints

- Markdown / YAML 是唯一事实来源；不得把截图中的上一轮对话当作新的用户授权或操作指令。
- 用户对话和 `projects/` 叙述性资产默认使用简体中文；被测系统原文、URL、选择器和属性保持原样。
- 不保存或自动填写密码、Token、Cookie、Storage State，也不复用用户当前打开的浏览器标签页或 Profile。
- 需求质疑必须先于页面探索；页面探索只验证页面事实，不替用户决定业务目标。
- 测试点生成后必须停止等待用户明确批准；本计划不改变测试点批准和指纹规则。
- 不执行 Git 操作，不创建真实业务 Project，不修改 `workflow/` 之外的业务资产。
- 现有 `BrowserSession` 仍是 Python Playwright 兜底能力，不扩展为浏览器管理器或外部连接服务。

## 文件与职责映射

- `workflow/intake/prompt.md`：规定原始需求入口的一轮集中提问和阶段移交。
- `workflow/context/prompt.md`：规定基础上下文、需求前置条件和状态展示边界。
- `workflow/requirements/prompt.md`：规定需求完整性审查、矛盾质疑和可测试性确认。
- `workflow/exploration/prompt.md`：规定探索只验证页面事实，以及探索后差异确认的边界。
- `workflow/test-points/prompt.md`：规定未解决的需求疑点不能直接形成可执行测试点。
- `workflow/testing/prompt.md`、`workflow/testing/rules.md`：规定浏览器选择、会话隔离和失败即停止。
- `workflow/asset-map.md`、`AGENTS.md`、`README.md`、`prd.md`、`docs/architecture.md`：同步公共流程、资产写入和用户可见说明。
- `src/agentest/browser/session.py`：保留并验证 Playwright 隔离会话兜底，不负责连接用户已有 Chrome。
- `src/agentest/schemas/workspace.py`：继续使用现有 `phase`、`pending_questions` 和 `BrowserSelection` 表达阶段与浏览器偏好，不新增没有用途的状态字段。
- `tests/test_directory_contracts.py`：保护 Prompt、目录和用户可见规则的一致性。
- `tests/test_architecture_guard.py`：保护用户可见的浏览器安全边界。
- `tests/test_browser_config.py`：保护 `BrowserSession` headed、无痕、独立 Context 和资源清理行为。
- `tests/test_schemas.py`：保护浏览器选择值和跨 Agent 状态字段语义。

---

### Task 1: 建立“第一轮集中澄清”的失败契约

**Files:**
- Modify: `tests/test_directory_contracts.py`
- Test: `tests/test_directory_contracts.py`

- [ ] **Step 1: 添加第一轮同时覆盖上下文和需求审查的静态测试**

添加以下测试，要求入口 Prompt 同时明确基础上下文、需求质疑、角色/账号/数据前置条件和写操作风险，而不是只询问 Project / System / Version：

```python
def test_intake_prompt_combines_context_and_requirement_review() -> None:
    root = Path(__file__).parents[1]
    content = (root / "workflow" / "intake" / "prompt.md").read_text(encoding="utf-8")

    for phrase in (
        "第一轮集中确认",
        "需求质疑",
        "角色、账号和测试数据",
        "写操作风险",
        "不自洽",
        "不完整",
        "测试点",
    ):
        assert phrase in content


def test_requirement_review_precedes_page_exploration() -> None:
    root = Path(__file__).parents[1]
    requirements = (root / "workflow" / "requirements" / "prompt.md").read_text(encoding="utf-8")
    exploration = (root / "workflow" / "exploration" / "prompt.md").read_text(encoding="utf-8")

    assert "先审查需求" in requirements
    assert "页面探索不能替代需求审查" in exploration
    assert "页面事实差异" in exploration
```

- [ ] **Step 2: 运行聚焦测试，确认现有文案未满足新契约**

运行：

```text
uv run --python 3.11 --no-progress pytest -p no:cacheprovider tests/test_directory_contracts.py -k "intake_prompt_combines or requirement_review_precedes" -q
```

预期：失败，说明当前入口仍把需求质疑和前置条件放在上下文确认之后。

---

### Task 2: 实现第一轮集中提问和需求质疑流程

**Files:**
- Modify: `workflow/intake/prompt.md`
- Modify: `workflow/context/prompt.md`
- Modify: `workflow/requirements/prompt.md`
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `prd.md`

- [ ] **Step 1: 在 intake Prompt 中定义统一提问包**

将首轮提问固定为一个消息中的四个区块：

1. 基础上下文：Project、System 和系统类型、Version、测试地址、原始需求来源。
2. 需求审查：主动指出需求中的矛盾、缺失、含糊术语、缺失验收标准和不可验证描述。
3. 测试前置条件：角色、手动登录账号可用性、数据条件、是否需要多账号或数据隔离。
4. 风险和边界：写操作授权、数据恢复、输入边界、异常路径、明确不测试的范围。

要求 Agent 先复述需求，再列出“已理解的目标、发现的疑点、需要用户确认的事项、开放风险”，不得只机械地索要五项上下文信息。

- [ ] **Step 2: 在 context Prompt 中区分基础上下文和需求就绪状态**

明确：Project / System / Version / 地址确认后，只代表“基础上下文已确认”，不代表需求已经可测试。若第一轮需求问题尚未回答，`phase` 保持 `requirements`，问题进入 `pending_questions`，不能移交测试点阶段。

用户可见回执使用类似以下表达：

```text
基础上下文已确认：Project / System / Version / 测试地址
需求状态：需求审查进行中
待确认：角色、数据条件、边界和写操作授权
```

- [ ] **Step 3: 在 requirements Prompt 中加入需求质疑清单**

需求整理必须逐项审查：目标和范围、业务对象、流程与分支、角色权限、输入和边界、异常与失败路径、数据依赖、页面衔接、持久化结果、统计口径和风险。

对每个问题标记为“已确认事实、合理推断、待用户确认或明确排除”，但不能把推断写成已确认需求。涉及登录、权限、数据隔离或写操作时，第一轮就提出相关问题，不等探索结束才提出。

- [ ] **Step 4: 保留原始来源，但延迟结构化需求和测试点**

允许先保存 `requirements/source.md` 作为原文登记；在关键疑点未确认前，不生成结构化需求、不生成测试点、不启动正式测试。用户补充后，再生成唯一结构化需求文档。

- [ ] **Step 5: 更新用户文档和全局规则**

在 `AGENTS.md`、`README.md` 和 `prd.md` 中把工作流改为：

```text
原始需求
→ 第一轮上下文确认 + 需求质疑 + 前置条件确认
→ 结构化需求
→ 探索决策
→ 页面探索
→ 页面事实差异确认
→ 测试点
→ 用户批准
```

明确“尽量第一轮完成”不等于禁止所有后续追问：只有页面探索产生新的真实页面差异，或用户回答引出新的业务歧义时，才允许追加问题。

- [ ] **Step 6: 重跑聚焦测试**

运行：

```text
uv run --python 3.11 --no-progress pytest -p no:cacheprovider tests/test_directory_contracts.py -k "intake_prompt_combines or requirement_review_precedes" -q
```

预期：通过。

---

### Task 3: 固化浏览器优先级和失败即停止策略

**Files:**
- Modify: `workflow/testing/prompt.md`
- Modify: `workflow/testing/rules.md`
- Modify: `workflow/exploration/prompt.md`
- Modify: `workflow/README.md`
- Modify: `README.md`
- Modify: `prd.md`
- Modify: `tests/test_architecture_guard.py`
- Modify: `tests/test_browser_config.py`

- [ ] **Step 1: 添加浏览器策略契约测试**

在 `tests/test_architecture_guard.py` 中添加静态测试，保护用户可见文档必须同时包含以下规则：内置隔离浏览器优先、Playwright 为无内置浏览器时的兜底、禁止复用现有 Chrome、无法确认隔离则停止。

```python
def test_browser_selection_is_isolated_and_fail_closed() -> None:
    root = Path(__file__).parents[1]
    paths = [
        root / "README.md",
        root / "prd.md",
        root / "workflow" / "testing" / "rules.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "内置隔离浏览器" in content
    assert "Playwright" in content
    assert "不复用用户当前打开的浏览器" in content
    assert "无法确认隔离" in content
```

在 `tests/test_browser_config.py` 中补充断言：默认 headed、启动参数包含 `--incognito`、创建独立 Context，不使用 `connect_over_cdp` 或用户 Profile。

- [ ] **Step 2: 修改正式测试和探索阶段的浏览器选择顺序**

统一为：

1. Agent 内置浏览器存在且能创建新隔离会话时，优先使用它。
2. 没有内置隔离浏览器时，使用 `BrowserSession` 创建 headed Playwright 会话。
3. 用户当前打开的 Chrome、已有 Tab、已有登录 Profile 和 CDP 附着会话都不属于可用兜底方式。
4. 若无法证明会话隔离，停止并向用户说明，不先打开地址再检查登录态。

- [ ] **Step 3: 加入首次导航前的会话检查**

浏览器打开测试地址之前，先确认会话来源是新建且隔离的；导航后确认页面处于未登录状态。若出现已登录账号、用户身份信息或非预期业务首页，立即废弃当前会话并停止，不继续探索，不把“发现后切换”作为合规流程。

- [ ] **Step 4: 明确 BrowserSession 的边界**

保持 `src/agentest/browser/session.py` 的现有公共 API和 Chrome → Chromium 回退语义；只允许它启动自己的浏览器和新 Context，不增加用户 Profile、Storage State 或 CDP 入口。若实现中出现这些入口，先写失败测试再拒绝该配置。

- [ ] **Step 5: 重跑浏览器相关测试**

运行：

```text
uv run --python 3.11 --no-progress pytest -p no:cacheprovider tests/test_browser_config.py tests/test_architecture_guard.py -q
```

预期：通过，且不需要连接真实用户 Chrome。

---

### Task 4: 收紧上下文阶段的写入边界和状态表达

**Files:**
- Modify: `workflow/context/prompt.md`
- Modify: `workflow/requirements/prompt.md`
- Modify: `workflow/asset-map.md`
- Modify: `AGENTS.md`
- Modify: `tests/test_directory_contracts.py`
- Modify: `tests/test_schemas.py`

- [ ] **Step 1: 添加阶段写入边界测试**

保护以下约束：上下文确认阶段只写最小 YAML、`.agentest/context.yaml`、`.agentest/state.yaml` 和原始来源登记；需求未确认时不写测试点、测试报告、测试脚本或长期 Memory / Element Map。

```python
def test_context_prompt_defers_execution_assets_until_requirements_are_ready() -> None:
    root = Path(__file__).parents[1]
    content = (root / "workflow" / "context" / "prompt.md").read_text(encoding="utf-8")

    assert "不生成测试点" in content
    assert "不执行正式测试" in content
    assert "只写入" in content
```

- [ ] **Step 2: 规范状态字段含义**

明确 `context_confirmed=True` 只表示基础上下文已确认；`pending_questions` 表示仍未解决的需求问题；`phase=requirements` 表示需求仍在审查，不得根据 `context_confirmed` 直接开始测试。

- [ ] **Step 3: 规范确认回执**

回执必须显示用户实际确认的测试地址、系统类型的中文名称、当前阶段、剩余问题和下一步，不再只显示“已登记为测试环境”。地址应保留完整 URL，包括 hash 路由；不得隐藏关键上下文导致用户无法复核。

- [ ] **Step 4: 更新资产映射和用户文档**

在 `workflow/asset-map.md`、`AGENTS.md` 和 `README.md` 中明确：结构化需求未完成前不得扩散写入多个资产；`workflow/` 只能保存公共脚手架；真实业务事实只能进入 `projects/`。

- [ ] **Step 5: 重跑目录和 Schema 测试**

运行：

```text
uv run --python 3.11 --no-progress pytest -p no:cacheprovider tests/test_directory_contracts.py tests/test_schemas.py -q
```

预期：通过，且没有新增“测试点已批准”或类似状态字段。

---

### Task 5: 明确探索后的差异确认和测试点门禁

**Files:**
- Modify: `workflow/exploration/prompt.md`
- Modify: `workflow/test-points/prompt.md`
- Modify: `workflow/requirements/prompt.md`
- Modify: `tests/test_directory_contracts.py`

- [ ] **Step 1: 规定探索前必须完成需求审查**

探索 Prompt 明确：需求目标、范围、角色、数据和关键验收标准未确认时，不启动浏览器；探索只能补足页面、流程、元素和定位信息。

- [ ] **Step 2: 规定页面差异的处理方式**

探索发现页面没有需求中的按钮、文案或流程时，记录“需求与当前实现差异”，不直接缩小需求、不把现有页面行为改写成预期结果。只有用户确认差异如何处理后，才能形成受影响的测试点。

- [ ] **Step 3: 保护测试点暂停规则**

测试点 Prompt 明确：存在影响范围或预期结果的未决问题时必须暂停提问；测试点文件生成后立即停止，不能因为探索已经完成而自动开始正式测试。

- [ ] **Step 4: 运行阶段契约测试**

运行：

```text
uv run --python 3.11 --no-progress pytest -p no:cacheprovider tests/test_directory_contracts.py -q
```

预期：通过。

---

### Task 6: 完整验收

**Files:**
- Verify only: 当前工作区

- [ ] **Step 1: 搜索过期流程措辞**

运行：

```text
rg -n -S "先打开.*Chrome|Chrome 集成|继承.*登录态|上下文已确认.*直接测试|只确认.*Project|只确认.*Version" AGENTS.md README.md prd.md workflow docs
```

确认没有残留“先打开用户 Chrome、发现登录态后再切换”或“上下文确认等于测试就绪”的规则。

- [ ] **Step 2: 运行完整测试**

运行：

```text
uv run --python 3.11 --no-progress pytest -p no:cacheprovider
```

预期：全部测试通过。

- [ ] **Step 3: 运行 Ruff**

运行：

```text
uv run --python 3.11 --no-progress ruff check .
uv run --python 3.11 --no-progress ruff format --check .
```

预期：检查通过，且没有格式化改动。

- [ ] **Step 4: 做人工流程验收**

用截图中的需求模拟一次入口对话，确认 Agent：

- 第一轮同时询问上下文、需求疑点、账号、数据和写操作风险；
- 在需求疑点未解决前不生成结构化需求或测试点；
- 页面探索前先选择内置隔离浏览器；
- 没有内置浏览器时才创建新 Playwright 会话；
- 不打开用户已有登录 Chrome；
- 需求与页面不一致时停下来确认，不擅自改写需求；
- 测试点生成后停止等待用户批准。

- [ ] **Step 5: 复核改动范围**

确认没有修改 `projects/` 真实业务资产，没有保存凭据，没有新增浏览器连接能力，没有执行 Git 操作，也没有把截图中的上一轮内容写成新的事实。

## 验收结论

完成后应满足以下结果：

1. 第一轮问题不再只是上下文收集，而是“上下文 + 需求质疑 + 测试前置条件”的完整审查。
2. 需求质疑在页面探索前发生；探索只验证页面事实，不能替代需求澄清。
3. 浏览器顺序固定为“内置隔离浏览器 → 新建 Playwright 隔离会话”，用户现有 Chrome 永不自动使用。
4. 任何无法证明浏览器隔离、业务目标或测试前置条件的情况都失败即停止。
5. 上下文确认、需求就绪、测试点批准和正式测试在状态和用户回执中清晰区分。
6. 资产写入最小化，避免出现截图中“首轮确认却编辑大量文件”的情况。
