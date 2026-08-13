from pathlib import Path


def test_major_repository_directories_have_requirement_contracts() -> None:
    root = Path(__file__).parents[1]
    directories = [
        root,
        root / "docs",
        root / "docs" / "examples",
        root / "src",
        root / "src" / "agentest",
        root / "src" / "agentest" / "browser",
        root / "src" / "agentest" / "scaffold",
        root / "src" / "agentest" / "schemas",
        root / "templates",
        root / "projects",
        root / "tests",
    ]

    missing = [
        str(directory)
        for directory in directories
        if not (directory / "requirement.md").is_file()
    ]

    assert missing == []


def test_all_project_directories_have_requirement_contracts() -> None:
    root = Path(__file__).parents[1]
    ignored_names = {
        ".git",
        ".venv",
        ".uv-cache",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "__pycache__",
    }
    directories = [
        directory
        for directory in root.rglob("*")
        if directory.is_dir() and not (set(directory.parts) & ignored_names)
    ]
    missing = [
        str(directory)
        for directory in directories
        if not (directory / "requirement.md").is_file()
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
        root / "docs" / "workflow.md",
        root / "docs" / "asset-spec.md",
        root / "docs" / "testing-rules.md",
    ]
    contract_paths.extend(root.rglob("*.md"))

    for path in set(contract_paths):
        if set(path.parts) & {".git", ".venv", ".uv-cache", ".pytest_cache", ".ruff_cache"}:
            continue
        content = path.read_text(encoding="utf-8")
        assert any("\u4e00" <= char <= "\u9fff" for char in content), path
