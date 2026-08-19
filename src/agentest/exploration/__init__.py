"""探索期工具：预算硬熔断、定位打分、单会话批量发现。

这些能力把"靠 agent 自觉压不住"的探索约束（预算收敛、结构 vs 数据判别、
批量发现替代逐次试错）下沉为可被程序强制、可单测的逻辑。
"""

from agentest.exploration.budget import ExplorationBudget, StopDecision
from agentest.exploration.discovery import (
    Discovery,
    LocatorCandidate,
    ResolveResult,
    discover,
    resolve_candidate,
)
from agentest.exploration.scoring import LocatorScore, score_locator
from agentest.exploration.session import ExplorationSession

__all__ = [
    "ExplorationBudget",
    "StopDecision",
    "LocatorScore",
    "score_locator",
    "LocatorCandidate",
    "ResolveResult",
    "Discovery",
    "discover",
    "resolve_candidate",
    "ExplorationSession",
]
