from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from agentest.browser.doctor import (
    check_chromium,
    check_chromium_launch,
    check_playwright_package,
    check_projects_writable,
    check_python,
)
from agentest.scaffold.common import ScaffoldError
from agentest.scaffold.project import create_project
from agentest.scaffold.system import create_system
from agentest.scaffold.version import create_version

app = typer.Typer(help="AgentTest lightweight testing scaffold.")
_current_root = Path(".")


@app.callback()
def main(
    root: Annotated[Path, typer.Option(help="Repository root containing projects/")] = Path("."),
) -> None:
    global _current_root
    _current_root = root.resolve()


def _projects_root() -> Path:
    return _current_root / "projects"


@app.command()
def doctor() -> None:
    """Check the local AgentTest and browser environment."""
    root = _current_root
    checks = [
        check_python(),
        check_playwright_package(),
        check_chromium(),
        check_chromium_launch(),
        check_projects_writable(root / "projects"),
    ]
    typer.echo("AgentTest Doctor")
    for ok, label in checks:
        typer.echo(f"{'PASS' if ok else 'FAIL'} {label}")
    if not checks[2][0]:
        typer.echo("Chromium is not installed. Run: uv run playwright install chromium")
    if not all(ok for ok, _ in checks):
        raise typer.Exit(code=1)


@app.command("create-project")
def create_project_command(
    project_id: str,
    name: Annotated[str, typer.Option("--name")],
    description: Annotated[str, typer.Option("--description")] = "",
) -> None:
    """Create a Project asset tree without overwriting existing data."""
    _run_create(lambda: create_project(_projects_root(), project_id, name, description))


@app.command("create-system")
def create_system_command(
    project_id: str,
    system_id: str,
    name: Annotated[str, typer.Option("--name")],
    system_type: Annotated[str, typer.Option("--type")] = "web",
    base_url: Annotated[str, typer.Option("--base-url")] = "",
    description: Annotated[str, typer.Option("--description")] = "",
) -> None:
    """Create a System asset tree without overwriting existing data."""
    _run_create(
        lambda: create_system(
            _projects_root(), project_id, system_id, name, system_type, base_url, description
        )
    )


@app.command("create-version")
def create_version_command(
    project_id: str,
    system_id: str,
    version_id: str,
    name: Annotated[str | None, typer.Option("--name")] = None,
    test_url: Annotated[str, typer.Option("--test-url")] = "",
    description: Annotated[str, typer.Option("--description")] = "",
) -> None:
    """Create a Version asset tree without overwriting existing data."""
    _run_create(
        lambda: create_version(
            _projects_root(), project_id, system_id, version_id, name, test_url, description
        )
    )


def _run_create(create: Callable[[], Path]) -> None:
    try:
        path = create()
    except ScaffoldError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1) from exc
    typer.echo(f"Created: {path}")
