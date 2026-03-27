# CoderResearch 开发指南

## 项目概述

CoderResearch 是一个面向质性研究的 AI 辅助编码系统，基于扎根理论方法论实现三级编码工作流（开放编码 → 轴心编码 → 选择性编码）。

## 系统架构

```
CoderResearch/
├── ImportEngine/          # 数据导入与预处理
├── CodeEngine/            # 三级编码引擎
│   ├── ir/               # 中间表示（核心数据结构）
│   ├── open_coding/      # 开放编码
│   ├── axial_coding/     # 轴心编码
│   └── selective_coding/ # 选择性编码
├── TheoryEngine/          # 理论建构与可视化
├── MemoEngine/            # 备忘录撰写
├── ForumEngine/           # 多 Agent 协作
├── CodebookDB/            # 代码本数据库
├── ReportEngine/          # 报告生成
│   └── exporters.py      # 第三方软件导出
├── utils/                 # 工具模块
│   ├── llm_client.py     # LLM 客户端
│   └── session_manager.py # 会话管理
└── tests/                 # 测试套件
```

## 架构重构 (v2.0)

### 分层架构

```
CLI Layer (cli/)
├── commands.py     # 命令定义
├── formatters.py   # 输出格式化
└── dependencies.py # 依赖注入

Service Layer (services/)
├── coding_service.py  # 编码工作流
└── import_service.py  # 导入工作流

Repository Layer (repositories/)
├── base.py               # Repository 基类
├── code_repository.py    # 代码 CRUD
├── category_repository.py # 类属 CRUD
└── session_repository.py  # 会话管理

Engine Layer (保留)
├── CodeEngine/
├── ImportEngine/
├── TheoryEngine/
├── MemoEngine/
├── ForumEngine/
└── ReportEngine/
```

### 迁移指南

旧代码 (v1.x):
```python
from ImportEngine.agent import ImportEngine
engine = ImportEngine()
```

新代码 (v2.0):
```python
from cli.dependencies import get_import_service
service = get_import_service()
segments = service.import_file("data.txt")
```

向后兼容 (v2.0):
```python
from compatibility import get_legacy_import_engine
engine = get_legacy_import_engine()  # 发出 DeprecationWarning
```

## 核心概念

### 编码单元 IR

所有数据通过中间表示（IR）传递，定义在 `CodeEngine/ir/code_ir.py`：

```python
@dataclass
class TextSegment:
    id: str
    content: str
    source: str           # 数据来源
    position: Tuple[int, int]

@dataclass
class CodeUnit:
    id: str
    text_segment: TextSegment
    code_label: str       # 代码标签
    code_definition: str  # 代码定义
    confidence: float     # 置信度
    created_by: CodeSource  # HUMAN/AI/COLLABORATION

@dataclass
class Category:
    id: str
    name: str
    definition: str
    codes: List[str]      # 包含的代码 ID
```

### 编码流程

```
原始文本 → TextSegment → CodeUnit (开放编码) → Category (轴心编码) → 理论框架 (选择性编码)
```

## LLM 客户端

### 配置

支持多提供商，通过环境变量或配置文件设置：

```bash
# .env 文件
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4

# 或使用 Moonshot (Kimi)
OPENAI_BASE_URL=https://api.moonshot.cn/v1
DEFAULT_MODEL=moonshot-v1-8k

# 或使用本地 Ollama（无需 API Key）
OLLAMA_HOST=http://localhost:11434
```

### 使用

```python
from utils.llm_client import llm_client, LLMProvider

# 健康检查
status = llm_client.health_check()

# 普通对话
response = llm_client.chat([
    {"role": "user", "content": "分析这段文本..."}
])

# 生成 JSON
result = llm_client.generate_json(prompt, schema={...})

# 流式输出
for chunk in llm_client.chat_stream(messages):
    print(chunk, end="")
```

### 降级策略

1. API 调用失败时自动重试（指数退避）
2. Rate Limit 时等待后重试
3. 远程 API 失败时自动切换到 Ollama（如果可用）
4. 所有方式失败时返回模拟响应

## 人工审核机制

### 开放编码审核

AI 生成的编码建议需要人工审核后才能入库：

```python
from CodeEngine.open_coding.agent import OpenCodingAgent, OpenCodingConfig

agent = OpenCodingAgent(OpenCodingConfig(
    require_human_review=True,      # 启用人工审核
    auto_approve_high_confidence=False  # 不自动通过
))

# 编码（不自动审核）
agent.code_segment(segment, auto_review=False)

# 获取待审核建议
pending = agent.review_manager.pending_reviews

# 批准
agent.review_manager.approve(suggestion_id, comment="审核通过")

# 拒绝
agent.review_manager.reject(suggestion_id, comment="不合适")

# 修改后批准
agent.review_manager.modify_and_approve(
    suggestion_id, new_label, new_def, comment
)
```

### CLI 交互式审核

在命令行中使用：

```bash
# 启用审核
python app.py open-code --require-review

# 跳过审核（快速模式）
python app.py open-code --no-require-review
```

## 会话管理

使用数据库存储会话数据（替代 pickle）：

```python
from utils.session_manager import SessionManager

manager = SessionManager()

# 保存会话
manager.save_session({
    "segments": [...],
    "open_codes": [...]
}, session_id="default")

# 加载会话
session = manager.load_session("default")

# 备份
manager.backup_session("backup.json")

# 恢复
manager.restore_session("backup.json")
```

## 导出格式

### 支持的平台

```python
from ReportEngine.exporters import NVivoExporter, AtlasTiExporter

# NVivo
nvivo = NVivoExporter()
nvivo.export(codes, categories, "./outputs/nvivo")

# Atlas.ti
atlasti = AtlasTiExporter()
atlasti.export(codes, categories, "./outputs/atlasti")
```

### CLI 导出

```bash
# 标准报告
python app.py report --format markdown
python app.py report --format docx

# 第三方软件
python app.py report --format nvivo
python app.py report --format atlasti
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块
pytest tests/test_llm_client.py
pytest tests/test_open_coding.py

# 带覆盖率
pytest --cov=. --cov-report=html
```

### 测试分类

- `test_llm_client.py` - LLM 客户端、重试机制、降级策略
- `test_open_coding.py` - 开放编码、审核机制
- `test_session_manager.py` - 会话管理、序列化

## 开发规范

### 代码风格

- 使用类型注解
- 函数文档字符串遵循 Google Style
- 复杂逻辑添加注释

### 提交前检查

```bash
# 类型检查
mypy .

# 代码格式
black .
isort .

# 测试
pytest
```

## 常见问题

### Q: API Key 未设置如何处理？

A: 系统会自动降级到 Ollama 或返回模拟数据。建议：
1. 设置 OPENAI_API_KEY 环境变量
2. 或启动本地 Ollama 服务

### Q: 如何提高编码质量？

A: 
1. 使用 `--require-review` 启用人工审核
2. 调整 `min_confidence` 阈值
3. 使用 in_vivo 编码风格保留受访者原话

### Q: 会话数据存储在哪里？

A: 默认存储在 SQLite 数据库（`coderresearch.db`），不再使用 pickle。

### Q: 如何导出到其他质性分析软件？

A: 支持 NVivo 和 Atlas.ti 格式，使用 `--format nvivo` 或 `--format atlasti`。

## 路线图

- [x] 多 LLM 提供商支持
- [x] 人工审核机制
- [x] 会话持久化到数据库
- [x] NVivo/Atlas.ti 导出
- [ ] Web UI 界面
- [ ] 多语言支持
- [ ] 协作编码（多用户）
- [ ] 代码版本分支管理
