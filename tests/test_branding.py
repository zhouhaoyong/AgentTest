from pathlib import Path


def test_user_facing_branding_uses_agenttest() -> None:
    root = Path(__file__).parents[1]
    paths = [
        *root.rglob("*.md"),
        *root.rglob("*.yaml"),
        root / "src" / "agentest" / "__init__.py",
        root / "src" / "agentest" / "browser" / "session.py",
        root / "src" / "agentest" / "schemas" / "__init__.py",
    ]
    ignored = {".git", ".venv", ".uv-cache", ".pytest_cache", ".ruff_cache", "__pycache__"}

    for path in set(paths):
        if set(path.parts) & ignored:
            continue
        content = path.read_text(encoding="utf-8")
        legacy_names = ("Agen" + "Test", "agent" + "Test")
        assert not any(legacy_name in content for legacy_name in legacy_names), path
