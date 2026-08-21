"""关联同一元素地图模块 / 业务域的可重复执行测试脚本模板。

覆盖用例：TC-001、TC-002（同一模块的用例聚在同一脚本文件，各为一个测试函数）。
前置条件：测试用例已批准；测试地址为已确认的测试环境；目标数据已就绪；用户手动登录并确认完成。
手动登录：启动隔离 Chrome 后由用户手动登录，Agent 不填写或保存凭据。
不在脚本、日志或产物中保存账号、密码、Token、Cookie 或 Storage State。
运行命令：python -m pytest <this-script.py> -q。

归组约定（W1-4）：一个元素地图模块 / 功能域对应一个脚本文件；公共连接器（登录、
导航、弹窗、列表切换）抽到单独文件复用，不在每个用例里重复。

数据约定（W1-4 / W1-5）：脚本不硬编码具体业务 id（订单号 / UID / 金额）；改为运行时
按条件发现目标样本（见 discover_* 辅助）。确需固定样本时抽到显式 fixture 并标注
"依赖数据前置"，缺失即抛出结构化的数据前置说明，不静默跳过或误判为业务 Bug。

数据缺口处理约定：前置数据不就绪时，抛出 DataPrerequisiteError（下方定义）而非
pytest.skip——静默 skip 会让用例在报告里凭空消失。该用例应记为 BLOCKED（环境数据缺口，
非功能 Bug），并把"缺什么数据 / 卡在哪 / 需哪端联动"写进报告的数据前置清单。

缺少数据时：记录为 BLOCKED，并写入报告的数据前置清单。
结果判断：以测试用例中的 PASS / FAIL / BLOCKED / NOT RUN 为准。

每个正式 `.py` 文件都必须保留以上六类元数据：覆盖用例、前置条件、手动登录、运行命令、
缺少数据时的处理和结果判断；公共连接器也要单独说明自身用途，不能依赖 `conftest.py` 代写。
"""

from collections.abc import Iterator

import pytest

from agentest.browser import BrowserSession
from agentest.schemas.system import TestEnvironment


class DataPrerequisiteError(RuntimeError):
    """前置数据未就绪：对应用例记为 BLOCKED（环境数据缺口，非功能 Bug），不得静默跳过。"""


@pytest.fixture(scope="module")
def browser() -> Iterator[BrowserSession]:
    # 实际项目应传入 System 与 Version 合并后的最终测试环境。
    environment = TestEnvironment.defaults_for_type("web")
    with BrowserSession(test_environment=environment) as session:
        yield session


def discover_target_row(browser: BrowserSession) -> str:
    """运行时按条件发现一个满足前置的样本，返回其稳定引用（而非硬编码 id）。

    找不到符合条件的数据时，抛出带"数据前置说明"的错误，交由数据自愈 / 用户补数据，
    不要退化为对某个写死的订单号断言。
    """
    page = browser.goto("<confirmed-test-url>")
    # 用结构定位（行模板 / 容器）配合运行时条件筛选，例如"一个已逾期且含接单用户的订单"。
    candidates = page.locator("<stable-row-selector>")
    if candidates.count() == 0:
        # 缺什么数据 / 需哪端联动，写进报告的数据前置清单；本用例记 BLOCKED，不是 FAIL，
        # 也不静默 skip——抛结构化错误让缺口在结果里显式可见。
        raise DataPrerequisiteError("数据前置未就绪：缺少满足条件的样本")
    return candidates.first.get_attribute("<stable-ref-attr>") or ""


def test_tp_001_read_only_feature(browser: BrowserSession) -> None:
    """只读用例 TC-001：运行时发现数据，只断言结构与回显，不做写操作。"""
    target = discover_target_row(browser)
    assert target, "未发现目标样本"
    # 使用 data-testid、语义 locator 或稳定属性；不要使用动态 class 或坐标。


def test_tp_002_write_op_feature(browser: BrowserSession) -> None:
    """写操作用例 TC-002：真实可复跑（前置数据→执行→断言回显→必要时幂等）。

    仅在已确认测试环境 + 已授权的写操作范围内实现；不留"只读骨架"。
    """
    # 1) 前置：运行时准备 / 发现本次写操作所需数据（缺失走数据自愈或结构化上报，不硬编码）。
    target = discover_target_row(browser)
    # 2) 执行：在稳定定位下完成写操作（提交 / 审批 / 保存等）。
    # 3) 断言：在目标页面或数据中核对回显，成功提示不等于通过。
    # 4) 幂等：可重复运行时先判断 / 复位状态，避免二次执行污染或误判。
    assert target, "写操作前置数据未就绪"
