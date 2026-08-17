# versions 目录契约

## 目录职责

保存父级 System 的 Version 目录。

## 允许内容

- 每个 Version ID 对应一个目录。
- 本文件：目录契约。

## 文件职责

每个 Version 目录保存一个明确测试范围的需求、测试点和测试结果；测试点文件同时保留每个测试点的执行状态与结果记录。

## 更新规则

Version ID 在同一 System 内唯一。新的测试范围创建新的 Version，不静默覆盖已有 Version。

## 禁止事项

- 不把 Version 目录当成 Git 分支。
- 不把 System 级 Memory 或 Element Map 复制到这里。
- 不保存密码、Token、Cookie、Storage State 或其他凭据，也不保存无关应用文件。
- 测试后只更新测试点执行字段和已验证的版本事实；不得把未经确认的推测写入最终资产。

## 阅读策略

只阅读当前任务目标 Version 的契约和相关资产。
