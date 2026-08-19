from pathlib import Path

from agentest.test_cases import parse_key_coverage_constraints

_ROOT = Path(__file__).resolve().parents[1]


def test_test_case_template_has_parseable_key_coverage_contract() -> None:
    content = (_ROOT / "workflow" / "test-cases" / "template-test-cases.md").read_text(
        encoding="utf-8"
    )

    constraints, issues = parse_key_coverage_constraints(content)

    assert issues == []
    assert constraints[0].id == "KC-001"
    assert constraints[0].test_case_ids == ("TC-001", "TC-002")


def test_report_template_summary_points_to_its_actual_numeric_summary_section() -> None:
    for relative_path in (
        "workflow/reporting/template-report.md",
        "docs/examples/report.md",
    ):
        content = (_ROOT / relative_path).read_text(encoding="utf-8")

        assert "详见「6. 本次结果汇总」" in content


def test_script_templates_use_the_auditable_covered_test_case_field() -> None:
    for relative_path in (
        "workflow/testing/template-test-script.py",
        "docs/examples/test-script.py",
    ):
        content = (_ROOT / relative_path).read_text(encoding="utf-8")

        assert "覆盖用例：TC-001、TC-002" in content


def test_demo_includes_the_version_evidence_contract() -> None:
    content = (_ROOT / "docs" / "demo.md").read_text(encoding="utf-8")

    assert "Evidence" in content
    assert "evidence-requirement.md" in content
    assert (_ROOT / "docs" / "examples" / "evidence-requirement.md").is_file()


def test_fingerprint_guidance_mentions_key_coverage_constraints() -> None:
    for relative_path in (
        "workflow/testing/prompt.md",
        "prd.md",
        "src/agentest/test_cases.py",
    ):
        content = (_ROOT / relative_path).read_text(encoding="utf-8")

        assert "关键覆盖约束" in content
        assert "承接用例" in content
        assert "完成标准" in content


def test_formal_test_guidance_requires_a_script_for_each_test_case() -> None:
    expected = "每个测试用例都必须在报告中关联一个可复跑脚本"
    for relative_path in (
        "AGENTS.md",
        "README.md",
        "prd.md",
        "workflow/testing/prompt.md",
        "workflow/testing/rules.md",
        "workflow/reporting/prompt.md",
    ):
        content = (_ROOT / relative_path).read_text(encoding="utf-8")

        assert expected in content


def test_test_case_guidance_documents_consistent_execution_combinations() -> None:
    for relative_path in (
        "AGENTS.md",
        "prd.md",
        "workflow/test-cases/prompt.md",
        "workflow/test-cases/template-test-cases.md",
        "workflow/testing/rules.md",
    ):
        content = (_ROOT / relative_path).read_text(encoding="utf-8")

        assert "未测试 + 未执行" in content
        assert "完整 + PASS/FAIL" in content
        assert "部分 + BLOCKED" in content
