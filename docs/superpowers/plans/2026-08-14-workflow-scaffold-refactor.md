# Workflow Scaffold Refactor Implementation Plan

本计划将按测试先行方式执行，不改变真实业务测试资产的位置。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the public scaffold around workflow stages, keep real assets in `projects/`, and correct the discovered schema defects.

**Architecture:** `workflow/README.md` routes user intent to one stage; each stage co-locates its Prompt, templates, rules and contract. `projects/` remains the only destination for real test assets. Test environment configuration distinguishes resolved settings from partial overrides.

**Tech Stack:** Python 3.13, Pydantic v2, PyYAML, pytest, Ruff, Markdown.

---

### Task 1: Lock down intended behavior with tests

**Files:**
- Modify: `tests/test_schemas.py`
- Modify: `tests/test_directory_contracts.py`

- [ ] Add tests that reject `.` and `..` for every asset ID consumer.
- [ ] Add tests that a mobile System preserves its mobile defaults when only a System environment locale is declared.
- [ ] Add tests that a Version can override only viewport width or height and preserves System settings through YAML serialization and reload.
- [ ] Replace public-structure assertions with checks for `workflow/`, all stage contracts, `workflow/README.md` intent routing, and no root `prompts/` or `templates/` directory.
- [ ] Run the focused tests and verify they fail for the intended missing behavior.

### Task 2: Implement schema corrections

**Files:**
- Modify: `src/agentest/schemas/common.py`
- Modify: `src/agentest/schemas/system.py`
- Modify: `src/agentest/schemas/version.py`
- Modify: `src/agentest/schemas/__init__.py`

- [ ] Reject `.` and `..` in `validate_asset_id`.
- [ ] Add a partial viewport and environment override schema with all optional fields.
- [ ] Build System environments by applying explicit fields over type defaults.
- [ ] Merge Version overrides field-by-field, including an independently partial viewport.
- [ ] Ensure `VersionConfig.model_dump()` writes only declared override values for its environment.
- [ ] Run schema tests and then the complete test suite.

### Task 3: Rehome public scaffold by workflow stage

**Files:**
- Create: `workflow/**`
- Delete: `prompts/**`
- Delete: `templates/**`
- Delete: `docs/workflow.md`
- Delete: `docs/asset-spec.md`
- Delete: `docs/testing-rules.md`

- [ ] Create the workflow root router, contract and asset map.
- [ ] Move each former prompt and related template into its stage directory with `template-` names.
- [ ] Add context and exploration prompts; keep intake as an orchestration-only entry.
- [ ] Move workflow, asset and testing rules into the workflow root, testing stage and asset map respectively.
- [ ] Add stage contracts and the minimal Test Case-linked Playwright template.
- [ ] Update template contents to use their co-located workflow paths and accurate scope.

### Task 4: Update all rule and documentation references

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `prd.md`
- Modify: `docs/requirement.md`
- Modify: `docs/demo.md`
- Modify: `.agentest/requirement.md`

- [ ] Require user-intent routing through `workflow/README.md` in `AGENTS.md`.
- [ ] Replace all old prompt/template/docs references with new workflow paths.
- [ ] Describe the separation of public workflow scaffold and real assets consistently.
- [ ] Ensure the Demo and directory contracts still describe only current files.

### Task 5: Final verification

**Files:**
- Modify only if verification exposes a defect.

- [ ] Search all repository text for stale root `prompts/`, `templates/`, and retired docs paths.
- [ ] Run `python -m pytest -q` and verify zero failures.
- [ ] Run `python -m ruff check src tests` and verify zero violations.
- [ ] Validate public YAML examples and templates with the relevant schemas.
