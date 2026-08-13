from pathlib import Path

import yaml

from agentest.scaffold.common import (
    ScaffoldError,
    remove_created_tree,
    validate_id,
    write_new_file,
)
from agentest.scaffold.templates import read_template
from agentest.schemas.project import ProjectConfig


def create_project(projects_root: Path, project_id: str, name: str, description: str = "") -> Path:
    validate_id(project_id, "Project")
    config = ProjectConfig(id=project_id, name=name, description=description)
    project_dir = projects_root / project_id
    if project_dir.exists():
        raise ScaffoldError(f"Project already exists: {project_dir}")

    project_dir.mkdir(parents=True)
    try:
        write_new_file(
            project_dir / "project.yaml",
            yaml.safe_dump(config.model_dump(), allow_unicode=True, sort_keys=False),
        )
        write_new_file(project_dir / "requirement.md", read_template("project-requirement.md"))
        systems_dir = project_dir / "systems"
        systems_dir.mkdir()
        write_new_file(systems_dir / "requirement.md", read_template("systems-requirement.md"))
    except Exception:
        remove_created_tree(project_dir)
        raise
    return project_dir
