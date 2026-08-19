"""单会话批量发现（W2-2）。

在一个持续会话内一次评估多个候选定位、内部自带重试，替代 dogfood 里
"生成脚本 → run → 没定准 → 再生成下一版"的逐次试错（约 30 个一次性脚本、
每 run 一次弹一次窗）。发现结果结合 W2-3 打分排序，把"选哪个定位"的判断
留给调用方，但给出机器可读依据。

page 只需实现 Playwright Page 的一小部分（get_by_test_id / get_by_role /
get_by_label / get_by_text / locator），因此可用 duck-typed 假对象单测，
无需真实浏览器。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentest.exploration.budget import ExplorationBudget
from agentest.exploration.scoring import score_locator


@dataclass(frozen=True)
class LocatorCandidate:
    """一个待验证的候选定位。

    type：testid/role/label/text/css/xpath。
    value：原样定位串（css/xpath 选择器、testid 值、可见文本、role 名等）。
    name：role 类型的可访问名（get_by_role(role, name=...)）。
    """

    id: str
    type: str
    value: str
    name: str | None = None


@dataclass(frozen=True)
class ResolveResult:
    """一次解析结果：命中数量与可能的错误。"""

    count: int
    error: str | None = None


@dataclass(frozen=True)
class Discovery:
    """单个候选的发现结论（命中情况 + 打分）。"""

    candidate: LocatorCandidate
    count: int
    found: bool
    unique: bool
    score: int
    tier: str
    data_derived: bool
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


def resolve_candidate(page: Any, candidate: LocatorCandidate) -> ResolveResult:
    """把一个候选定位解析到 page 上，返回命中数量。

    不抛异常：定位类型不支持、或 Playwright 调用报错都收敛为 error 字段。
    """

    loc_type = (candidate.type or "").strip().lower()
    value = candidate.value
    try:
        if loc_type == "testid":
            locator = page.get_by_test_id(value)
        elif loc_type == "role":
            if candidate.name is not None:
                locator = page.get_by_role(value, name=candidate.name)
            else:
                locator = page.get_by_role(value)
        elif loc_type == "label":
            locator = page.get_by_label(value)
        elif loc_type == "text":
            locator = page.get_by_text(value)
        elif loc_type == "css":
            locator = page.locator(value)
        elif loc_type == "xpath":
            selector = value if value.startswith("xpath=") else f"xpath={value}"
            locator = page.locator(selector)
        else:
            return ResolveResult(0, error=f"未知定位类型 {loc_type!r}")
        count = int(locator.count())
    except Exception as exc:  # noqa: BLE001 - 发现期把任何解析错误收敛为结构化结果
        return ResolveResult(0, error=f"{type(exc).__name__}: {exc}")
    return ResolveResult(max(0, count))


def _rank_key(discovery: Discovery) -> tuple[int, int, int, int]:
    # 排序优先级：命中且唯一 > 命中 > 分数高 > 命中数少（越接近唯一越好）。
    return (
        1 if discovery.found else 0,
        1 if discovery.unique else 0,
        discovery.score,
        -discovery.count,
    )


def discover(
    page: Any,
    candidates: list[LocatorCandidate],
    *,
    retries: int = 1,
    budget: ExplorationBudget | None = None,
) -> list[Discovery]:
    """在同一会话内逐个解析候选定位并按稳定性排序返回。

    - retries：单个候选解析失败（抛错）时的额外重试次数（默认 1）。
    - budget：可选探索预算；每次解析计一次 attempt，预算触发即停止后续候选，
      已解析的仍返回。命中记 progress，未命中/报错记失败尝试。
    """

    if retries < 0:
        raise ValueError("retries 不能为负")

    results: list[Discovery] = []
    for candidate in candidates:
        if budget is not None:
            decision = budget.should_stop()
            if decision.stop:
                break
            budget.start_entry(candidate.id)

        result = resolve_candidate(page, candidate)
        attempts_left = retries
        while result.error is not None and attempts_left > 0:
            attempts_left -= 1
            result = resolve_candidate(page, candidate)

        found = result.error is None and result.count > 0
        unique = result.error is None and result.count == 1
        rating = score_locator(candidate.type, candidate.value, name=candidate.name)

        results.append(
            Discovery(
                candidate=candidate,
                count=result.count,
                found=found,
                unique=unique,
                score=rating.score,
                tier=rating.tier,
                data_derived=rating.data_derived,
                warnings=list(rating.warnings),
                error=result.error,
            )
        )

        if budget is not None:
            budget.record_attempt(candidate.id, success=found)
            if found:
                budget.record_progress()

    results.sort(key=_rank_key, reverse=True)
    return results


__all__ = [
    "LocatorCandidate",
    "ResolveResult",
    "Discovery",
    "resolve_candidate",
    "discover",
]
