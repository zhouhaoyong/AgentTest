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
from agentest.schemas.system import SystemConfig


def create_system(
    projects_root: Path,
    project_id: str,
    system_id: str,
    name: str,
    system_type: str = "web",
    base_url: str = "",
    description: str = "",
) -> Path:
    validate_id(project_id, "Project")
    validate_id(system_id, "System")
    project_dir = projects_root / project_id
    require_directory(project_dir, "Project")
    systems_dir = project_dir / "systems"
    require_directory(systems_dir, "Project systems directory")
    system_dir = systems_dir / system_id
    if system_dir.exists():
        raise ScaffoldError(f"System already exists: {system_dir}")

    config = SystemConfig(
        id=system_id,
        name=name,
        type=system_type,
        base_url=base_url,
        description=description,
    )
    system_dir.mkdir()
    try:
        write_new_file(
            system_dir / "system.yaml",
            yaml.safe_dump(config.model_dump(), allow_unicode=True, sort_keys=False),
        )
        write_new_file(system_dir / "requirement.md", read_template("system-requirement.md"))
        _create_contract_directory(
            system_dir / "element-map", "element-map-requirement.md", "element-map-index.md"
        )
        _create_contract_directory(
            system_dir / "memory", "memory-requirement.md", "memory-index.md"
        )
        versions_dir = system_dir / "versions"
        versions_dir.mkdir()
        write_new_file(
            versions_dir / "requirement.md", read_template("versions-requirement.md")
        )
    except Exception:
        remove_created_tree(system_dir)
        raise
    return system_dir


def _create_contract_directory(
    directory: Path, contract_template: str, index_template: str
) -> None:
    directory.mkdir()
    write_new_file(directory / "requirement.md", read_template(contract_template))
    write_new_file(directory / "index.md", read_template(index_template))
    (directory / "modules").mkdir()
    write_new_file(
        directory / "modules" / "requirement.md", read_template("modules-requirement.md")
    )
