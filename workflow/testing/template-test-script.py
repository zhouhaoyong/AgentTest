"""关联同一测试组的可重复执行测试脚本模板。

前置条件：测试点已批准；如需登录，由用户手动完成后再继续。
不在脚本、日志或产物中保存账号、密码、Token、Cookie 或 Storage State。
"""

from collections.abc import Iterator

import pytest

from agentest.browser import BrowserSession
from agentest.schemas.system import TestEnvironment


@pytest.fixture(scope="module")
def browser() -> Iterator[BrowserSession]:
    # 实际项目应传入 System 与 Version 合并后的最终测试环境。
    environment = TestEnvironment.defaults_for_type("web")
    with BrowserSession(test_environment=environment) as session:
        yield session


def test_tp_001_feature_name(browser: BrowserSession) -> None:
    """验证 TP-001：替换为清晰、可观察的测试目标。"""
    # 仅在当前 Version 或联动范围已批准的 Test Point 范围内实现稳定定位与断言。
    page = browser.goto("<confirmed-test-url>")
    # 使用 data-testid、语义 locator 或稳定属性；不要使用动态 class 或坐标。
    assert page.url.startswith("<confirmed-test-url>")
    # 业务明确打开新页签时，再显式创建或捕获辅助 Page；不要让普通 goto 隐式创建新页签。
