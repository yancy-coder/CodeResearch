# CoderResearch 分层架构重构计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 CoderResearch 从单文件 CLI 重构为分层架构（CLI → Service → Engine → Repository），保持所有测试通过

**Architecture:** 
- 引入 Repository 层统一数据库访问
- 引入 Service 层封装业务工作流
- CLI 层只负责参数解析和界面渲染
- Engine 层专注于编码算法实现

**Tech Stack:** Python 3.13, SQLAlchemy 2.0, Typer, Rich, Pytest

---

## 当前问题

- `app.py` 695 行，包含 CLI + 业务逻辑 + 数据流控制
- SessionManager、Database 被多处直接调用，耦合度高
- 缺少 Repository 抽象，数据库操作散落在各处

## 目标架构

```
cli/              # CLI 层
  commands.py     # 命令定义
  formatters.py   # 输出格式化

services/         # Service 层
  coding_service.py      # 编码工作流
  import_service.py      # 导入工作流
  report_service.py      # 报告工作流

repositories/     # Repository 层
  code_repository.py     # 代码 CRUD
  category_repository.py # 类属 CRUD
  session_repository.py  # 会话管理

engines/          # Engine 层（保留原有）
  open_coding/
  axial_coding/
  selective_coding/
  import_engine/
  theory_engine/
  memo_engine/
  forum_engine/
  report_engine/

models/           # 领域模型（从 ir/ 迁移）
  code_ir.py

interfaces/       # 接口定义
  repository.py
  engine.py
```

---

## Phase 1: 创建 Repository 层

### Task 1: 创建 Repository 基础接口

**Files:**
- Create: `repositories/__init__.py`
- Create: `repositories/base.py`

- [ ] **Step 1: 创建 Repository 基类接口**

```python
# repositories/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Repository 模式基类"""
    
    @abstractmethod
    def get(self, id: str) -> Optional[T]: ...
    
    @abstractmethod
    def list(self, **filters) -> List[T]: ...
    
    @abstractmethod
    def save(self, entity: T) -> str: ...
    
    @abstractmethod
    def delete(self, id: str) -> bool: ...

class UnitOfWork:
    """工作单元模式 - 管理事务"""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None
    
    def __enter__(self):
        self.session = self.session_factory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()
```

- [ ] **Step 2: 运行现有测试确保基础正常**

```bash
pytest tests/ -v --tb=short
```
Expected: 49 tests pass

- [ ] **Step 3: Commit**

```bash
git add repositories/
git commit -m "feat: add repository base interfaces"
```

---

### Task 2: 创建 Code Repository

**Files:**
- Create: `repositories/code_repository.py`
- Create: `tests/repositories/test_code_repository.py`

- [ ] **Step 1: 编写测试 - 代码仓库基本 CRUD**

```python
# tests/repositories/test_code_repository.py
import pytest
from datetime import datetime
from repositories.code_repository import CodeRepository, CodeEntity
from CodebookDB.db import CodebookDB

@pytest.fixture
def db():
    # 使用内存数据库测试
    return CodebookDB("sqlite:///:memory:")

@pytest.fixture
def repository(db):
    return CodeRepository(db)

@pytest.fixture
def sample_code():
    return CodeEntity(
        id="test-001",
        label="测试代码",
        definition="这是一个测试代码定义",
        level="open",
        created_by="human"
    )

def test_save_code(repository, sample_code):
    code_id = repository.save(sample_code)
    assert code_id == "test-001"

def test_get_code(repository, sample_code):
    repository.save(sample_code)
    code = repository.get("test-001")
    assert code is not None
    assert code.label == "测试代码"

def test_list_codes(repository):
    for i in range(3):
        code = CodeEntity(
            id=f"code-{i}",
            label=f"代码{i}",
            definition=f"定义{i}",
            level="open"
        )
        repository.save(code)
    
    codes = repository.list()
    assert len(codes) == 3

def test_filter_by_level(repository):
    repository.save(CodeEntity(id="c1", label="A", level="open"))
    repository.save(CodeEntity(id="c2", label="B", level="axial"))
    
    open_codes = repository.list(level="open")
    assert len(open_codes) == 1
    assert open_codes[0].label == "A"

def test_delete_code(repository, sample_code):
    repository.save(sample_code)
    result = repository.delete("test-001")
    assert result is True
    assert repository.get("test-001") is None
```

