from agentest.exploration import ExplorationBudget, ExplorationSession, LocatorCandidate
from agentest.exploration.budget import REASON_ENTRY_RETRY


class _Locator:
    def __init__(self, count: int) -> None:
        self._count = count

    def count(self) -> int:
        return self._count


class _Page:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def locator(self, value: str) -> _Locator:
        self.calls.append(value)
        return _Locator(1 if value == "[data-testid='orders']" else 0)

    def get_by_test_id(self, value: str) -> _Locator:
        return self.locator(f"[data-testid='{value}']")

    def get_by_role(self, value: str, name: str | None = None) -> _Locator:
        return self.locator(f"role:{value}:{name}")

    def get_by_label(self, value: str) -> _Locator:
        return self.locator(f"label:{value}")

    def get_by_text(self, value: str) -> _Locator:
        return self.locator(f"text:{value}")


def test_session_stops_candidate_discovery_after_entry_retry_budget_is_exhausted() -> None:
    page = _Page()
    session = ExplorationSession(
        page,
        ExplorationBudget(max_retries_per_entry=2, max_steps_without_progress=99),
    )

    session.begin_entry("nav:orders")
    session.record_navigation(False)
    decision = session.record_navigation(False)
    discoveries = session.discover_candidates(
        [LocatorCandidate("orders", "css", "[data-testid='orders']")]
    )

    assert decision.reason == REASON_ENTRY_RETRY
    assert discoveries == []
    assert page.calls == []


def test_session_uses_one_budget_for_navigation_and_batched_candidate_discovery() -> None:
    page = _Page()
    session = ExplorationSession(page, ExplorationBudget(max_steps_without_progress=99))

    session.begin_entry("nav:orders")
    assert session.record_navigation(True).stop is False
    discoveries = session.discover_candidates(
        [
            LocatorCandidate("miss", "css", "[data-testid='missing']"),
            LocatorCandidate("orders", "css", "[data-testid='orders']"),
        ]
    )

    assert [item.candidate.id for item in discoveries] == ["orders", "miss"]
    assert session.stop_decision.stop is False
    assert page.calls == ["[data-testid='missing']", "[data-testid='orders']"]
