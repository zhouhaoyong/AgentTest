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


def _agentest_capability_modules() -> set[str]:
    """当前实际存在的顶层能力模块（包目录或顶层模块），用于防止文档漏报。"""

    package = Path(__file__).parents[1] / "src" / "agentest"
    ignored = {"__init__.py", "requirement.md", "__pycache__", "py.typed"}
    names: set[str] = set()
    for entry in package.iterdir():
        if entry.name in ignored:
            continue
        if entry.is_dir():
            names.add(entry.name)
        elif entry.suffix == ".py":
            names.add(entry.stem)
    return names


def test_architecture_and_prd_document_every_capability_module() -> None:
    """系统构成类文档必须覆盖每一项实际能力模块，挡住"加了能力忘了同步文档"的漂移。"""

    root = Path(__file__).parents[1]
    modules = _agentest_capability_modules()
    documents = {
        "docs/architecture.md": (root / "docs" / "architecture.md").read_text(encoding="utf-8"),
        "prd.md": (root / "prd.md").read_text(encoding="utf-8"),
    }
    for doc_name, content in documents.items():
        missing = sorted(name for name in modules if name not in content)
        assert missing == [], f"{doc_name} 未覆盖能力模块：{missing}"
