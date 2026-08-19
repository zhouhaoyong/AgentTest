# Workflow Integrity Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Make user requirements, execution facts, environment scope, scripts, evidence and report conclusions pass through auditable workflow gates before confirmation, test start and delivery.

**Architecture:** Keep Markdown and YAML as the only sources of truth. Extend the existing pure parsers and asset audit for Version-level facts, add a focused project/workflow gate module for context and linked-end resolution, and make prompts invoke these pure checks at the three workflow boundaries. A disposable end-to-end fixture protects the complete file flow without accessing a real browser or business system.

**Tech Stack:** Python 3.11, Pydantic v2, PyYAML, pytest, Ruff, Markdown/YAML workflow assets.

**Spec:** docs/superpowers/specs/2026-08-19-workflow-integrity-gates-design.md

## Global Constraints

- Markdown and YAML remain the only business-test facts; no database, runtime service, browser extension, remote API or fixed CLI entry point.
- Do not modify real assets under projects/ and do not create a sample business Project there.
- Do not store credentials, cookies, tokens, storage state, one-off business identifiers or sensitive evidence.
- Version test_url is the only executable test address; an empty address blocks formal testing.
- Do not perform Git commands, commits, branches, merges or resets unless the user explicitly requests them.
- Workflow gates are pure read-only Python functions returning AssetAuditIssue values; they must not create, overwrite or delete assets.
- All user-facing workflow prompts and generated narrative assets remain in simplified Chinese; page literals and selectors remain verbatim.

---

## File Structure

- Modify: src/agentest/test_cases.py — parse key coverage constraints, keep execution fields out of the approved-scope digest, and expose a structured constraint result.
- Modify: tests/test_test_cases.py — protect the scope behavior of key coverage constraints.
- Modify: src/agentest/asset_audit.py — validate constraints, derive one outcome mapping, reconcile test-case/state/report facts, and verify script declarations.
- Modify: tests/test_asset_audit.py — create focused fixtures for each Version-level integrity failure.
- Create: src/agentest/workflow_gates.py — compose read-only project, context, linked-end and phase-gate checks.
- Modify: src/agentest/schemas/workspace.py — require the current Version in a confirmed workspace context.
- Modify: src/agentest/schemas/__init__.py — export any newly public gate types only when needed by callers.
- Modify: tests/test_schemas.py — cover required current Version behavior without changing YAML compatibility rules.
- Create: tests/test_workflow_gates.py — use temporary asset trees to test confirmation, test-start and delivery gates.
- Create: src/agentest/exploration/session.py — provide one workflow-facing coordinator that uses existing budget, discovery and scoring helpers.
- Modify: src/agentest/exploration/__init__.py — export the coordinator.
- Create: tests/test_exploration_session.py — verify a single exploration session actually applies stop budgets and batch candidate discovery.
- Modify: workflow/test-cases/template-test-cases.md, workflow/test-cases/prompt.md — introduce KC-xxx and require the confirmation gate.
- Modify: workflow/testing/prompt.md, workflow/testing/rules.md, workflow/regression/prompt.md — require the test-start and delivery gates and use the new result/script rules.
- Modify: workflow/context/prompt.md, workflow/context/template-system.yaml, workflow/context/template-version.yaml — make Version test_url the only executable address and require explicit linked versions before testing.
- Modify: workflow/reporting/template-report.md, workflow/reporting/prompt.md — add the key-constraint completion table and correct report section references.
- Modify: workflow/exploration/prompt.md — instruct exploration work to use ExplorationSession instead of only repeating soft budgets.
- Modify: AGENTS.md, README.md, prd.md, workflow/README.md — align the workflow contract, address source, linked-end resolution and gate boundaries.
- Modify: docs/demo.md, docs/examples/test-cases.md, docs/examples/test-script.py, docs/examples/report.md — bring the mandatory first-read example into line with the public templates.
- Create: tests/test_workflow_documentation.py — protect template/Demo concepts and section references.

## Task 1: Protect key coverage constraints in the approved scope

**Files:**
- Modify: src/agentest/test_cases.py
- Modify: tests/test_test_cases.py
- Modify: workflow/test-cases/template-test-cases.md

