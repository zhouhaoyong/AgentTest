from pathlib import Path

import yaml

from agentest.asset_audit import audit_version_assets
from agentest.test_points import fingerprint_test_point_scope


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_contract(path: Path, name: str) -> None:
    write_text(path, f"# {name} 目录契约\n\n## 目录职责\n\n保存资产。\n")


def test_audit_reports_missing_execution_assets_and_fields(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(
        version / "test-points" / "test-points.md",
        """# 测试点

### TP-001 查看列表

#### 测试步骤

1. 打开列表。

#### 预期结果

- 列表展示。
""",
    )

    issues = audit_version_assets(version, require_execution_assets=True)
    codes = {issue.code for issue in issues}

    assert "missing_test_points_contract" in codes
    assert "missing_test_scripts" in codes
    assert "missing_report" in codes
    assert "missing_execution_field" in codes


def test_audit_accepts_consistent_executed_version(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    test_points = """# 测试点

### TP-001 查看列表

- 测试状态：已测试
- 测试结果：PASS
- 实际说明：列表展示。
- 执行时间：2026-08-17 10:00
- 证据：无

#### 测试步骤

1. 打开列表。

#### 预期结果

- 列表展示。
"""
    write_text(version / "test-points" / "test-points.md", test_points)
    write_contract(version / "test-points" / "requirement.md", "test-points")
    write_contract(version / "test-scripts" / "requirement.md", "test-scripts")
    write_text(version / "test-scripts" / "lists.py", "# TP-001\n")
    write_contract(version / "report" / "requirement.md", "report")
    write_text(
        version / "report" / "report.md",
        """# 测试报告

## 测试点结果

| 测试点 | 关联需求 | 使用脚本 | 本次结果 | 说明 |
|---|---|---|---|---|
| TP-001 | 列表 | lists.py | PASS | 列表展示。 |

## 本次结果汇总

- 本次测试点总数：1
- PASS：1
- FAIL：0
- BLOCKED：0
- NOT RUN：0
""",
    )
    state_path = tmp_path / ".agentest" / "state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        yaml.safe_dump(
            {
                "completed_test_point_ids": ["TP-001"],
                "test_points_fingerprint": fingerprint_test_point_scope(test_points),
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    assert audit_version_assets(version, state_path=state_path, require_execution_assets=True) == []


def test_audit_reports_scope_count_and_evidence_problems(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    test_points = """# 测试点

### TP-001 查看列表

- 测试状态：已测试
- 测试结果：FAIL
- 实际说明：失败。
- 执行时间：2026-08-17 10:00
- 证据：evidence/bug.png
"""
    write_text(version / "test-points" / "test-points.md", test_points)
    write_contract(version / "test-points" / "requirement.md", "test-points")
    write_contract(version / "report" / "requirement.md", "report")
    write_text(
        version / "report" / "report.md",
        """# 测试报告

| 测试点 | 关联需求 | 使用脚本 | 本次结果 | 说明 |
|---|---|---|---|---|
| TP-002 | 列表 | lists.py | PASS | 错误。 |

## 本次结果汇总

- 本次测试点总数：2
- PASS：2
- FAIL：0
- BLOCKED：0
- NOT RUN：0
""",
    )

    codes = {issue.code for issue in audit_version_assets(version, require_execution_assets=True)}

    assert "report_test_point_mismatch" in codes
    assert "report_summary_mismatch" in codes
    assert "missing_evidence" in codes
    assert "missing_referenced_asset" in codes


def test_audit_reports_fingerprint_drift(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(
        version / "test-points" / "test-points.md",
        """# 测试点

### TP-001 查看列表

- 测试状态：未测试
- 测试结果：NOT RUN
- 实际说明：未执行
- 执行时间：未执行
- 证据：无
""",
    )
    write_contract(version / "test-points" / "requirement.md", "test-points")
    state_path = tmp_path / ".agentest" / "state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("test_points_fingerprint: drifted\n", encoding="utf-8")

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "fingerprint_mismatch" in codes


def test_audit_reports_missing_fingerprint(tmp_path: Path) -> None:
    version = tmp_path / "versions" / "v1"
    write_text(version / "version.yaml", "id: v1\nname: v1\n")
    write_contract(version / "requirement.md", "version")
    write_contract(version / "requirements" / "requirement.md", "requirements")
    write_text(version / "requirements" / "source.md", "# 需求来源\n")
    write_text(version / "requirements" / "20260817_Vv1_demo.md", "# 结构化需求\n")
    write_text(
        version / "test-points" / "test-points.md",
        """# 测试点

### TP-001 查看列表

- 测试状态：未测试
- 测试结果：NOT RUN
- 实际说明：未执行
- 执行时间：未执行
- 证据：无
""",
    )
    write_contract(version / "test-points" / "requirement.md", "test-points")
    state_path = tmp_path / ".agentest" / "state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("completed_test_point_ids: []\n", encoding="utf-8")

    codes = {issue.code for issue in audit_version_assets(version, state_path=state_path)}

    assert "missing_fingerprint" in codes
