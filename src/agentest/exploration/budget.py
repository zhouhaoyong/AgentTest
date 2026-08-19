"""探索预算硬熔断（W2-1）。

纯状态机，不依赖浏览器。把 dogfood 里"同一入口反复死磕、连续无新事实还在空耗"
的黑洞下沉为可被程序强制的止损：到点直接 stop，不靠 agent 自觉。

用法：
    budget = ExplorationBudget()
    budget.start_entry("nav:众包订单")
    budget.record_attempt("nav:众包订单", success=False)
    ...
    decision = budget.should_stop()
    if decision.stop:
        # 停手并产出结构化上报：decision.reason / decision.detail
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field

# 止损原因取值（供调用方分支与上报文案使用）。
REASON_ENTRY_RETRY = "entry_retry_exhausted"
REASON_NO_PROGRESS = "no_progress"
REASON_STEP_LIMIT = "step_limit"
REASON_TIME_LIMIT = "time_limit"


@dataclass(frozen=True)
class StopDecision:
    """一次止损判定。stop=False 时 reason/detail 为空。"""

    stop: bool
    reason: str = ""
    detail: str = ""


@dataclass
class ExplorationBudget:
    """探索预算计数器。

    - max_retries_per_entry：同一入口连续失败达到此数即判该入口熔断。
    - max_steps_without_progress：连续多少步没有"新事实"即整体止损。
    - max_total_steps：总步数兜底上限。
    - max_seconds：可选墙钟兜底（软约束；真正硬超时由调度层负责）。
    """

    max_retries_per_entry: int = 3
    max_steps_without_progress: int = 5
    max_total_steps: int = 40
    max_seconds: float | None = None
    _clock: Callable[[], float] = field(default=time.monotonic, repr=False)

    total_steps: int = field(default=0, init=False)
    steps_since_progress: int = field(default=0, init=False)
    _entry_failures: dict[str, int] = field(default_factory=dict, init=False)
    _exhausted_entry: str | None = field(default=None, init=False)
    _start_time: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        for name, value in (
            ("max_retries_per_entry", self.max_retries_per_entry),
            ("max_steps_without_progress", self.max_steps_without_progress),
            ("max_total_steps", self.max_total_steps),
        ):
            if value <= 0:
                raise ValueError(f"{name} 必须为正整数")
        if self.max_seconds is not None and self.max_seconds <= 0:
            raise ValueError("max_seconds 必须为正数或 None")

    def start_entry(self, key: str) -> None:
        """进入一个探索目标入口（用于按入口统计连续失败）。"""
        if self._start_time is None:
            self._start_time = self._clock()
        self._entry_failures.setdefault(key, 0)

    def record_attempt(self, key: str, *, success: bool) -> None:
        """登记一次针对某入口的尝试。success=True 会清零该入口失败计数。"""
        if self._start_time is None:
            self._start_time = self._clock()
        self.total_steps += 1
        self.steps_since_progress += 1
        if success:
            self._entry_failures[key] = 0
            return
        self._entry_failures[key] = self._entry_failures.get(key, 0) + 1
        if self._entry_failures[key] >= self.max_retries_per_entry:
            self._exhausted_entry = key

    def record_progress(self) -> None:
        """记录一条"新事实"（进了新页面 / 记到新元素），重置无进展计数。"""
        self.steps_since_progress = 0

    def should_stop(self) -> StopDecision:
        """按优先级返回止损判定：入口熔断 > 无进展 > 步数 > 时间。"""
        if self._exhausted_entry is not None:
            detail = (
                f"入口 {self._exhausted_entry!r} 连续失败达 "
                f"{self.max_retries_per_entry} 次，停止死磕。"
            )
            return StopDecision(True, REASON_ENTRY_RETRY, detail)
        if self.steps_since_progress >= self.max_steps_without_progress:
            return StopDecision(
                True,
                REASON_NO_PROGRESS,
                f"连续 {self.steps_since_progress} 步无新增已验证事实，停止空耗。",
            )
        if self.total_steps >= self.max_total_steps:
            return StopDecision(
                True,
                REASON_STEP_LIMIT,
                f"总步数达到上限 {self.max_total_steps}，触发兜底止损。",
            )
        if self.max_seconds is not None and self._start_time is not None:
            elapsed = self._clock() - self._start_time
            if elapsed >= self.max_seconds:
                return StopDecision(
                    True,
                    REASON_TIME_LIMIT,
                    f"探索耗时达到软上限 {self.max_seconds:.0f}s，触发兜底止损。",
                )
        return StopDecision(False)


__all__ = [
    "ExplorationBudget",
    "StopDecision",
    "REASON_ENTRY_RETRY",
    "REASON_NO_PROGRESS",
    "REASON_STEP_LIMIT",
    "REASON_TIME_LIMIT",
]
