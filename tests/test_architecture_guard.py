from pathlib import Path

FORBIDDEN_IMPORTS = (
    "fastapi",
    "sqlalchemy",
    "openai",
    "anthropic",
    "langchain",
    "llama_index",
)


def test_source_and_dependencies_do_not_contain_forbidden_frameworks() -> None:
    root = Path(__file__).parents[1]
    source = "\n".join(path.read_text(encoding="utf-8") for path in (root / "src").rglob("*.py"))
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")

    for forbidden in FORBIDDEN_IMPORTS:
        assert forbidden not in source.lower()
        assert forbidden not in pyproject.lower()