- [ ] **Step 2: 运行测试确保失败**

```bash
pytest tests/repositories/test_code_repository.py -v
```
Expected: ImportError / ModuleNotFoundError

- [ ] **Step 3: 实现 Code Entity 和 Repository**

```python
# repositories/code_repository.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from repositories.base import Repository

@dataclass
class CodeEntity:
    """代码实体 - 领域层"""
    id: str
    label: str
    definition: str = ""
    level: str = "open"  # open/axial/selective
    category_id: Optional[str] = None
    created_by: str = "human"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"

class CodeRepository(Repository[CodeEntity]):
    """代码 Repository"""
    
    def __init__(self, db: CodebookDB):
        self.db = db
    
    def get(self, id: str) -> Optional[CodeEntity]:
        data = self.db.get_code(id)
        if not data:
            return None
        return self._to_entity(data)
    
    def list(self, **filters) -> List[CodeEntity]:
        level = filters.get('level')
        codes_data = self.db.list_codes(level)
        return [self._to_entity(c) for c in codes_data]
    
    def save(self, entity: CodeEntity) -> str:
        data = {
            "id": entity.id,
            "label": entity.label,
            "definition": entity.definition,
            "level": entity.level,
            "created_by": entity.created_by
        }
        return self.db.save_code(data)
    
    def delete(self, id: str) -> bool:
        # 暂时使用底层 session 直接删除
        session = self.db.Session()
        try:
            from CodebookDB.db import CodeModel
            code = session.query(CodeModel).filter_by(id=id).first()
            if code:
                session.delete(code)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def _to_entity(self, data: dict) -> CodeEntity:
        return CodeEntity(
            id=data["id"],
            label=data["label"],
            definition=data.get("definition", ""),
            level=data.get("level", "open"),
            created_by=data.get("created_by", "human")
        )
```

- [ ] **Step 4: 运行测试确保通过**

```bash
pytest tests/repositories/test_code_repository.py -v
```
Expected: 6 tests pass

- [ ] **Step 5: Commit**

```bash
git add repositories/code_repository.py tests/repositories/
git commit -m "feat: add code repository with CRUD operations"
```

---

### Task 3: 创建 Category Repository

**Files:**
- Create: `repositories/category_repository.py`
- Create: `tests/repositories/test_category_repository.py`

- [ ] **Step 1: 编写测试**

```python
# tests/repositories/test_category_repository.py
import pytest
from repositories.category_repository import CategoryRepository, CategoryEntity

@pytest.fixture
def repository():
    from CodebookDB.db import CodebookDB
    db = CodebookDB("sqlite:///:memory:")
    return CategoryRepository(db)

def test_save_and_get_category(repository):
    cat = CategoryEntity(
        id="cat-001",
        name="用户体验",
        definition="关于用户体验的类属"
    )
    repository.save(cat)
    
    retrieved = repository.get("cat-001")
    assert retrieved.name == "用户体验"

def test_hierarchical_categories(repository):
    parent = CategoryEntity(id="p1", name="父类属")
    child = CategoryEntity(id="c1", name="子类属", parent_id="p1")
    
    repository.save(parent)
    repository.save(child)
    
    children = repository.get_children("p1")
    assert len(children) == 1
    assert children[0].name == "子类属"
```

- [ ] **Step 2: 实现 Category Repository**

