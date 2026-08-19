from agentest.exploration.scoring import score_locator


def test_testid_is_strong() -> None:
    result = score_locator("testid", "contact-add")
    assert result.score == 100
    assert result.tier == "strong"
    assert result.data_derived is False
    assert result.warnings == []


def test_role_with_chinese_name_is_not_penalized() -> None:
    # role 类型不属于选择器类，中文可访问名合法，不该判数据派生。
    result = score_locator("role", "button", name="登录")
    assert result.score == 90
    assert result.data_derived is False


def test_css_with_chinese_is_data_derived() -> None:
    result = score_locator("css", "订单标题")
    assert result.data_derived is True
    assert result.tier == "weak"
    assert any("中文" in w for w in result.warnings)


def test_fuzzy_attr_penalized() -> None:
    result = score_locator("css", "[class*='setting']")
    assert result.data_derived is True
    assert any("模糊属性" in w for w in result.warnings)


def test_text_instruction_parens_penalized() -> None:
    result = score_locator("text", "订单标题（点击卡片标题区）")
    assert result.data_derived is True
    assert any("操作性" in w for w in result.warnings)


def test_dynamic_value_penalized() -> None:
    result = score_locator("css", "#order-HY20260805842845154A")
    assert result.data_derived is True
    assert any("动态值" in w for w in result.warnings)


def test_plain_text_gets_soft_note() -> None:
    result = score_locator("text", "保存")
    assert result.tier == "ok"
    assert result.data_derived is False
    assert any("降权" in w for w in result.warnings)


def test_unknown_type_is_zero() -> None:
    result = score_locator("magic", "whatever")
    assert result.score == 0
    assert result.data_derived is True


def test_empty_value_is_zero() -> None:
    result = score_locator("css", "   ")
    assert result.score == 0
    assert result.data_derived is True


def test_priority_order_between_types() -> None:
    testid = score_locator("testid", "x").score
    role = score_locator("role", "button").score
    css = score_locator("css", "div.card").score
    xpath = score_locator("xpath", "//div").score
    assert testid > role > css > xpath
