"""TP-001 示例：正常添加联系人。

这是结构示例，不连接真实系统执行。
"""

from agentest.browser import BrowserSession


def test_add_contact() -> None:
    with BrowserSession(headless=False) as browser:
        page = browser.goto("http://localhost:3000/contacts")
        page.get_by_role("button", name="添加联系人").click()
        page.get_by_label("姓名").fill("示例联系人")
        page.get_by_role("button", name="保存").click()
        assert page.get_by_text("示例联系人").is_visible()