```python
# repositories/category_repository.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from repositories.base import Repository

@dataclass
class CategoryEntity:
    """类属实体"""
    id: str
    name: str
    definition: str = ""
    parent_id: Optional[str] = None
    properties: List[str] = field(default_factory=list)
    dimensions: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class CategoryRepository(Repository[CategoryEntity]):
    """类属 Repository"""
    
    def __init__(self, db: CodebookDB):
        self.db = db
        self.engine = db.engine
    
    def get(self, id: str) -> Optional[CategoryEntity]:
        from CodebookDB.db import CategoryModel
        session = self.db.Session()
        try:
            cat = session.query(CategoryModel).filter_by(id=id).first()
            return self._to_entity(cat) if cat else None
        finally:
            session.close()
    
    def list(self, **filters) -> List[CategoryEntity]:
        from CodebookDB.db import CategoryModel
        session = self.db.Session()
        try:
            query = session.query(CategoryModel)
            if 'parent_id' in filters:
                query = query.filter_by(parent_id=filters['parent_id'])
            cats = query.all()
            return [self._to_entity(c) for c in cats]
        finally:
            session.close()
    
    def save(self, entity: CategoryEntity) -> str:
        from CodebookDB.db import CategoryModel
        session = self.db.Session()
        try:
            cat = CategoryModel(
                id=entity.id,
                name=entity.name,
                definition=entity.definition,
                parent_id=entity.parent_id,
                properties=entity.properties,
                dimensions=entity.dimensions
            )
            session.merge(cat)  # merge 支持更新
            session.commit()
            return entity.id
        finally:
            session.close()
    
    def delete(self, id: str) -> bool:
        from CodebookDB.db import CategoryModel
        session = self.db.Session()
        try:
            cat = session.query(CategoryModel).filter_by(id=id).first()
            if cat:
                session.delete(cat)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_children(self, parent_id: str) -> List[CategoryEntity]:
        return self.list(parent_id=parent_id)
    
    def _to_entity(self, model) -> CategoryEntity:
        return CategoryEntity(
            id=model.id,
            name=model.name,
            definition=model.definition or "",
            parent_id=model.parent_id,
            properties=model.properties or [],
            dimensions=model.dimensions or {}
        )
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/repositories/test_category_repository.py -v
```

- [ ] **Step 4: Commit**

```bash
git add repositories/category_repository.py tests/repositories/test_category_repository.py
git commit -m "feat: add category repository"
```

---

### Task 4: 创建 Session Repository

**Files:**
- Create: `repositories/session_repository.py`
- Modify: `utils/session_manager.py` (使其使用新 repository)

- [ ] **Step 1: 创建 Session Entity 和 Repository**

```python
# repositories/session_repository.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import json

@dataclass
class SessionEntity:
    """会话实体"""
    id: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class SessionRepository:
    """会话 Repository - 包装原有 SessionManager"""
    
    def __init__(self, db: CodebookDB):
        self.db = db
    
    def get(self, session_id: str = "default") -> Optional[SessionEntity]:
        from CodebookDB.db import SessionModel
        session = self.db.Session()
        try:
            record = session.query(SessionModel).filter_by(id=session_id).first()
            if record:
                return SessionEntity(
                    id=record.id,
                    data=record.data or {},
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
            return None
        finally:
            session.close()
    
    def save(self, entity: SessionEntity) -> str:
        from CodebookDB.db import SessionModel
        session = self.db.Session()
        try:
            record = session.query(SessionModel).filter_by(id=entity.id).first()
            if record:
                record.data = entity.data
                record.updated_at = datetime.now()
            else:
                record = SessionModel(
                    id=entity.id,
                    data=entity.data,
                    created_at=entity.created_at,
                    updated_at=entity.updated_at
                )
                session.add(record)
            session.commit()
            return entity.id
        finally:
            session.close()
    
    def delete(self, session_id: str) -> bool:
        from CodebookDB.db import SessionModel
        session = self.db.Session()
        try:
            record = session.query(SessionModel).filter_by(id=session_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        finally:
            session.close()
```

- [ ] **Step 2: 测试 Session Repository**

```bash
python -c "
from repositories.session_repository import SessionRepository, SessionEntity
from CodebookDB.db import CodebookDB

db = CodebookDB('sqlite:///:memory:')
repo = SessionRepository(db)

# 测试保存
session = SessionEntity(id='test', data={'key': 'value'})
repo.save(session)

# 测试读取
retrieved = repo.get('test')
assert retrieved.data['key'] == 'value'
print('Session repository test passed')
"
```

- [ ] **Step 3: Commit**

```bash
git add repositories/session_repository.py
git commit -m "feat: add session repository"
```

---

## Phase 2: 创建 Service 层

### Task 5: 创建 Coding Service

**Files:**
- Create: `services/__init__.py`
- Create: `services/coding_service.py`
- Create: `tests/services/test_coding_service.py`

