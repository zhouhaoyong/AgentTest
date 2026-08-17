# AgentTest Demo 总览

这是 AgentTest 的最小 Demo。它只用于帮助 Agent 和人理解资产之间的关系，不代表真实业务项目，也不用于执行正式测试。

## 阅读顺序

首次了解 AgentTest 资产结构时，按下面顺序阅读：

1. 先看本文件的树形结构。
2. 再看 Project、System 和 Version 的 YAML 配置。
3. 再看需求、测试用例、测试脚本和测试报告示例。
4. 最后看 Element Map 和 Memory，理解哪些知识应该跨 Version 沉淀。

## 资产树

真实业务资产的结构如下：

```text
Project
└── System
    ├── Element Map
    ├── Memory
    └── Version
        ├── Requirement Source
        ├── Requirement
        ├── Test Cases
        ├── Test Scripts
        └── Test Report
```

Demo 为了方便发现和阅读，将示例内容平铺在当前目录的 `examples/` 下：

```text
docs/
├── demo.md                         # 本入口：树形结构和阅读说明
└── examples/                       # 平铺的示例内容
    ├── project.yaml                # Project 配置
    ├── project-requirement.md      # Project 目录契约
    ├── system.yaml                 # System 配置
    ├── system-requirement.md       # System 目录契约
    ├── element-map.yaml            # Element Map 机器可读示例
    ├── element-map.md              # Element Map 人工索引示例
    ├── memory.md                   # Memory 示例
    ├── version.yaml                # Version 配置
    ├── version-requirement.md      # Version 目录契约
    ├── source.md                   # 原始需求来源示例
    ├── requirement.md              # examples 目录契约
    ├── 20260814_V2026.08.04_demo-web.md # 结构化需求示例
    ├── test-cases.md              # 测试用例平铺示例；真实位置见 Version/test-cases/test-cases.md
    ├── test-script.py              # 可重复执行的测试脚本示例
    └── report.md                   # 测试报告（建议版）示例
```

平铺 Demo 只是阅读方式。真实业务资产仍然必须遵循 `Project → System → Version` 的目录结构，并放在 `projects/` 下。

## 示例文件

### Project

- [project.yaml](examples/project.yaml)
- [Project 目录契约](examples/project-requirement.md)

### System

- [system.yaml](examples/system.yaml)
- [System 目录契约](examples/system-requirement.md)
- [Element Map 示例](examples/element-map.md)
- [Element Map YAML 示例](examples/element-map.yaml)
- [Memory 示例](examples/memory.md)

### Version

- [version.yaml](examples/version.yaml)
- [Version 目录契约](examples/version-requirement.md)
- [examples 目录契约](examples/requirement.md)
- [原始需求来源](examples/source.md)
- [结构化需求](examples/20260814_V2026.08.04_demo-web.md)
- [测试用例](examples/test-cases.md)
- [测试脚本](examples/test-script.py)
- [测试报告（建议版）](examples/report.md)

## 注意事项

- Demo 不保存真实需求、账号、密码、Token、Cookie 或正式测试结果。
- Demo 中的 Version 测试脚本只展示结构，不保证可以直接连接真实系统执行。
- Agent 开始真实测试前，仍需读取目标 Project、System 和 Version 的目录契约。
