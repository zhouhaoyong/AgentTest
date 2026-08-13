# run 目录契约

## 目录职责

保存本 Version 最近一次正式测试的执行结果。

## 允许内容

- `result.md`：每个 Test Point 的最新状态。
- 本文件：目录契约。

## 文件职责

`result.md` 必须记录 PASS、FAIL、BLOCKED 或 NOT RUN，并说明非 PASS 状态的原因。

## 更新规则

只有执行已批准的 Test Points 后才能更新。

## 禁止事项

- v0.1 不创建重复 run 历史目录。
- 关键测试维度未执行时，不得声称测试完成。

## 阅读策略

写入结果前，先读已批准的 Test Points 和相关 System 索引。
