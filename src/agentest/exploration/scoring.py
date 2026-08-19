"""定位候选自动打分（W2-3）。

纯逻辑。与 asset_audit 的静态弱定位校验（W1-3）共用启发式，但用途不同：
W1-3 在入库期拦截/告警；打分在发现期给候选排序、把数据派生的降权标红，
让"结构 vs 数据"判别从模型自觉搬进工具。

判据核心：一条定位越接近"标记契约（testid/role/label/稳定属性）"越稳；
越接近"回显业务数据（中文自然语言、动态值、模糊 class、操作性文本）"越不稳。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# 与 asset_audit._CJK_PATTERN / _FUZZY_ATTR_PATTERN / _TEXT_INSTRUCTION_PATTERN 对齐。
_CJK_PATTERN = re.compile(r"[一-鿿]")
_FUZZY_ATTR_PATTERN = re.compile(r"\[[a-zA-Z_:-]+[*^$~]=")
_TEXT_INSTRUCTION_PATTERN = re.compile(
    r"[（(][^）)]*(?:点击|选择|取|进入|见图|如下|或)[^）)]*[）)]"
)
# 疑似动态值：长数字串（订单号/UID）、长十六进制串（生成态 class/hash）。
_PURE_DIGITS_PATTERN = re.compile(r"\d{6,}")
_LONG_HEX_PATTERN = re.compile(r"\b[0-9a-fA-F]{8,}\b")
_SELECTOR_TYPES = {"css", "xpath", "testid"}

# 各定位类型的基础分（定位优先级：测试属性 > 语义 > 稳定属性 CSS > 稳定文本 > XPath）。
_BASE_SCORE = {
    "testid": 100,
    "role": 90,
    "label": 80,
    "css": 70,
    "text": 50,
    "xpath": 30,
}


@dataclass(frozen=True)
class LocatorScore:
    """一条候选定位的稳定性评分。

    - score：0-100，越高越稳。
    - tier：strong(>=80) / ok(>=50) / weak(<50)。
    - data_derived：是否疑似把数据当结构（应降权、复用前复核）。
    - warnings：具体扣分原因，便于 agent 与人排查。
    """

    score: int
    tier: str
    data_derived: bool = False
    warnings: list[str] = field(default_factory=list)


def _tier_for(score: int) -> str:
    if score >= 80:
        return "strong"
    if score >= 50:
        return "ok"
    return "weak"


def score_locator(loc_type: str, value: str, *, name: str | None = None) -> LocatorScore:
    """给单条候选定位打分。

    loc_type：testid/role/label/css/text/xpath（大小写不敏感）。
    value：原样定位串；role 类型可另传 name（可访问名）参与判据。
    """

    loc_type = (loc_type or "").strip().lower()
    text = value if isinstance(value, str) else ""
    base = _BASE_SCORE.get(loc_type)
    warnings: list[str] = []
    data_derived = False

    if base is None:
        return LocatorScore(0, "weak", data_derived=True, warnings=[f"未知定位类型 {loc_type!r}"])
    if not text.strip():
        return LocatorScore(0, "weak", data_derived=True, warnings=["定位值为空"])

    score = base

    # 选择器类（css/xpath/testid）里出现中文自然语言 → 几乎必是把回显内容当选择器。
    if loc_type in _SELECTOR_TYPES and _CJK_PATTERN.search(text):
        score -= 50
        data_derived = True
        warnings.append("选择器含中文自然语言，疑为占位/数据而非真实选择器")

    # 模糊属性匹配（[class*=]、[attr^=] 等）。
    if _FUZZY_ATTR_PATTERN.search(text):
        score -= 30
        data_derived = True
        warnings.append("模糊属性匹配（[attr*=/^=/$=/~=]），稳定性差，建议改精确属性或降 fallback")

    # text 定位夹带操作性说明括号。
    if loc_type == "text" and _TEXT_INSTRUCTION_PATTERN.search(text):
        score -= 30
        data_derived = True
        warnings.append("text 夹带操作性说明括号，疑为占位而非真实可见文本")

    # 疑似动态值（长数字 / 长十六进制）——常见于订单号、UID、生成态 class。
    if _PURE_DIGITS_PATTERN.search(text) or _LONG_HEX_PATTERN.search(text):
        score -= 20
        data_derived = True
        warnings.append("含疑似动态值（长数字/十六进制），可能把具体数据烧进了定位")

    # 纯 text 定位本身是"稳定文本陷阱"，轻度提醒（不重复叠加已有 text 惩罚）。
    if loc_type == "text" and not warnings:
        warnings.append("纯文本定位属降权项，仅在无更好锚点时使用")

    score = max(0, min(100, score))
    return LocatorScore(score, _tier_for(score), data_derived=data_derived, warnings=warnings)


__all__ = ["LocatorScore", "score_locator"]
