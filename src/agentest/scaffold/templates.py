from pathlib import Path


def template_root() -> Path:
    return Path(__file__).resolve().parents[3] / "templates"


def read_template(name: str) -> str:
    path = template_root() / name
    if not path.is_file():
        raise RuntimeError(f"Missing AgentTest template: {path}")
    return path.read_text(encoding="utf-8")