- [ ] **Step 1: 编写测试 - Coding Service 工作流**

```python
# tests/services/test_coding_service.py
import pytest
from unittest.mock import Mock, MagicMock
from services.coding_service import CodingService
from repositories.code_repository import CodeEntity
from CodeEngine.ir.code_ir import TextSegment

@pytest.fixture
def mock_repositories():
    return {
        'code': Mock(),
        'category': Mock(),
        'session': Mock()
    }

@pytest.fixture
def mock_engines():
    return {
        'open_coding': Mock(),
        'axial_coding': Mock(),
        'selective_coding': Mock()
    }

@pytest.fixture
def service(mock_repositories, mock_engines):
    return CodingService(
        code_repo=mock_repositories['code'],
        category_repo=mock_repositories['category'],
        session_repo=mock_repositories['session'],
        engines=mock_engines
    )

def test_open_coding_workflow(service, mock_engines, mock_repositories):
    # Mock 引擎返回
    segment = TextSegment(id="s1", content="测试文本", source="test.txt", position=(0, 8))
    mock_codes = [Mock(code_label="代码1", code_definition="定义1", confidence=0.9)]
    mock_engines['open_coding'].batch_code.return_value = {
        'approved_codes': mock_codes,
        'pending_reviews': []
    }
    
    # 执行工作流
    result = service.run_open_coding([segment])
    
    # 验证引擎被调用
    mock_engines['open_coding'].batch_code.assert_called_once()
    # 验证代码被保存
    mock_repositories['code'].save.assert_called()

def test_full_coding_pipeline(service, mock_engines):
    # 测试完整工作流
    segments = [
        TextSegment(id="s1", content="文本1", source="t.txt", position=(0, 3))
    ]
    
    # Mock 各阶段返回
    mock_engines['open_coding'].batch_code.return_value = {
        'approved_codes': [Mock(code_label="代码", code_definition="定义")],
        'pending_reviews': []
    }
    mock_engines['axial_coding'].categorize_codes.return_value = []
    mock_engines['selective_coding'].identify_core_category.return_value = None
    
    # 执行
    result = service.run_full_pipeline(segments)
    
    # 验证所有引擎被调用
    mock_engines['open_coding'].batch_code.assert_called_once()
    mock_engines['axial_coding'].categorize_codes.assert_called_once()
```

- [ ] **Step 2: 实现 Coding Service**

