# Element Map 示例

Element Map 属于 System，记录测试真正使用且未来可能复用的页面元素和定位方式。

| 模块 | 页面 | 元素 | 主定位 | 备用定位 | 稳定性依据 | 验证视口 |
| --- | --- | --- | --- | --- | --- | --- |
| 联系人列表 | `/contacts` | 添加联系人按钮 | `get_by_test_id("contact-add")` | `get_by_role("button", name="添加联系人")` | `data-testid` | web 最大化 1920×1080 |
| 联系人表单 | `/contacts/new` | 姓名输入框 | `get_by_label("姓名")` | `[name="contact_name"]` | 表单 label / name | web 最大化 1920×1080 |

定位优先使用专用测试属性和语义定位，CSS 只使用稳定属性，XPath 仅作为最后兜底。定位串本身不受窗口大小影响，但布局相关的元素随视口变化，因此记录验证时的视口/窗口尺寸（web 真实最大化尺寸随机器变，务必写明）。真实 Element Map 应放在 System 的 `element-map/` 下，并通过 `index.md` 索引模块。
