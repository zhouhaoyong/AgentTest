# scaffold 目录契约

## 目录职责

根据已校验数据和模板创建 Project、System、Version 文件树。

## 允许内容

- `project.py`：创建 Project。
- `system.py`：创建 System。
- `version.py`：创建 Version。
- `common.py`：共享的文件系统安全校验。
- `templates.py`：读取模板。
- `__init__.py`：导出创建函数。
- 本文件：目录契约。

## 文件职责

创建逻辑负责 ID 校验、父目录检查、重复目标拒绝、模板写入和部分失败回滚。

## 更新规则

使用 pathlib 和模板；创建失败时不得留下本次创建的半成品目录。

## 禁止事项

- 不删除已有用户资产。
- 不执行 Git 操作。
- 不把业务测试行为塞进脚手架创建函数。

## 阅读策略

先读本契约，再阅读当前需要修改的创建模块。