```python
# services/coding_service.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from CodeEngine.ir.code_ir import TextSegment, CodeUnit
from repositories.code_repository import CodeRepository, CodeEntity
from repositories.category_repository import CategoryRepository
from repositories.session_repository import SessionRepository

@dataclass
class CodingResult:
    """编码结果"""
    success: bool
    codes: List[CodeUnit]
    categories: List[Any]
    core_category: Optional[Any]
    message: str = ""

class CodingService:
    """编码服务 - 协调各 Engine 完成编码工作流"""
    
    def __init__(
        self,
        code_repo: CodeRepository,
        category_repo: CategoryRepository,
        session_repo: SessionRepository,
        engines: Dict[str, Any]
    ):
        self.code_repo = code_repo
        self.category_repo = category_repo
        self.session_repo = session_repo
        self.engines = engines
    
    def run_open_coding(
        self,
        segments: List[TextSegment],
        config: Optional[Dict] = None
    ) -> CodingResult:
        """运行开放编码"""
        open_coding = self.engines.get('open_coding')
        if not open_coding:
            return CodingResult(False, [], [], None, "Open coding engine not available")
        
        # 配置引擎
        if config:
            from CodeEngine.open_coding.agent import OpenCodingConfig
            open_coding.config = OpenCodingConfig(**config)
        
        # 批量编码
        result = open_coding.batch_code(segments)
        
        # 保存代码
        for code in result.get('approved_codes', []):
            entity = CodeEntity(
                id=code.id,
                label=code.code_label,
                definition=code.code_definition,
                level="open",
                created_by=code.created_by.value
            )
            self.code_repo.save(entity)
        
        return CodingResult(
            success=True,
            codes=result.get('approved_codes', []),
            categories=[],
            core_category=None,
            message=f"Generated {len(result.get('approved_codes', []))} codes"
        )
    
    def run_axial_coding(self, codes: List[CodeUnit]) -> CodingResult:
        """运行轴心编码"""
        axial_coding = self.engines.get('axial_coding')
        if not axial_coding:
            return CodingResult(False, codes, [], None, "Axial coding engine not available")
        
        categories = axial_coding.categorize_codes(codes)
        
        # 保存类属
        for cat in categories:
            from repositories.category_repository import CategoryEntity
            entity = CategoryEntity(
                id=cat.id,
                name=cat.name,
                definition=cat.definition
            )
            self.category_repo.save(entity)
        
        return CodingResult(
            success=True,
            codes=codes,
            categories=categories,
            core_category=None,
            message=f"Generated {len(categories)} categories"
        )
    
    def run_selective_coding(self, categories: List[Any]) -> CodingResult:
        """运行选择性编码"""
        selective_coding = self.engines.get('selective_coding')
        if not selective_coding:
            return CodingResult(False, [], categories, None, "Selective coding engine not available")
        
        core_category = selective_coding.identify_core_category(categories)
        
        return CodingResult(
            success=True,
            codes=[],
            categories=categories,
            core_category=core_category,
            message=f"Core category: {core_category.name if core_category else 'None'}"
        )
    
    def run_full_pipeline(
        self,
        segments: List[TextSegment],
        config: Optional[Dict] = None
    ) -> CodingResult:
        """运行完整编码工作流"""
        # Step 1: 开放编码
        result1 = self.run_open_coding(segments, config)
        if not result1.success:
            return result1
        
        # Step 2: 轴心编码
        result2 = self.run_axial_coding(result1.codes)
        if not result2.success:
            return CodingResult(
                success=True,
                codes=result1.codes,
                categories=[],
                core_category=None,
                message="Open coding done, axial coding failed"
            )
        
        # Step 3: 选择性编码
        result3 = self.run_selective_coding(result2.categories)
        
        return CodingResult(
            success=True,
            codes=result1.codes,
            categories=result2.categories,
            core_category=result3.core_category,
            message="Full pipeline completed"
        )
    
    def get_coding_status(self) -> Dict[str, Any]:
        """获取当前编码状态"""
        codes = self.code_repo.list()
        categories = self.category_repo.list()
        
        return {
            "total_codes": len(codes),
            "total_categories": len(categories),
            "open_codes": len([c for c in codes if c.level == "open"]),
            "axial_codes": len([c for c in codes if c.level == "axial"])
        }
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/services/test_coding_service.py -v
```

- [ ] **Step 4: Commit**

```bash
git add services/ tests/services/
git commit -m "feat: add coding service layer"
```

---

### Task 6: 创建 Import Service

**Files:**
- Create: `services/import_service.py`
- Create: `tests/services/test_import_service.py`

- [ ] **Step 1: 实现 Import Service**

```python
# services/import_service.py
from typing import List, Optional
from pathlib import Path
from CodeEngine.ir.code_ir import TextSegment

class ImportService:
    """导入服务 - 封装导入逻辑"""
    
    def __init__(self, import_engine, session_repo):
        self.import_engine = import_engine
        self.session_repo = session_repo
    
    def import_file(
        self,
        file_path: str,
        segment_type: str = "paragraph",
        anonymize: bool = True
    ) -> List[TextSegment]:
        """导入文件并返回文本片段"""
        from ImportEngine.agent import ImportConfig
        
        config = ImportConfig(anonymize=anonymize)
        self.import_engine.config = config
        
        segments = self.import_engine.import_file(file_path, segment_type)
        
        # 保存到会话
        self._save_to_session(segments, file_path)
        
        return segments
    
    def _save_to_session(self, segments: List[TextSegment], source_file: str):
        """保存导入结果到会话"""
        from repositories.session_repository import SessionEntity
        
        session = self.session_repo.get("default")
        if not session:
            session = SessionEntity(id="default")
        
        session.data['segments'] = [
            {
                'id': s.id,
                'content': s.content,
                'source': s.source,
                'position': s.position
            }
            for s in segments
        ]
        session.data['source_file'] = source_file
        
        self.session_repo.save(session)
```

