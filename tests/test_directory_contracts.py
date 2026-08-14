from pathlib import Path


def test_major_repository_directories_have_requirement_contracts() -> None:
    root = Path(__file__).parents[1]
    directories = [
        root,
        root / "docs",
        root / "docs" / "examples",
        root / "docs" / "superpowers",
        root / "docs" / "superpowers" / "specs",
        root / "docs" / "superpowers" / "plans",
        root / "workflow",
        root / "workflow" / "intake",
        root / "workflow" / "context",
        root / "workflow" / "requirements",
        root / "workflow" / "exploration",
        root / "workflow" / "test-points",
        root / "workflow" / "testing",
        root / "workflow" / "reporting",
        root / "workflow" / "regression",
        root / "src",
        root / "src" / "agentest",
        root / "src" / "agentest" / "browser",
        root / "src" / "agentest" / "schemas",
        root / "projects",
        root / "tests",
    ]

    missing = [
        str(directory) for directory in directories if not (directory / "requirement.md").is_file()
    ]

    assert missing == []


def test_public_scaffold_is_grouped_by_workflow_stage() -> None:
    root = Path(__file__).parents[1]
    workflow = root / "workflow"
    stages = {
        "intake",
        "context",
        "requirements",
        "exploration",
        "test-points",
        "testing",
        "reporting",
        "regression",
    }

    assert workflow.joinpath("README.md").is_file()
    assert workflow.joinpath("asset-map.md").is_file()
    assert all(workflow.joinpath(stage, "requirement.md").is_file() for stage in stages)
    assert not (root / "prompts").exists()
    assert not (root / "templates").exists()

    router = workflow.joinpath("README.md").read_text(encoding="utf-8")
    for stage in stages:
        assert f"{stage}/" in router


def test_workflow_scaffold_keeps_real_assets_in_projects() -> None:
    root = Path(__file__).parents[1]
    workflow = root / "workflow"
    asset_map = workflow.joinpath("asset-map.md").read_text(encoding="utf-8")

    assert "projects/<project>/systems/<system>/versions/<version>/" in asset_map
    assert "不得把真实资产写入 `workflow/`" in asset_map


def test_all_project_directories_have_requirement_contracts() -> None:
    root = Path(__file__).parents[1]
    ignored_names = {
        ".git",
        ".github",
        ".venv",
        ".uv-cache",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".obsidian",
        "__pycache__",
    }
    directories = [
        directory
        for directory in root.rglob("*")
        if directory.is_dir() and not (set(directory.parts) & ignored_names)
    ]
    missing = [
        str(directory) for directory in directories if not (directory / "requirement.md").is_file()
    ]

    assert missing == []


def test_directory_contracts_have_chinese_content() -> None:
    root = Path(__file__).parents[1]
    contract_paths = [
        root / "requirement.md",
        root / "AGENTS.md",
        root / "README.md",
        root / "docs" / "requirement.md",
        root / "docs" / "architecture.md",
        root / "workflow" / "README.md",
        root / "workflow" / "asset-map.md",
    ]
    contract_paths.extend(root.rglob("*.md"))

    for path in set(contract_paths):
        if set(path.parts) & {".git", ".venv", ".uv-cache", ".pytest_cache", ".ruff_cache"}:
            continue
        content = path.read_text(encoding="utf-8")
        assert any("\u4e00" <= char <= "\u9fff" for char in content), path


def test_demo_has_a_single_discoverable_entry_and_flat_examples() -> None:
    root = Path(__file__).parents[1]
    demo_entry = root / "docs" / "demo.md"
    examples_dir = root / "docs" / "examples"
    expected_examples = {
        "project.yaml",
        "system.yaml",
        "version.yaml",
        "project-requirement.md",
        "system-requirement.md",
        "element-map.md",
        "memory.md",
        "requirement.md",
        "20260814_V2026.08.04_demo-web.md",
        "test-points.md",
        "test-script.py",
        "report.md",
    }

    assert demo_entry.is_file()
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert "[Demo 总览](docs/demo.md)" in agents
    assert expected_examples <= {path.name for path in examples_dir.iterdir() if path.is_file()}
    assert not (examples_dir / "demo-project").exists()

    demo_content = demo_entry.read_text(encoding="utf-8")
    for filename in expected_examples:
        assert f"examples/{filename}" in demo_content


def test_workflow_prompts_share_a_stage_contract_and_adaptive_exploration() -> None:
    root = Path(__file__).parents[1]
    required_headings = {
        "## 进入条件",
        "## 必读资料",
        "## 决策与执行",
        "## 允许写入的位置",
        "## 交付物与移交方向",
        "## 强制停止条件",
    }
    prompt_paths = [
        root / "workflow" / stage / "prompt.md"
        for stage in (
            "intake",
            "context",
            "requirements",
            "exploration",
            "test-points",
            "testing",
            "reporting",
            "regression",
        )
    ]

    for path in prompt_paths:
        content = path.read_text(encoding="utf-8")
        assert required_headings <= set(content.splitlines()), path

    requirements_prompt = (root / "workflow" / "requirements" / "prompt.md").read_text(
        encoding="utf-8"
    )
    exploration_prompt = (root / "workflow" / "exploration" / "prompt.md").read_text(
        encoding="utf-8"
    )
    regression_prompt = (root / "workflow" / "regression" / "prompt.md").read_text(encoding="utf-8")

    assert "探索决策" in requirements_prompt
    assert "复用已有知识" in exploration_prompt
    assert "当前 Version 的完整测试点集合" in regression_prompt


def test_test_point_template_is_the_only_template_and_has_no_approval_status() -> None:
    root = Path(__file__).parents[1]
    paths = [
        root / "workflow" / "test-points" / "prompt.md",
        root / "workflow" / "test-points" / "template-test-points.md",
        root / "docs" / "examples" / "test-points.md",
    ]

    for path in paths:
        assert "状态：Draft" not in path.read_text(encoding="utf-8"), path

    prompt = paths[0].read_text(encoding="utf-8")
    assert "# 测试点\n\n状态：" not in prompt
