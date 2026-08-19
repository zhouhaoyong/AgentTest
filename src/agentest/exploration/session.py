"""Workflow-facing coordinator for one bounded exploration session."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentest.exploration.budget import ExplorationBudget, StopDecision
from agentest.exploration.discovery import Discovery, LocatorCandidate, discover


@dataclass
class ExplorationSession:
    """Apply one shared budget to navigation attempts and locator discovery."""

    page: Any
    budget: ExplorationBudget
    _active_entry: str = field(default="", init=False)
    _stop_decision: StopDecision = field(default_factory=lambda: StopDecision(False), init=False)

    @property
    def stop_decision(self) -> StopDecision:
        """Return the latest stop decision for business-facing progress reporting."""

        return self._stop_decision

    def begin_entry(self, entry_key: str) -> StopDecision:
        """Start a module entry only when the session has remaining budget."""

        self._refresh_stop_decision()
        if self._stop_decision.stop:
            return self._stop_decision
        self._active_entry = entry_key
        self.budget.start_entry(entry_key)
        self._refresh_stop_decision()
        return self._stop_decision

    def record_navigation(self, success: bool) -> StopDecision:
        """Record one observed navigation attempt and preserve the shared budget."""

        if not self._active_entry:
            raise ValueError("必须先调用 begin_entry 再记录导航结果")
        self._refresh_stop_decision()
        if self._stop_decision.stop:
            return self._stop_decision
        self.budget.record_attempt(self._active_entry, success=success)
        if success:
            self.budget.record_progress()
        self._refresh_stop_decision()
        return self._stop_decision

    def discover_candidates(self, candidates: list[LocatorCandidate]) -> list[Discovery]:
        """Batch-check candidates only while the same exploration session may continue."""

        self._refresh_stop_decision()
        if self._stop_decision.stop:
            return []
        discoveries = discover(self.page, candidates, budget=self.budget)
        self._refresh_stop_decision()
        return discoveries

    def _refresh_stop_decision(self) -> None:
        self._stop_decision = self.budget.should_stop()


__all__ = ["ExplorationSession"]
