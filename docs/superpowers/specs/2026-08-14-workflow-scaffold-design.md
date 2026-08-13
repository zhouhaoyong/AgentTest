# Workflow Scaffold Design

本设计记录 AgentTest 工作流脚手架重构的已确认方案。

## Goal

将公共脚手架按 AgentTest 用户工作流聚合到唯一的 `workflow/` 目录，使 Agent 能先路由用户意图、再读取当前阶段的 Prompt、模板和规则；真实业务测试资产继续只写入 `projects/` 的既有层级。

## Scope and boundaries

- 移除根目录 `prompts/` 与 `templates/`，不保留旧路径兼容层。
- `workflow/` 仅保存公共 Prompt、模板、契约、规则和资产映射；不得保存真实 Project、需求、测试结果、凭据或运行状态。
- `.agentest/` 继续保存可续接的最小上下文和阶段状态；`projects/` 继续是业务事实与测试沉淀的唯一位置。
- `docs/` 保留架构、Demo 与示例。原有工作流、资产规范和测试规则移动到相应 `workflow/` 位置。
- 同时修复目录安全 ID、Version 局部环境覆盖和移动端局部环境覆盖问题。

## Public scaffold layout

```text
workflow/
├── README.md
├── requirement.md
├── asset-map.md
├── intake/
│   ├── requirement.md
│   └── prompt.md
├── context/
│   ├── requirement.md
│   ├── prompt.md
│   ├── template-project.yaml
│   ├── template-project-requirement.md
│   ├── template-systems-requirement.md
│   ├── template-system.yaml
│   ├── template-system-requirement.md
│   ├── template-versions-requirement.md
│   ├── template-version.yaml
│   ├── template-version-requirement.md
│   └── template-workspace-requirement.md
├── requirements/
├── analysis/
├── exploration/
├── test-points/
├── testing/
├── reporting/
└── regression/
```

Each stage contains its own `requirement.md`. Its `prompt.md`, rules and templates live in the same directory whenever the stage needs them. Template names begin with `template-` so they cannot be mistaken for final assets.

## Intent routing and agent behavior

`workflow/README.md` is the sole public workflow entry. It maps a user request plus `.agentest/state.yaml` to exactly one stage. The root `AGENTS.md` requires the Agent to read this router first, then the chosen stage contract and prompt.

- Raw requirement: `intake/`, which orchestrates context → requirements → exploration → test points and stops for approval.
- Context setup or selection: `context/`.
- Requirement organization: `requirements/`.
- System exploration and reusable knowledge: `exploration/`.
- Test-point design: `test-points/`, then mandatory approval wait.
- Approved execution: `testing/`.
- Report-only request: `reporting/`, without browser testing.
- Confirmed bug regression: `regression/`.

When intent conflicts with the persisted state or lacks key authorization, the Agent pauses for clarification rather than selecting a later stage itself.

## Prompt and template improvements

- Keep `intake` orchestral: it links to stage-specific instructions instead of duplicating them.
- Add independent `context/prompt.md` and `exploration/prompt.md` to remove two implicit stages.
- Clarify every stage's entry condition, required reads, allowed `projects/...` writes, handoff and stop condition.
- Remove the contradiction that a simple requirement should both skip analysis and keep an empty analysis template: simple requirements do not create `analysis/`.
- Add a minimal reusable Playwright script template tied to stable Test Point IDs.
- Constrain report Bug status to `Open`, `Fixed Pending Regression`, `Regressed` or `Closed`.
- Normalize `.agentest` contracts to describe `system_type` and Storage State consistently.

## Environment schema behavior

`TestEnvironment` remains the fully resolved browser configuration. A new partial override model represents only fields actually supplied by a Version. A partial viewport permits either width or height.

System construction begins from type-specific defaults and applies any declared System environment fields. Version resolution begins from the System result and applies the Version override. Serializing a Version model preserves only explicitly supplied environment fields, so a YAML round trip cannot inject web defaults over a mobile System configuration.

## ID safety behavior

Asset IDs continue to accept letters, digits, dots, underscores and hyphens, but reject the path segments `.` and `..`. This keeps version identifiers such as `v0.0.1` valid while preventing a directory path from resolving to a parent or current directory.

## Verification

Tests prove the public workflow router and stage contracts exist, old public directories are absent, and all documentation links use the new paths. Schema tests cover `.` and `..`, partial viewport fields, mobile System partial overrides, and Version YAML round trips. The full pytest suite and Ruff run must pass.
