"""TC-001 示例：正常添加联系人。

关联 Test Case：TC-001。
前置条件：测试用例已批准；测试地址可达；登录由用户手动完成。
运行方式：python -m pytest docs/examples/test-script.py -q。
"""

from agentest.browser import BrowserSession


def test_add_contact() -> None:
    with BrowserSession(headless=False) as browser:
        page = browser.goto("http://localhost:3000/contacts")
        page.get_by_role("button", name="添加联系人").click()
        page.get_by_label("姓名").fill("示例联系人")
        page.get_by_role("button", name="保存").click()
        assert page.get_by_text("示例联系人").is_visible()
