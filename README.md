# CoderResearch

## 定性研究智能编码系统

CoderResearch 是一个面向质性研究（Qualitative Research）的多 Agent 编码系统，基于扎根理论（Grounded Theory）方法论，支持从数据导入到理论建构的全流程自动化辅助。

## 🏗️ 系统架构（v2.0 分层架构）

```
CoderResearch/
├── cli/                   # CLI 层 - 命令行界面
│   ├── commands.py        # 命令定义
│   ├── formatters.py      # 输出格式化
│   └── dependencies.py    # 依赖注入
│
├── services/              # Service 层 - 业务工作流
│   ├── coding_service.py  # 编码工作流服务
│   └── import_service.py  # 导入工作流服务
│
├── repositories/          # Repository 层 - 数据访问
│   ├── base.py            # Repository 基类
│   ├── code_repository.py      # 代码 CRUD
│   ├── category_repository.py  # 类属 CRUD
│   └── session_repository.py   # 会话管理
│
├── CodeEngine/            # Engine 层 - 编码引擎
│   ├── open_coding/       # 开放编码
│   ├── axial_coding/      # 轴心编码
│   └── selective_coding/  # 选择性编码
│
├── ImportEngine/          # 数据导入与预处理
├── TheoryEngine/          # 理论建构与可视化
├── MemoEngine/            # 备忘录撰写与反思
├── ForumEngine/           # 多 Agent 编码协作
├── CodebookDB/            # 代码本数据库与版本控制
├── ReportEngine/          # 研究报告生成
│
└── compatibility.py       # 向后兼容层（v1.x 迁移用）
```

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 运行示例
python app.py --help

# 完整工作流示例
python app.py import-data data.txt
python app.py list-codes
```

## 🔄 架构分层说明

| 层级 | 职责 | 示例 |
|------|------|------|
| **CLI** | 参数解析、用户交互 | `app.py version` |
| **Service** | 业务逻辑编排 | `CodingService.run_full_pipeline()` |
| **Engine** | 核心算法实现 | `OpenCodingAgent.code_segment()` |
| **Repository** | 数据持久化 | `CodeRepository.save(entity)` |

## 📚 核心功能

- **智能编码辅助**：AI 辅助开放编码，逐行生成初始代码
- **信度检验**：多编码者一致性计算（Kappa 系数）
- **负向案例追踪**：自动标记不符合理论的案例
- **版本控制**：代码演化历史追踪（Git 式管理）
- **协作讨论**：AI 质疑者角色，主动挑战研究者假设
- **多格式导出**：支持 NVivo、Atlas.ti、DOCX、LaTeX

## 🆕 v2.0 新特性

- **分层架构**：清晰的 CLI → Service → Engine → Repository 分层
- **依赖注入**：通过 `cli/dependencies.py` 管理服务生命周期
- **Repository 模式**：统一的数据访问抽象
- **向后兼容**：`compatibility.py` 提供 v1.x API 兼容

## 📖 使用指南

### 基本命令

```bash
# 系统健康检查
python app.py health

# 导入数据
python app.py import-data interview.txt --segment-type paragraph

# 查看代码本
python app.py list-codes

# 显示版本
python app.py version
```

### 程序化使用

```python
# 新 API (v2.0 推荐)
from cli.dependencies import get_coding_service, get_import_service

import_service = get_import_service()
segments = import_service.import_file("data.txt")

coding_service = get_coding_service()
result = coding_service.run_open_coding(segments)
```

```python
# 向后兼容 (v1.x)
from compatibility import get_legacy_import_engine

engine = get_legacy_import_engine()  # 会发出 DeprecationWarning
```

## 📄 许可证

MIT License
