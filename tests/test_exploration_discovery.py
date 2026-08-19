import pytest

from agentest.exploration.budget import ExplorationBudget
from agentest.exploration.discovery import (
    LocatorCandidate,
    discover,
    resolve_candidate,
)


class FakeLocator:
    def __init__(self, count: int) -> None:
        self._count = count

    def count(self) -> int:
        return self._count


class FakePage:
    """Duck-typed Playwright Page：按定位串返回预置命中数。

    counts 的 key 用 '<method>:<value>' 或 'role:<value>:<name>'。
    raises：命中即抛错（模拟解析失败），值为抛出次数（用于测试重试）。
    """

    def __init__(self, counts: dict[str, int], raises: dict[str, int] | None = None) -> None:
        self.counts = counts
        self.raises = raises or {}
        self.calls: list[str] = []

    def _maybe_raise(self, key: str) -> None:
        if self.raises.get(key, 0) > 0:
            self.raises[key] -= 1
            raise RuntimeError("boom")

    def get_by_test_id(self, value: str) -> FakeLocator:
        key = f"testid:{value}"
        self.calls.append(key)
        self._maybe_raise(key)
        return FakeLocator(self.counts.get(key, 0))

    def get_by_role(self, value: str, name: str | None = None) -> FakeLocator:
        key = f"role:{value}:{name}"
        self.calls.append(key)
        self._maybe_raise(key)
        return FakeLocator(self.counts.get(key, 0))

    def get_by_label(self, value: str) -> FakeLocator:
        key = f"label:{value}"
        self.calls.append(key)
        return FakeLocator(self.counts.get(key, 0))

    def get_by_text(self, value: str) -> FakeLocator:
        key = f"text:{value}"
        self.calls.append(key)
        return FakeLocator(self.counts.get(key, 0))

    def locator(self, selector: str) -> FakeLocator:
        key = f"locator:{selector}"
        self.calls.append(key)
        return FakeLocator(self.counts.get(key, 0))


def test_resolve_testid_found_unique() -> None:
    page = FakePage({"testid:add": 1})
    result = resolve_candidate(page, LocatorCandidate("a", "testid", "add"))
    assert result.count == 1
    assert result.error is None


def test_resolve_role_with_name() -> None:
    page = FakePage({"role:button:登录": 1})
    result = resolve_candidate(page, LocatorCandidate("a", "role", "button", name="登录"))
    assert result.count == 1


def test_resolve_xpath_prefix_added() -> None:
    page = FakePage({"locator:xpath=//button": 2})
    result = resolve_candidate(page, LocatorCandidate("a", "xpath", "//button"))
    assert result.count == 2


def test_resolve_unknown_type_returns_error() -> None:
    page = FakePage({})
    result = resolve_candidate(page, LocatorCandidate("a", "magic", "x"))
    assert result.count == 0
    assert result.error is not None


def test_resolve_error_is_captured() -> None:
    page = FakePage({"testid:x": 1}, raises={"testid:x": 1})
    result = resolve_candidate(page, LocatorCandidate("a", "testid", "x"))
    assert result.error is not None


def test_discover_ranks_found_unique_first() -> None:
    page = FakePage(
        {
            "testid:add": 1,  # found + unique + high score
            "locator:div.card": 0,  # not found
            "text:保存": 3,  # found but not unique, lower score
        }
    )
    candidates = [
        LocatorCandidate("miss", "css", "div.card"),
        LocatorCandidate("text", "text", "保存"),
        LocatorCandidate("id", "testid", "add"),
    ]
    ranked = discover(page, candidates)
    assert ranked[0].candidate.id == "id"
    assert ranked[0].found and ranked[0].unique
    assert ranked[-1].candidate.id == "miss"
    assert ranked[-1].found is False


def test_discover_retries_transient_error() -> None:
    # 首次抛错、重试成功。
    page = FakePage({"testid:x": 1}, raises={"testid:x": 1})
    ranked = discover(page, [LocatorCandidate("x", "testid", "x")], retries=1)
    assert ranked[0].error is None
    assert ranked[0].found is True


def test_discover_stops_when_budget_exhausted() -> None:
    page = FakePage({"locator:a": 0, "locator:b": 0, "locator:c": 0})
    budget = ExplorationBudget(max_retries_per_entry=99, max_steps_without_progress=2)
    candidates = [
        LocatorCandidate("a", "css", "a"),
        LocatorCandidate("b", "css", "b"),
        LocatorCandidate("c", "css", "c"),
        LocatorCandidate("d", "css", "d"),
    ]
    ranked = discover(page, candidates, budget=budget)
    # 前两个都未命中 → 无进展达 2 步 → 第三个开始前触发止损。
    assert len(ranked) == 2


def test_discover_negative_retries_rejected() -> None:
    page = FakePage({})
    with pytest.raises(ValueError):
        discover(page, [LocatorCandidate("a", "css", "a")], retries=-1)


def test_discover_marks_data_derived_warning() -> None:
    page = FakePage({"locator:[class*='setting']": 1})
    ranked = discover(page, [LocatorCandidate("g", "css", "[class*='setting']")])
    assert ranked[0].data_derived is True
    assert ranked[0].warnings
