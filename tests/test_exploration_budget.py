import pytest

from agentest.exploration.budget import (
    REASON_ENTRY_RETRY,
    REASON_NO_PROGRESS,
    REASON_STEP_LIMIT,
    REASON_TIME_LIMIT,
    ExplorationBudget,
)


def test_no_stop_when_within_budget() -> None:
    budget = ExplorationBudget()
    budget.start_entry("nav:orders")
    budget.record_attempt("nav:orders", success=True)
    budget.record_progress()
    assert budget.should_stop().stop is False


def test_entry_retry_exhausted() -> None:
    budget = ExplorationBudget(max_retries_per_entry=3)
    budget.start_entry("nav:众包订单")
    for _ in range(3):
        budget.record_attempt("nav:众包订单", success=False)
    decision = budget.should_stop()
    assert decision.stop is True
    assert decision.reason == REASON_ENTRY_RETRY
    assert "众包订单" in decision.detail


def test_success_resets_entry_failures() -> None:
    budget = ExplorationBudget(max_retries_per_entry=3)
    budget.start_entry("e")
    budget.record_attempt("e", success=False)
    budget.record_attempt("e", success=False)
    budget.record_attempt("e", success=True)  # 清零
    budget.record_attempt("e", success=False)
    assert budget.should_stop().stop is False


def test_no_progress_stop() -> None:
    budget = ExplorationBudget(max_steps_without_progress=5, max_retries_per_entry=99)
    for _ in range(5):
        budget.record_attempt("e", success=True)  # 成功但没有 record_progress
    decision = budget.should_stop()
    assert decision.stop is True
    assert decision.reason == REASON_NO_PROGRESS


def test_progress_resets_no_progress_counter() -> None:
    budget = ExplorationBudget(max_steps_without_progress=3, max_retries_per_entry=99)
    budget.record_attempt("e", success=True)
    budget.record_attempt("e", success=True)
    budget.record_progress()
    budget.record_attempt("e", success=True)
    assert budget.should_stop().stop is False


def test_step_limit_stop() -> None:
    budget = ExplorationBudget(
        max_total_steps=4, max_steps_without_progress=99, max_retries_per_entry=99
    )
    for _ in range(4):
        budget.record_attempt("e", success=True)
        budget.record_progress()
    decision = budget.should_stop()
    assert decision.stop is True
    assert decision.reason == REASON_STEP_LIMIT


def test_time_limit_stop_with_fake_clock() -> None:
    ticks = iter([0.0, 100.0])  # start_entry sets start=0.0; should_stop reads 100.0
    budget = ExplorationBudget(
        max_seconds=10.0,
        max_total_steps=99,
        max_steps_without_progress=99,
        max_retries_per_entry=99,
        _clock=lambda: next(ticks),
    )
    budget.start_entry("e")
    budget.record_attempt("e", success=True)
    budget.record_progress()
    decision = budget.should_stop()
    assert decision.stop is True
    assert decision.reason == REASON_TIME_LIMIT


def test_entry_retry_has_priority_over_no_progress() -> None:
    budget = ExplorationBudget(max_retries_per_entry=2, max_steps_without_progress=2)
    budget.record_attempt("e", success=False)
    budget.record_attempt("e", success=False)
    decision = budget.should_stop()
    assert decision.reason == REASON_ENTRY_RETRY


def test_invalid_config_rejected() -> None:
    with pytest.raises(ValueError):
        ExplorationBudget(max_retries_per_entry=0)
    with pytest.raises(ValueError):
        ExplorationBudget(max_seconds=0)