- [ ] **Step 2: 编写测试**

```python
# tests/services/test_import_service.py
import pytest
from unittest.mock import Mock, MagicMock
from services.import_service import ImportService

@pytest.fixture
def service():
    import_engine = Mock()
    session_repo = Mock()
    return ImportService(import_engine, session_repo)

def test_import_file(service):
    from CodeEngine.ir.code_ir import TextSegment
    
    # Mock
    mock_segments = [
        TextSegment(id="s1", content="文本1", source="t.txt", position=(0, 3))
    ]
    service.import_engine.import_file.return_value = mock_segments
    
    # 执行
    result = service.import_file("test.txt", segment_type="paragraph")
    
    # 验证
    assert len(result) == 1
    service.import_engine.import_file.assert_called_once()
```

- [ ] **Step 3: Commit**

```bash
git add services/import_service.py tests/services/test_import_service.py
git commit -m "feat: add import service"
```

---

## Phase 3: 重构 CLI 层

### Task 7: 提取 CLI 命令到独立模块

**Files:**
- Create: `cli/__init__.py`
- Create: `cli/commands.py` (从 app.py 提取)
- Create: `cli/formatters.py`
- Create: `cli/dependencies.py`
- Modify: `app.py` (大幅简化)

- [ ] **Step 1: 创建 CLI 依赖注入模块**

```python
# cli/dependencies.py
"""CLI 依赖管理"""
from functools import lru_cache
from config import settings
from CodebookDB.db import CodebookDB
from repositories.code_repository import CodeRepository
from repositories.category_repository import CategoryRepository
from repositories.session_repository import SessionRepository
from ImportEngine.agent import ImportEngine
from CodeEngine.open_coding.agent import OpenCodingAgent
from CodeEngine.axial_coding.agent import AxialCodingAgent
from CodeEngine.selective_coding.agent import SelectiveCodingAgent
from MemoEngine.agent import MemoEngine
from ForumEngine.agent import ForumEngine
from ReportEngine.generator import ReportEngine
from TheoryEngine.visualizer import CodeNetworkVisualizer, SaturationChecker
from services.coding_service import CodingService
from services.import_service import ImportService

@lru_cache()
def get_db() -> CodebookDB:
    return CodebookDB()

@lru_cache()
def get_code_repository() -> CodeRepository:
    return CodeRepository(get_db())

@lru_cache()
def get_category_repository() -> CategoryRepository:
    return CategoryRepository(get_db())

@lru_cache()
def get_session_repository() -> SessionRepository:
    return SessionRepository(get_db())

def get_coding_service() -> CodingService:
    engines = {
        'open_coding': OpenCodingAgent(),
        'axial_coding': AxialCodingAgent(),
        'selective_coding': SelectiveCodingAgent()
    }
    return CodingService(
        code_repo=get_code_repository(),
        category_repo=get_category_repository(),
        session_repo=get_session_repository(),
        engines=engines
    )

def get_import_service() -> ImportService:
    return ImportService(
        import_engine=ImportEngine(),
        session_repo=get_session_repository()
    )
```

- [ ] **Step 2: 创建格式化模块**

