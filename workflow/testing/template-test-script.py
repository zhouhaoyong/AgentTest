"""关联 TP-001 的可重复执行测试脚本模板。

前置条件：测试点已批准；如需登录，由用户手动完成后再继续。
不在脚本、日志或产物中保存账号、密码、Token、Cookie 或 Storage State。
"""

from agentest.browser import BrowserSession


def test_tp_001_feature_name() -> None:
    """验证 TP-001：替换为清晰、可观察的测试目标。"""
    # 仅在当前 Version 已批准的 Test Point 范围内实现稳定定位与断言。
    with BrowserSession(headless=False) as browser:
        page = browser.goto("<confirmed-test-url>")
        # 使用 data-testid、语义 locator 或稳定属性；不要使用动态 class 或坐标。
        assert page.url.startswith("<confirmed-test-url>")