**Interfaces:**
- Produces: \`KeyCoverageConstraint(id: str, user_requirement: str, test_case_ids: tuple[str, ...], completion_criteria: str)\`.
- Produces: \`parse_key_coverage_constraints(content: str) -> tuple[list[KeyCoverageConstraint], list[KeyCoverageParseIssue]]\`.
- Produces: \`fingerprint_test_case_scope(content: str) -> str\`, now including business requirements, linked Test Case IDs and completion criteria from each KC-xxx block while excluding its current execution status.
- Consumed by: Version asset audit and report-delivery gate in Tasks 2 and 3.

- [ ] **Step 1: Write failing fingerprint and parser tests**

Add cases in tests/test_test_cases.py using this representative block:

\`\`\`markdown
### 关键覆盖约束

#### KC-001 至少验证两个订单列表
- 用户要求：至少验证两个订单列表。
- 承接用例：TC-001、TC-002
- 完成标准：两个用例均完整执行且 PASS。
- 当前状态：未开始
\`\`\`

Assert that changing 用户要求、承接用例 or 完成标准 changes the digest; changing only 当前状态 does not. Assert that parse_key_coverage_constraints returns KC-001 and the two IDs, and that an empty or malformed block is representable for the audit to reject.

- [ ] **Step 2: Run the new tests and confirm the missing behavior**

Run: \`python -m pytest tests/test_test_cases.py -q\`

Expected: at least the new key-coverage digest/parser tests fail because the current digest ignores the level-three section and no structured parser exists.

- [ ] **Step 3: Implement the constrained parser and digest inclusion**

In src/agentest/test_cases.py:

1. Add a frozen KeyCoverageConstraint dataclass and a KeyCoverageParseIssue dataclass with a code and business-readable message.
2. Locate only the section headed “关键覆盖约束”; parse its level-four KC-<number> children and their four named fields.
3. Normalize referenced TC IDs with the existing TC pattern, preserving sorted IDs in the parsed object.
4. Include normalized KC ID, user requirement, referenced IDs and completion criteria in _scope_lines.
5. Explicitly exclude 当前状态 and any execution/result fields from the digest.
6. Export only the parser, parser issue type and constraint type that Task 2 needs.

Use the following shape:

\`\`\`python
@dataclass(frozen=True)
class KeyCoverageConstraint:
    id: str
    user_requirement: str
    test_case_ids: tuple[str, ...]
    completion_criteria: str

def parse_key_coverage_constraints(
    content: str,
) -> tuple[list[KeyCoverageConstraint], list[KeyCoverageParseIssue]]:
    ...
\`\`\`

- [ ] **Step 4: Update the Test Case template**

Replace the free-form comment under “关键覆盖约束” with one KC-001 example containing 用户要求、承接用例、完成标准 and 当前状态. Keep the example as a comment so new test assets start clean, but make the required structure unambiguous.

- [ ] **Step 5: Run focused regression**

Run: \`python -m pytest tests/test_test_cases.py -q\`

Expected: PASS, including existing guarantees that status/result/coverage changes do not alter the approved-scope digest.

## Task 2: Make Version results, scripts and report conclusion agree

**Files:**
- Modify: src/agentest/asset_audit.py
- Modify: tests/test_asset_audit.py
- Modify: workflow/reporting/template-report.md

**Interfaces:**
- Consumes: \`parse_key_coverage_constraints(content)\` and the current parsed Test Case blocks.
- Produces: \`CaseExecution(coverage: str, display_result: str, state_result: str | None)\` internally for consistent outcome checks.
- Produces: additional AssetAuditIssue codes for invalid key coverage, outcome mismatch, script declaration mismatch and key-coverage report mismatch.
- Consumed by: the Version audit and delivery gate in Task 3.

- [ ] **Step 1: Write failing Version-audit tests**

Add fixtures in tests/test_asset_audit.py for all of these cases:

1. KC-001 refers to TC-999 and returns an invalid-key-coverage issue.
2. state.yaml says TC-001 is passed while the Test Case says BLOCKED with 部分 coverage.
3. a report says PASS while the Test Case and state both say BLOCKED.
4. a report declares “是否可宣称通过：是” when a key coverage row is 部分阻塞.
5. a script header declares 覆盖用例：TC-002 but the report attributes that script to TC-001.
6. a script declares an ID outside the current Test Case range.
7. a valid report has a key coverage completion table matching KC-001 and is accepted.

Use a full script header in valid fixtures:

\`\`\`python
# 覆盖用例：TC-001
# 前置条件：已进入测试环境。
# 手动登录：需要登录时由用户手动登录并确认。
# 运行方式：python -m pytest test-scripts/orders.py
# 缺少数据时：记录 BLOCKED，不把数据缺口记为业务缺陷。
# 结果判断：完整覆盖后才记录 PASS 或 FAIL。
\`\`\`

- [ ] **Step 2: Run the new audit tests and confirm they fail**

Run: \`python -m pytest tests/test_asset_audit.py -q\`

Expected: the new mismatch cases fail because the audit currently validates each file mostly in isolation and only checks that a script contains a Test Case-looking string.

- [ ] **Step 3: Add a single outcome mapping and cross-record comparison**

In src/agentest/asset_audit.py:

1. Define one mapping from (执行覆盖, 测试结果) to state.yaml values:

\`\`\`python
_DISPLAY_TO_STATE_OUTCOME = {
    ("完整", "PASS"): "passed",
    ("完整", "FAIL"): "failed",
    ("部分", "BLOCKED"): "blocked",
    ("未执行", "BLOCKED"): "blocked",
    ("未执行", "NOT RUN"): "not_run",
}
\`\`\`

2. Parse every Test Case’s coverage/result once, emit the existing coverage/result errors first, then compare valid pairs to state.yaml results.
3. Parse report rows with the existing header-aware table parser and compare them to the same Test Case execution map and state result map.
4. Keep state.yaml progress semantics intact: not_run must not appear in completed_test_case_ids; passed/failed/blocked require a completed ID.
5. Return business-readable issue codes such as test_case_state_result_mismatch and report_state_result_mismatch rather than silently choosing a winner.

- [ ] **Step 4: Validate key coverage and its report completion table**

Extend the Version audit to:

1. Parse key coverage constraints from test-cases.md.
2. Reject missing KC blocks when a Test Case document claims it has key coverage, duplicate KC IDs, blank required fields and references outside the Test Case range.
3. Determine each KC’s expected delivery state from its mapped Test Case execution records: 已满足 only when every referenced case is complete PASS; 未满足 when any referenced case is FAIL; 部分阻塞 otherwise.
4. Parse the report’s “关键覆盖约束完成情况” table with columns 约束、承接用例、状态、说明.
5. Reject a report table whose IDs, referenced Test Cases or statuses differ from the calculated state.
6. Make a failed or blocked KC force “是否可宣称通过：否”.

- [ ] **Step 5: Replace superficial script matching with declared coverage**

Require every Python test script to contain one 覆盖用例 field. Parse only TC IDs from that declaration, then:

1. reject blank declarations and IDs outside the approved Test Case range;
2. ensure each report row with a script points to a real script;
3. ensure that script declares the same Test Case ID as the report row;
4. require each PASS, FAIL or BLOCKED report row to name a script that declares the case;
5. preserve NOT RUN rows without a script when no test was started.

Retain the existing prerequisite, manual-login, run-command, data-gap and result-judgement metadata checks.

- [ ] **Step 6: Correct the report template**

Place “关键覆盖约束完成情况” immediately after Test Case results, move the numeric summary to the correct following section, and update every internal comment and “详见” reference to the real section number. Keep the first-screen conclusion and its four counts at the top.

- [ ] **Step 7: Run focused regression**

Run: \`python -m pytest tests/test_asset_audit.py -q\`

Expected: PASS; valid fixtures retain their accepted status and every new cross-record contradiction is rejected.

## Task 3: Add project-level facts and the three workflow gates

**Files:**
- Create: src/agentest/workflow_gates.py
- Modify: src/agentest/schemas/workspace.py
- Modify: src/agentest/schemas/__init__.py
- Modify: tests/test_schemas.py
- Create: tests/test_workflow_gates.py

**Interfaces:**
- Produces: \`WorkflowGateStage = Literal["test_case_confirmation", "formal_test_start", "report_delivery"]\`.
- Produces: \`audit_workflow_gate(workspace_root: Path, stage: WorkflowGateStage) -> list[AssetAuditIssue]\`.
- Consumes: .agentest/context.yaml, .agentest/state.yaml, project.yaml, system.yaml, version.yaml, \`audit_version_assets\`, \`load_yaml_model\`, \`ProjectConfig\`, \`SystemConfig\`, \`VersionConfig\` and \`WorkspaceContext\`.
- Guarantees: no write, no browser invocation, no filesystem mutation.
- Consumed by: prompts and documentation in Task 5; golden fixture in Task 6.

- [ ] **Step 1: Write failing schema and gate tests**

In tests/test_schemas.py, change the minimal confirmed WorkspaceContext fixture to include version_id and add a test that an empty version_id is rejected.

Create tests/test_workflow_gates.py with a helper that writes:

\`\`\`text
<tmp>/
  .agentest/context.yaml
  .agentest/state.yaml
  projects/demo/project.yaml
  projects/demo/systems/orders/system.yaml
  projects/demo/systems/orders/versions/v1/version.yaml
\`\`\`

Cover these failures:

1. Context points to a missing Project, System or Version.
2. version.yaml fails its Pydantic schema.
3. test_url is empty even when system.yaml has base_url.
4. linked=true has an end whose System or Version directory is absent.
5. linked end omits version_id at the formal-test-start gate.
6. linked end points to a Version whose test_url is empty.
7. report-delivery gate propagates a Version audit contradiction.

Cover one valid single-System confirmation gate and one valid explicit linked-end test-start gate.

- [ ] **Step 2: Run gate tests and confirm they fail**

Run: \`python -m pytest tests/test_schemas.py tests/test_workflow_gates.py -q\`

Expected: tests for required version_id and audit_workflow_gate fail because WorkspaceContext currently permits an empty Version and no project-level gate exists.

- [ ] **Step 3: Require a current Version in workspace context**

In src/agentest/schemas/workspace.py, make version_id use the same non-empty directory-safe validation as project_id and system_id. Do not change VersionConfig’s acceptance of an empty test_url: a blank address remains valid YAML but is rejected only by the formal-test-start gate.

- [ ] **Step 4: Implement the read-only gate compositor**

Create src/agentest/workflow_gates.py with:

\`\`\`python
WorkflowGateStage = Literal[
    "test_case_confirmation",
    "formal_test_start",
    "report_delivery",
]

def audit_workflow_gate(
    workspace_root: Path,
    stage: WorkflowGateStage,
) -> list[AssetAuditIssue]:
    ...
\`\`\`

Implementation sequence:

1. Load context.yaml through WorkspaceContext; return a context issue instead of raising when absent or invalid.
2. Resolve project, system and version paths only from validated IDs.
3. Load project.yaml, system.yaml and version.yaml through their Pydantic models; report each invalid source file.
4. For all stages, use the selected Version and state path to call audit_version_assets.
5. At test_case_confirmation, require a valid key-coverage/Test Case relationship and a non-empty current test_url.
6. At formal_test_start, require the approved-scope fingerprint, current non-empty test_url, and explicit valid linked ends.
7. Resolve every linked end relative to the current Project. Reject missing target directories, invalid target YAML, blank target test_url, self references and omitted version_id.
8. At report_delivery, call the execution-assets audit and therefore enforce result, report, script, evidence and key-coverage consistency.
9. Preserve first-seen issue order and de-duplicate an identical code/path/message triple.

Add public exports in schemas/__init__.py only for model types already treated as public; export workflow-gate API from its own module rather than expanding the schemas package with unrelated behavior.

- [ ] **Step 5: Run focused gate regression**

Run: \`python -m pytest tests/test_schemas.py tests/test_workflow_gates.py -q\`

Expected: PASS; test_url fallback from system.yaml is rejected and every linked endpoint resolves to an explicit usable Version.

## Task 4: Connect exploration stop rules to a workflow-facing session

**Files:**
- Create: src/agentest/exploration/session.py
- Modify: src/agentest/exploration/__init__.py
- Create: tests/test_exploration_session.py
- Modify: workflow/exploration/prompt.md

**Interfaces:**
- Consumes: ExplorationBudget, LocatorCandidate, Discovery and discover from the existing exploration package.
- Produces: \`ExplorationSession(page: PageLike, budget: ExplorationBudget)\`.
- Produces: \`begin_entry(entry_key: str) -> StopDecision\`, \`record_navigation(success: bool) -> StopDecision\`, and \`discover_candidates(candidates: list[LocatorCandidate]) -> list[Discovery]\`.
- Guarantees: candidate discovery shares the one session budget; a stop decision prevents later candidate attempts and exposes the stopping reason.

- [ ] **Step 1: Write failing coordinator tests**

Create tests/test_exploration_session.py with a fake Page exposing the same get_by_* and locator methods used by tests/test_exploration_discovery.py.

Test that:

1. repeated failed navigation for one entry returns entry_retry_exhausted and later discovery returns no new candidate attempts;
2. a successful navigation records progress and allows one batched discovery call;
3. candidate discovery calls the existing discovery path with the same budget, orders candidates as before, and exposes the budget stopping reason;
4. the session has no file writes and does not instantiate a browser.

- [ ] **Step 2: Run the new session tests and confirm they fail**

Run: \`python -m pytest tests/test_exploration_session.py -q\`

Expected: FAIL because no workflow-facing ExplorationSession exists.

- [ ] **Step 3: Implement the minimal session coordinator**

In src/agentest/exploration/session.py:

1. Define a small PageLike Protocol only for the locator calls already supported by discovery.py.
2. Store page, budget, active entry and stopped reason in ExplorationSession.
3. Route begin_entry through budget.start_entry and return budget.should_stop().
4. Route record_navigation through budget.record_attempt and call budget.record_progress only on success.
5. Pass the same budget to discover; once budget.should_stop().stop is true, return an empty list without calling page.
6. Export ExplorationSession from exploration/__init__.py.

Do not add persistence, browser startup, a command-line entry point or automatic Element Map writing.

- [ ] **Step 4: Update the exploration prompt**

In workflow/exploration/prompt.md, replace approximate retry/time wording with a requirement to create one ExplorationSession per explored module, record navigation success/failure through it, batch locator candidates through it, and stop when it returns a stop decision. Keep the existing business-language report and Element Map requirements.

- [ ] **Step 5: Run focused regression**

Run: \`python -m pytest tests/test_exploration_budget.py tests/test_exploration_discovery.py tests/test_exploration_scoring.py tests/test_exploration_session.py -q\`

Expected: PASS; existing pure logic keeps its behavior and the new coordinator proves a workflow call point.

## Task 5: Make templates, prompts, product rules and Demo state one consistent workflow

**Files:**
- Modify: workflow/test-cases/prompt.md
- Modify: workflow/testing/prompt.md
- Modify: workflow/testing/rules.md
- Modify: workflow/regression/prompt.md
- Modify: workflow/context/prompt.md
- Modify: workflow/context/template-system.yaml
- Modify: workflow/context/template-version.yaml
- Modify: workflow/reporting/prompt.md
- Modify: workflow/README.md
- Modify: AGENTS.md
- Modify: README.md
- Modify: prd.md
- Modify: docs/demo.md
- Modify: docs/examples/test-cases.md
- Modify: docs/examples/test-script.py
- Modify: docs/examples/report.md
- Create: tests/test_workflow_documentation.py

**Interfaces:**
- Consumes: audit_workflow_gate stage names, KC-xxx format, script header fields and Version-only test address rule from Tasks 1–4.
- Produces: public instructions that direct a conforming Agent to the same three gates used by the code.
- Produces: Demo files containing all mandatory facts represented by current templates.

- [ ] **Step 1: Write failing documentation-contract tests**

Create tests/test_workflow_documentation.py and assert:

1. Test Case template and Demo Test Case example both include KC-001, 用户要求, 承接用例, 完成标准 and 当前状态.
2. Script template/example use 覆盖用例 plus all six required metadata concepts.
3. Report template/example include the top conclusion, key coverage table and a correct reference to the actual numeric-summary section.
4. Context, testing, reporting and regression prompts name the required gate stage at the correct handoff point.
5. README, AGENTS and PRD say Version test_url is the executable address and do not describe system base_url as an execution fallback.
6. Demo lists the evidence directory and explains its contract.

- [ ] **Step 2: Run documentation-contract tests and confirm they fail**

Run: \`python -m pytest tests/test_workflow_documentation.py -q\`

Expected: FAIL because Demo and product documents still retain older address and report-section wording and do not yet require all gates.

- [ ] **Step 3: Update templates and phase prompts**

Apply the following exact behavioral rules:

1. Test-case generation writes KC-xxx blocks and calls the test_case_confirmation gate before asking the user to approve.
2. Formal testing calls formal_test_start before opening an isolated browser and report_delivery before presenting the report.
3. Regression follows the same start and delivery gates; it does not bypass the approved scope.
4. Reporting renders calculated KC state and refuses a passing conclusion with FAIL, BLOCKED, NOT RUN, zero effective execution or an unmet KC.
5. Context uses Version test_url as the only executable address; System base_url is described only as a non-executable compatibility/history field.
6. A linked end must name an explicit Version before the user is asked to approve formal linked testing.
7. Prompts explain the gate as an internal read-only check and continue to use business language when reporting a failure.

- [ ] **Step 4: Synchronize product documents and Demo**

Update AGENTS.md, README.md and prd.md to use the same terms and boundaries. Update docs/demo.md and its examples so a first-time reader sees:

1. Version-scoped test_url.
2. KC-001 linked to two sample Test Cases.
3. a script header declaring coverage, manual login, data-gap behavior and result judgement.
4. an evidence directory contract.
5. the result summary near the top of the report and the KC completion table before the numerical summary.

Preserve all example system UI literals exactly as examples and do not add actual credentials or business IDs.

- [ ] **Step 5: Run documentation regression**

Run: \`python -m pytest tests/test_workflow_documentation.py -q\`

Expected: PASS; every mandatory reader-facing asset agrees with the machine-checked workflow.

## Task 6: Protect the full workflow with a disposable golden fixture and final verification

**Files:**
- Modify: tests/test_workflow_gates.py
- Modify: tests/test_asset_audit.py
- Modify: tests/test_workflow_documentation.py
- Modify: docs/superpowers/specs/2026-08-19-workflow-integrity-gates-design.md only if implementation reveals and resolves a genuine design inconsistency.

**Interfaces:**
- Consumes: the three gate stages, temporary file-tree fixtures, and all parsers/audits from Tasks 1–5.
- Produces: an end-to-end test that reaches confirmation, formal-test start and report delivery with no real browser or business Project.

- [ ] **Step 1: Write the golden fixture before final implementation adjustments**

In tests/test_workflow_gates.py, construct one temporary workspace containing:

1. context and state pointing to one Version;
2. valid Project/System/Version YAML with Version test_url;
3. a structured requirement and Test Case document with KC-001 mapping TC-001 and TC-002;
4. an approved fingerprint;
5. scripts declaring TC coverage;
6. complete Test Case execution fields, matching state results, evidence contract and matching report rows/KC states/conclusion.

Assert all three audit_workflow_gate stages return no issues. Then parameterize focused mutations:

- change KC completion standard after approval;
- remove one of the two KC-linked Test Cases;
- change a state result to passed while the Test Case is BLOCKED;
- set a linked target’s test_url to blank;
- make a report claim passing with a blocked KC;
- change a script declaration away from its report Test Case.

Each mutation must return at least one issue at the relevant stage.

- [ ] **Step 2: Run the golden fixture and confirm the intended failures are caught**

Run: \`python -m pytest tests/test_workflow_gates.py -q\`

Expected: PASS after Tasks 1–5; every valid fixture passes and every isolated mutation is rejected.

- [ ] **Step 3: Run static checks and the full suite**

Run: \`ruff check src tests\`

Expected: PASS.

Run: \`python -m pytest -q\`

Expected: PASS with the existing suite plus the new coverage.

- [ ] **Step 4: Perform final asset/doc review**

Read the changed templates, prompts and Demo together. Confirm:

1. no sentence still tells an Agent to fall back from Version test_url to System base_url;
2. every gate name in documentation matches WorkflowGateStage exactly;
3. every required script metadata phrase matches the audit parser;
4. report section references identify the actual summary section;
5. no real projects/ assets were modified;
6. no sensitive data was introduced.

- [ ] **Step 5: Report completion evidence**

Provide the user with a concise Chinese summary organized by the nine original business problems, list the changed public behavior, and report the exact Ruff/Pytest results. Do not claim success unless both final commands completed successfully.
