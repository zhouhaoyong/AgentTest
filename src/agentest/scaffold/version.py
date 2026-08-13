from pathlib import Path

import yaml

from agentest.scaffold.common import (
    ScaffoldError,
    remove_created_tree,
    require_directory,
    validate_id,
    write_new_file,
)
from agentest.scaffold.templates import read_template
from agentest.schemas.version import VersionConfig


def create_version(
    projects_root: Path,
    project_id: str,
    system_id: str,
    version_id: str,
    name: str | None = None,
    test_url: str = "",
    description: str = "",
) -> Path:
    validate_id(project_id, "Project")
    validate_id(system_id, "System")
    validate_id(version_id, "Version")
    system_dir = projects_root / project_id / "systems" / system_id
    require_directory(system_dir, "System")
    versions_dir = system_dir / "versions"
    require_directory(versions_dir, "System versions directory")
    version_dir = versions_dir / version_id
    if version_dir.exists():
        raise ScaffoldError(f"Version already exists: {version_dir}")

    config = VersionConfig(
        id=version_id,
        name=name or version_id,
        test_url=test_url,
        description=description,
    )
    version_dir.mkdir()
    try:
        write_new_file(
            version_dir / "version.yaml",
            yaml.safe_dump(config.model_dump(), allow_unicode=True, sort_keys=False),
        )
        write_new_file(version_dir / "requirement.md", read_template("version-requirement.md"))
        (version_dir / "requirements" / "attachments").mkdir(parents=True)
        write_new_file(
            version_dir / "requirements" / "attachments" / "requirement.md",
            read_template("attachments-requirement.md"),
        )
        write_new_file(
            version_dir / "requirements" / "requirement.md",
            read_template("requirements-requirement.md")
            + "\n\n---\n\n"
            + read_template("requirement.md"),
        )
        write_new_file(version_dir / "requirements" / "source.md", read_template("source.md"))
        _create_version_directory(version_dir / "analysis", "analysis-requirement.md")
        write_new_file(version_dir / "analysis" / "analysis.md", read_template("analysis.md"))
        _create_version_directory(version_dir / "test-points", "test-points-requirement.md")
        write_new_file(
            version_dir / "test-points" / "test-points.md",
            read_template("test-points.md"),
        )
        _create_version_directory(version_dir / "run", "run-requirement.md")
        write_new_file(version_dir / "run" / "result.md", read_template("result.md"))
        _create_version_directory(version_dir / "bugs", "bugs-requirement.md")
        write_new_file(version_dir / "bugs" / "bugs.md", read_template("bugs.md"))
        _create_version_directory(version_dir / "report", "report-requirement.md")
        write_new_file(version_dir / "report" / "report.md", read_template("report.md"))
    except Exception:
        remove_created_tree(version_dir)
        raise
    return version_dir


def _create_version_directory(directory: Path, contract_template: str) -> None:
    directory.mkdir()
    write_new_file(directory / "requirement.md", read_template(contract_template))
