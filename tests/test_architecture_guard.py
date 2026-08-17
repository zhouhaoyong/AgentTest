from pathlib import Path

FORBIDDEN_IMPORTS = (
    "fastapi",
    "sqlalchemy",
    "openai",
    "anthropic",
    "langchain",
    "llama_index",
)


def test_runtime_baseline_is_python_311() -> None:
    root = Path(__file__).parents[1]

    assert (root / ".python-version").read_text(encoding="utf-8").strip() == "3.11"
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in pyproject
    assert 'target-version = "py311"' in pyproject
    assert "- Python `>= 3.11`" in (root / "prd.md").read_text(encoding="utf-8")


def test_user_facing_browser_guidance_hides_mcp_details() -> None:
    root = Path(__file__).parents[1]

    for path in [root / "README.md", root / "prd.md", root / "workflow" / "testing" / "rules.md"]:
        assert "MCP" not in path.read_text(encoding="utf-8")


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
    assert "禁止复用用户当前已打开的浏览器窗口、Tab、Profile 或地址" in content
    assert "无法确认隔离" in content


def test_source_and_dependencies_do_not_contain_forbidden_frameworks() -> None:
    root = Path(__file__).parents[1]
    source = "\n".join(path.read_text(encoding="utf-8") for path in (root / "src").rglob("*.py"))
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")

    for forbidden in FORBIDDEN_IMPORTS:
        assert forbidden not in source.lower()
        assert forbidden not in pyproject.lower()
