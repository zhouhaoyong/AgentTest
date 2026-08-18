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


def test_system_config_applies_type_defaults() -> None:
    config = SystemConfig(id="contact-h5", name="通讯录 H5", type="h5", base_url="")

    assert config.type == "h5"
    assert config.base_url == ""
    assert config.test_environment.viewport.width == 393
    assert config.test_environment.is_mobile is True


@pytest.mark.parametrize("system_id", ["contact", "gumai-pc", "contact-web-h5"])
def test_system_config_does_not_require_type_suffix(system_id: str) -> None:
    # 系统类型由 type 字段承载，System ID 只需目录安全，不再强制以类型结尾。
    config = SystemConfig(id=system_id, name="通讯录 Web", type="web")

    assert config.id == system_id
    assert config.type == "web"


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

    assert config.test_environment.viewport.width == 393
    assert config.test_environment.viewport.height == 852
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
    [({"width": 430}, 430, 852), ({"height": 932}, 393, 932)],
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
    assert environment.viewport.height == 852
    assert environment.is_mobile is True
    assert environment.locale == "en-US"


def test_workspace_state_does_not_persist_test_case_approval() -> None:
    state = WorkspaceState()

    assert "test_cases_approved" not in state.model_dump()


@pytest.mark.parametrize(
    "phase",
    [
        "intake",
        "context",
        "requirements",
        "exploration",
        "test-cases",
        "testing",
        "reporting",
        "regression",
    ],
)
def test_workspace_state_accepts_only_workflow_phases(phase: str) -> None:
    assert WorkspaceState(phase=phase).phase == phase


def test_workspace_state_rejects_unknown_phase() -> None:
    with pytest.raises(ValidationError):
        WorkspaceState(phase="requirement")


def test_workspace_state_rejects_unknown_field() -> None:
    # 统一后端后不再有浏览器选择配置；多余字段应被 extra="forbid" 拒绝。
    with pytest.raises(ValidationError):
        WorkspaceState(browser={"selected": "auto"})


def test_workspace_context_tracks_only_confirmed_scope() -> None:
    context = WorkspaceContext(
        project_id="store",
        system_id="shop-web",
        version_id="v0.0.1",
    )

    assert context.project_id == "store"
    assert context.system_id == "shop-web"
    assert context.version_id == "v0.0.1"


def test_workspace_context_rejects_removed_integration_scope_field() -> None:
    # 联动已改为版本内的轻量标记；上下文不再持有 integration_scope_id / test_url。
    with pytest.raises(ValidationError):
        WorkspaceContext(project_id="store", system_id="shop-web", integration_scope_id="x")
    with pytest.raises(ValidationError):
        WorkspaceContext(project_id="store", system_id="shop-web", test_url="https://x.test")


def test_version_declares_lightweight_linked_ends() -> None:
    version = VersionConfig(
        id="v0.0.1",
        name="v0.0.1",
        linked=True,
        linked_ends=[
            {"system_id": "shop-web", "version_id": "v0.0.1", "note": "下单入口"},
            {"system_id": "warehouse-web"},
        ],
    )

    assert version.linked is True
    assert [end.system_id for end in version.linked_ends] == ["shop-web", "warehouse-web"]
    # 省略 version_id 表示引用该系统当前范围内的版本。
    assert version.linked_ends[1].version_id == ""


def test_version_defaults_to_no_linkage() -> None:
    version = VersionConfig(id="v0.0.1", name="v0.0.1")

    assert version.linked is False
    assert version.linked_ends == []


@pytest.mark.parametrize(
    "version_data",
    [
        # linked=True 却没有声明任何联动端。
        {"id": "v0.0.1", "name": "v0.0.1", "linked": True},
        # linked=False 却声明了联动端。
        {
            "id": "v0.0.1",
            "name": "v0.0.1",
            "linked": False,
            "linked_ends": [{"system_id": "shop-web"}],
        },
        # 重复引用同一端。
        {
            "id": "v0.0.1",
            "name": "v0.0.1",
            "linked": True,
            "linked_ends": [
                {"system_id": "shop-web", "version_id": "v1"},
                {"system_id": "shop-web", "version_id": "v1"},
            ],
        },
        # 联动端引用了非法 ID。
        {
            "id": "v0.0.1",
            "name": "v0.0.1",
            "linked": True,
            "linked_ends": [{"system_id": "shop/web"}],
        },
    ],
)
def test_version_rejects_invalid_linkage(version_data: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        VersionConfig(**version_data)


def test_version_linkage_yaml_loads_with_shared_model_loader(tmp_path: Path) -> None:
    path = tmp_path / "version.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "id": "v0.0.1",
                "name": "v0.0.1",
                "test_url": "https://shop.test",
                "linked": True,
                "linked_ends": [
                    {"system_id": "shop-web", "version_id": "v0.0.1"},
                    {"system_id": "warehouse-web", "version_id": "v0.0.1"},
                ],
            }
        ),
        encoding="utf-8",
    )

    version = load_yaml_model(path, VersionConfig)

    assert version.id == "v0.0.1"
    assert len(version.linked_ends) == 2