```python
# cli/formatters.py
"""CLI 输出格式化"""
from typing import List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def print_segments_table(segments: List[Any], limit: int = 5):
    """打印文本片段表格"""
    table = Table(title=f"成功导入 {len(segments)} 个文本片段")
    table.add_column("ID", style="cyan", width=10)
    table.add_column("内容预览", style="green", width=50)
    table.add_column("来源", style="yellow")
    
    for seg in segments[:limit]:
        preview = seg.content[:60] + "..." if len(seg.content) > 60 else seg.content
        table.add_row(seg.id, preview, seg.source)
    
    if len(segments) > limit:
        table.add_row("...", f"还有 {len(segments) - limit} 个片段", "")
    
    console.print(table)

def print_codes_table(codes: List[Any], limit: int = 10):
    """打印代码表格"""
    table = Table(title=f"共 {len(codes)} 个代码")
    table.add_column("代码标签", style="cyan")
    table.add_column("定义", style="green")
    table.add_column("置信度", style="magenta")
    table.add_column("来源", style="yellow")
    
    for code in codes[:limit]:
        source = "AI" if hasattr(code, 'created_by') and code.created_by.value == "ai" else "人机协作"
        definition = code.code_definition if len(code.code_definition) <= 40 else code.code_definition[:40] + "..."
        table.add_row(
            code.code_label,
            definition,
            f"{code.confidence:.2f}",
            source
        )
    
    if len(codes) > limit:
        table.add_row("...", f"还有 {len(codes) - limit} 个代码", "", "")
    
    console.print(table)

def print_health_status(llm_status: dict, db_status: bool, session_info: dict):
    """打印健康状态"""
    from rich.table import Table
    
    console.print(Panel("[bold blue]系统健康检查[/bold blue]"))
    
    table = Table(title="LLM 服务状态")
    table.add_column("组件", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("详情", style="yellow")
    
    for provider, status in llm_status.get("providers", {}).items():
        avail = "✓ 可用" if status.get("available") else "✗ 不可用"
        detail = status.get("model", status.get("host", "-"))
        table.add_row(provider, avail, detail)
    
    console.print(table)
```

- [ ] **Step 3: 创建简化版 CLI 命令**

```python
# cli/commands.py
"""CLI 命令定义"""
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from cli.dependencies import (
    get_coding_service, get_import_service,
    get_code_repository, get_session_repository,
    get_db
)
from cli.formatters import print_segments_table, print_codes_table, print_health_status
from utils.llm_client import llm_client

app = typer.Typer(help="CoderResearch - 定性研究智能编码系统")
console = Console()

@app.command()
def health():
    """系统健康检查"""
    llm_status = llm_client.health_check()
    
    # 数据库检查
    db_ok = True
    try:
        db = get_db()
        codes = db.list_codes()
        db_count = len(codes)
    except Exception as e:
        db_ok = False
        db_count = 0
    
    # 会话检查
    session_repo = get_session_repository()
    session = session_repo.get("default")
    session_info = {
        "has_data": session is not None,
        "segments": len(session.data.get('segments', [])) if session else 0,
        "codes": len(session.data.get('open_codes', [])) if session else 0
    }
    
    print_health_status(llm_status, db_ok, session_info)
    
    if db_ok:
        rprint(f"\n[green]✓[/green] 数据库连接正常 (SQLite)")
        rprint(f"   当前代码本包含 {db_count} 个代码")
    else:
        rprint(f"\n[red]✗[/red] 数据库连接失败")

@app.command()
def import_data(
    file_path: str = typer.Argument(..., help="数据文件路径(.txt/.md)"),
    segment_type: str = typer.Option("paragraph", help="分段方式: paragraph/turn"),
    anonymize: bool = typer.Option(True, help="是否去标识化")
):
    """导入研究数据"""
    service = get_import_service()
    segments = service.import_file(file_path, segment_type, anonymize)
    print_segments_table(segments)
    rprint(f"[green]✓[/green] 数据已导入并保存")

@app.command()
def open_code(
    ai_assist: bool = typer.Option(True, help="是否启用 AI 辅助编码"),
    coding_style: str = typer.Option("descriptive", help="编码风格: descriptive/in_vivo/process"),
    require_review: bool = typer.Option(True, help="是否需要人工审核"),
    auto_approve: bool = typer.Option(False, help="高置信度自动通过")
):
    """开放编码 - 生成初始代码"""
    from CodeEngine.ir.code_ir import TextSegment
    
    # 获取会话数据
    session_repo = get_session_repository()
    session = session_repo.get("default")
    
    if not session or not session.data.get('segments'):
        rprint("[red]请先运行 import-data 导入数据[/red]")
        return
    
    segments = [
        TextSegment(**s) for s in session.data['segments']
    ]
    
    service = get_coding_service()
    config = {
        'allow_ai_suggestion': ai_assist,
        'coding_style': coding_style,
        'require_human_review': require_review,
        'auto_approve_high_confidence': auto_approve
    }
    
    rprint(f"对 {len(segments)} 个文本片段进行开放编码...")
    result = service.run_open_coding(segments, config)
    
    if result.success:
        print_codes_table(result.codes)
        rprint(f"[green]✓[/green] 已生成 {len(result.codes)} 个代码")
    else:
        rprint(f"[red]✗[/red] {result.message}")

@app.command()
def list_codes():
    """查看代码本"""
    repo = get_code_repository()
    codes = repo.list()
    
    if not codes:
        rprint("[yellow]暂无代码[/yellow]")
        return
    
    table = Table(title=f"共 {len(codes)} 个代码")
    table.add_column("ID", style="dim", width=8)
    table.add_column("代码标签", style="cyan")
    table.add_column("定义", style="green")
    table.add_column("层级", style="yellow", width=10)
    
    for code in codes[:20]:
        definition = code.definition[:40] + "..." if len(code.definition) > 40 else code.definition
        table.add_row(code.id, code.label, definition, code.level)
    
    console.print(table)

# 保留其他命令的简化版本...
@app.command()
def version():
    """显示版本信息"""
    rprint(Panel("""
[bold cyan]CoderResearch[/bold cyan] v2.0.0
定性研究智能编码系统（重构版）

基于分层架构：CLI → Service → Engine → Repository
    """, title="关于"))
```

