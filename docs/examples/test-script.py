"""联系人新增测试组示例脚本。

本文件是 `docs/examples/` 下的平铺示例，真实资产路径为
`projects/<project-name>/systems/<system-name>/versions/<version-name>/test-scripts/contacts-add.py`。

关联 Test Case：TC-001、TC-002（同属"联系人新增"测试组，复用同一测试组级会话）。
前置条件：测试用例已批准；测试地址为已确认的测试环境；需要登录时由用户手动完成并确认。
不在脚本、日志或产物中保存账号、密码、Token、Cookie 或 Storage State。
运行命令：python -m pytest docs/examples/test-script.py -q。
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


def test_tc_001_add_contact_name_and_save(browser: BrowserSession) -> None:
    """验证 TC-001：填写联系人姓名并保存，新增联系人出现在列表中。"""
    page = browser.goto("<confirmed-test-url>/contacts")
    page.get_by_test_id("contact-add").click()
    page.get_by_label("姓名").fill("示例联系人")
    page.get_by_role("button", name="保存").click()
    assert page.get_by_text("示例联系人").is_visible()


def test_tc_002_full_add_contact_flow(browser: BrowserSession) -> None:
    """验证 TC-002：完整新增流程后，联系人在重新进入列表时仍然存在。"""
    page = browser.goto("<confirmed-test-url>/contacts")
    assert page.get_by_text("示例联系人").is_visible()
