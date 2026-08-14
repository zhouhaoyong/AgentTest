from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from agentest.schemas.project import ProjectConfig, load_yaml_model
from agentest.schemas.system import SystemConfig
from agentest.schemas.version import VersionConfig
from agentest.schemas.workspace import WorkspaceContext, WorkspaceState


def test_project_config_accepts_minimal_valid_data() -> None:
    config = ProjectConfig(id="contact-platform", name="通讯录平台")

    assert config.id == "contact-platform"
    assert config.description == ""


@pytest.mark.parametrize(
    "invalid_id", ["", ".", "..", "../escape", "contact/platform", "contact platform"]
)
def test_project_config_rejects_unsafe_ids(invalid_id: str) -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(id=invalid_id, name="通讯录平台")


@pytest.mark.parametrize("invalid_id", [".", ".."])
def test_all_asset_id_consumers_reject_path_segments(invalid_id: str) -> None:
    with pytest.raises(ValidationError):
        SystemConfig(id=invalid_id, name="通讯录 Web")
    with pytest.raises(ValidationError):
        VersionConfig(id=invalid_id, name="v1")
    with pytest.raises(ValidationError):
        WorkspaceContext(project_id=invalid_id, system_id="contact-web")


def test_system_config_requires_supported_type_and_type_suffix() -> None:
    config = SystemConfig(id="contact-h5", name="通讯录 H5", type="h5", base_url="")

    assert config.type == "h5"
    assert config.base_url == ""
    assert config.test_environment.viewport.width == 390
    assert config.test_environment.is_mobile is True


@pytest.mark.parametrize("system_id", ["contact", "contact-web-h5"])
def test_system_config_rejects_id_without_matching_type_suffix(system_id: str) -> None:
    with pytest.raises(ValidationError):
        SystemConfig(id=system_id, name="通讯录 Web", type="web")


def test_system_config_accepts_explicit_playwright_environment() -> None:
    config = SystemConfig(
        id="contact-web",
        name="通讯录 Web",
        type="web",
        test_environment={
            "viewport": {"width": 1280, "height": 720},
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False,
            "locale": "en-US",
            "timezone_id": "UTC",
            "action_timeout_ms": 8000,
            "navigation_timeout_ms": 45000,
            "login": "manual",
        },
    )

    assert config.test_environment.viewport.width == 1280
    assert config.test_environment.locale == "en-US"
    assert config.test_environment.login == "manual"


def test_mobile_system_partial_environment_preserves_mobile_defaults() -> None:
    config = SystemConfig(
        id="contact-h5",
        name="通讯录 H5",
        type="h5",
        test_environment={"locale": "en-US"},
    )

    assert config.test_environment.viewport.width == 390
    assert config.test_environment.viewport.height == 844
    assert config.test_environment.device_scale_factor == 3
    assert config.test_environment.is_mobile is True
    assert config.test_environment.has_touch is True
    assert config.test_environment.locale == "en-US"


def test_version_config_allows_empty_test_url() -> None:
    config = VersionConfig(id="v0.0.1", name="v0.0.1", test_url="")

    assert config.test_url == ""


def test_version_config_can_override_test_environment() -> None:
    config = VersionConfig(
        id="v0.0.1",
        name="v0.0.1",
        test_environment={"viewport": {"width": 430, "height": 932}},
    )

    assert config.test_environment.viewport.width == 430
    assert config.test_environment.viewport.height == 932


@pytest.mark.parametrize(
    ("viewport", "expected_width", "expected_height"),
    [({"width": 430}, 430, 844), ({"height": 932}, 390, 932)],
)
def test_version_config_allows_partial_viewport_override(
    viewport: dict[str, int], expected_width: int, expected_height: int
) -> None:
    system = SystemConfig(id="contact-h5", name="通讯录 H5", type="h5")
    version = VersionConfig(id="v0.0.1", name="v0.0.1", test_environment={"viewport": viewport})

    environment = system.test_environment.merged_with(version.test_environment)

    assert environment.viewport.width == expected_width
    assert environment.viewport.height == expected_height
    assert environment.is_mobile is True


def test_version_environment_override_preserves_system_defaults() -> None:
    system = SystemConfig(id="contact-h5", name="通讯录 H5", type="h5")
    version = VersionConfig(
        id="v0.0.1",
        name="v0.0.1",
        test_environment={"viewport": {"width": 430, "height": 932}},
    )

    environment = system.test_environment.merged_with(version.test_environment)

    assert environment.viewport.width == 430
    assert environment.viewport.height == 932
    assert environment.is_mobile is True
    assert environment.has_touch is True
    assert environment.device_scale_factor == 3


def test_load_yaml_model_validates_file(tmp_path: Path) -> None:
    path = tmp_path / "project.yaml"
    path.write_text(yaml.safe_dump({"id": "demo", "name": "Demo"}), encoding="utf-8")

    config = load_yaml_model(path, ProjectConfig)

    assert config == ProjectConfig(id="demo", name="Demo")


def test_version_environment_yaml_round_trip_preserves_only_declared_overrides(
    tmp_path: Path,
) -> None:
    system = SystemConfig(id="contact-h5", name="通讯录 H5", type="h5")
    version = VersionConfig(
        id="v0.0.1",
        name="v0.0.1",
        test_environment={"locale": "en-US", "viewport": {"width": 430}},
    )
    path = tmp_path / "version.yaml"
    path.write_text(yaml.safe_dump(version.model_dump()), encoding="utf-8")

    restored = load_yaml_model(path, VersionConfig)
    environment = system.test_environment.merged_with(restored.test_environment)

    assert yaml.safe_load(path.read_text(encoding="utf-8"))["test_environment"] == {
        "locale": "en-US",
        "viewport": {"width": 430},
    }
    assert environment.viewport.width == 430
    assert environment.viewport.height == 844
    assert environment.is_mobile is True
    assert environment.locale == "en-US"


def test_workspace_state_does_not_persist_test_point_approval() -> None:
    state = WorkspaceState()

    assert "test_points_approved" not in state.model_dump()


def test_workspace_context_accepts_optional_integration_scope() -> None:
    context = WorkspaceContext(
        project_id="store",
        system_id="shop-web",
        integration_scope_id="order-sync",
    )

    assert context.integration_scope_id == "order-sync"
