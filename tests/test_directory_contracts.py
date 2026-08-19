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
        root / "workflow" / "test-cases",
        root / "workflow" / "testing",
        root / "workflow" / "reporting",
        root / "workflow" / "regression",
        root / "src",
        root / "src" / "agentest",
        root / "src" / "agentest" / "browser",
        root / "src" / "agentest" / "exploration",
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
        "test-cases",
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
        "element-map.yaml",
        "element-map.md",
        "memory.md",
        "requirement.md",
        "20260814_V2026.08.04_demo.md",
        "test-cases.md",
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
            "test-cases",
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
    assert "当前 Version 的完整测试用例集合" in regression_prompt


def test_context_prompt_asks_for_business_context_and_agent_generated_ids() -> None:
    root = Path(__file__).parents[1]
    content = (root / "workflow" / "context" / "prompt.md").read_text(encoding="utf-8")

    assert "用户只需提供业务可读名称" in content
    assert "Agent 根据名称生成目录安全 ID" in content
    assert "测试账号" in content
    assert "不是所有需求都需要" in content


def test_requirements_prompt_defers_roles_accounts_and_data_until_relevant() -> None:
    root = Path(__file__).parents[1]
    content = (root / "workflow" / "requirements" / "prompt.md").read_text(encoding="utf-8")

    assert "只有需求涉及登录、角色、权限或数据隔离时" in content
    assert "不索要密码、Token、Cookie 或 Storage State" in content


def test_intake_prompt_combines_context_and_numbered_pending_questions() -> None:
    root = Path(__file__).parents[1]
    content = (root / "workflow" / "intake" / "prompt.md").read_text(encoding="utf-8")

    for phrase in (
        "基础信息",
        "待确认需求",
        "按编号回复",
        "如果没有待确认需求，不展示这一部分",
        "需求质疑",
        "写操作风险",
    ):
        assert phrase in content


def test_requirement_review_precedes_page_exploration() -> None:
    root = Path(__file__).parents[1]
    requirements = (root / "workflow" / "requirements" / "prompt.md").read_text(encoding="utf-8")
    exploration = (root / "workflow" / "exploration" / "prompt.md").read_text(encoding="utf-8")

    assert "先审查需求" in requirements
    assert "页面探索不能替代需求审查" in exploration
    assert "页面事实差异" in exploration


def test_workflow_prompts_explain_action_and_reason() -> None:
    root = Path(__file__).parents[1]
    prompt_paths = [
        root / "workflow" / "intake" / "prompt.md",
        root / "workflow" / "context" / "prompt.md",
        root / "workflow" / "requirements" / "prompt.md",
        root / "workflow" / "exploration" / "prompt.md",
        root / "workflow" / "testing" / "prompt.md",
    ]

    for path in prompt_paths:
        content = path.read_text(encoding="utf-8")
        assert "做什么" in content, path
        assert "为什么" in content, path


def test_test_case_template_is_the_only_template_and_has_no_approval_status() -> None:
    root = Path(__file__).parents[1]
    paths = [
        root / "workflow" / "test-cases" / "prompt.md",
        root / "workflow" / "test-cases" / "template-test-cases.md",
        root / "docs" / "examples" / "test-cases.md",
    ]

    for path in paths:
        assert "状态：Draft" not in path.read_text(encoding="utf-8"), path

    prompt = paths[0].read_text(encoding="utf-8")
    assert "# 测试用例\n\n状态：" not in prompt

    template = paths[1].read_text(encoding="utf-8")
    assert "测试状态：未测试" in template
    assert "测试结果：NOT RUN" in template
    assert "【待页面核验】" not in template


def test_formal_testing_requires_explicit_start_and_uses_batch_execution() -> None:
    root = Path(__file__).parents[1]
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    prompt = (root / "workflow" / "testing" / "prompt.md").read_text(encoding="utf-8")
    rules = (root / "workflow" / "testing" / "rules.md").read_text(encoding="utf-8")

    for content in (agents, prompt, rules):
        assert "开始正式测试" in content
        assert "测试用例确认" in content
        assert "测试用例确认不等于正式测试" in content
        assert "批量生成" in content
        assert "分组调试" in content
        assert "复用同一个隔离浏览器会话" in content


def test_formal_testing_has_stall_guardrails() -> None:
    root = Path(__file__).parents[1]
    prompt = (root / "workflow" / "testing" / "prompt.md").read_text(encoding="utf-8")
    rules = (root / "workflow" / "testing" / "rules.md").read_text(encoding="utf-8")

    for content in (prompt, rules):
        assert "最多重试 1 次" in content
        assert "60 秒没有可观察进展" in content
        assert "5 分钟" in content
        assert "自动暂停" in content
        assert "当前测试用例" in content


def test_test_script_template_uses_group_session_and_explicit_environment() -> None:
    root = Path(__file__).parents[1]
    template = (root / "workflow" / "testing" / "template-test-script.py").read_text(
        encoding="utf-8"
    )
    contract = (
        root / "workflow" / "testing" / "template-test-scripts-directory-requirement.md"
    ).read_text(encoding="utf-8")

    assert 'pytest.fixture(scope="module")' in template
    assert "TestEnvironment" in template
    assert "browser" in template
    assert "主 Page" in contract
    assert "辅助 Page" in contract
    assert "测试组级 Session" in contract


def test_memory_rules_require_reusable_fact_metadata() -> None:
    root = Path(__file__).parents[1]
    prompt = (root / "workflow" / "exploration" / "prompt.md").read_text(encoding="utf-8")
    contract = (
        root / "workflow" / "exploration" / "template-memory-directory-requirement.md"
    ).read_text(encoding="utf-8")

    for content in (prompt, contract):
        assert "验证 Version" in content
        assert "长期用途" in content
        assert "稳定事实" in content
        assert "一次性测试结果" in content