- [ ] **Step 4: 简化 app.py**

```python
# app.py
"""
CoderResearch 主应用入口
重构版：分层架构（CLI → Service → Engine → Repository）
"""
from cli.commands import app

if __name__ == "__main__":
    app()
```

- [ ] **Step 5: 运行测试确保无破坏**

```bash
pytest tests/ -v --tb=short
```
Expected: 49+ tests pass（原有测试 + 新增 repository/service 测试）

- [ ] **Step 6: Commit**

```bash
git add cli/ app.py
git commit -m "refactor: extract CLI layer with dependency injection"
```

---

## Phase 4: 迁移与清理

### Task 8: 迁移旧代码并添加兼容性层

**Files:**
- Create: `compatibility.py`（向后兼容层）
- Modify: `utils/session_manager.py`（可选，使用新 repository）

- [ ] **Step 1: 创建兼容性层**

```python
# compatibility.py
"""向后兼容层 - 保持旧代码可用"""
import warnings

# 保留旧的全局实例（用于向后兼容）
def get_legacy_import_engine():
    warnings.warn(
        "直接访问全局引擎已废弃，请使用 services/",
        DeprecationWarning,
        stacklevel=2
    )
    from ImportEngine.agent import ImportEngine
    return ImportEngine()

def get_legacy_open_coding_agent():
    warnings.warn(
        "直接访问全局 Agent 已废弃，请使用 services/",
        DeprecationWarning,
        stacklevel=2
    )
    from CodeEngine.open_coding.agent import OpenCodingAgent
    return OpenCodingAgent()
```

- [ ] **Step 2: Commit**

```bash
git add compatibility.py
git commit -m "feat: add backward compatibility layer"
```

---

## Phase 5: 验证与文档

### Task 9: 运行完整测试套件

- [ ] **Step 1: 运行所有测试**

```bash
pytest tests/ -v --tb=short
```
Expected: 全部通过（原有 49 + 新增 repository/service 测试）

- [ ] **Step 2: 手动测试关键路径**

```bash
# 测试健康检查
python app.py health

# 测试导入
python app.py import-data test_interview.txt

# 测试列表
python app.py list-codes
```

- [ ] **Step 3: Commit 最终版本**

```bash
git add -A
git commit -m "refactor: complete layered architecture migration

- Add Repository layer (code, category, session)
- Add Service layer (coding, import)
- Extract CLI layer with dependency injection
- Maintain backward compatibility
- All tests passing"
```

---

## Summary

| 阶段 | 文件变更 | 测试要求 |
|------|----------|----------|
| Phase 1: Repository | 5 个新文件 + 3 个测试文件 | Repository 测试通过 |
| Phase 2: Service | 4 个新文件 + 2 个测试文件 | Service 测试通过 |
| Phase 3: CLI | 4 个新文件 + 大幅简化 app.py | 全部测试通过 |
| Phase 4: 兼容性 | 1 个新文件 | 无破坏 |
| Phase 5: 验证 | 文档更新 | 全部测试通过 |

**Total estimated tasks:** 9
**Estimated time:** 2-3 hours
