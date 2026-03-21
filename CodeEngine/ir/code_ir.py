"""
编码单元 IR（Intermediate Representation）
核心数据结构定义
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum


class CodeSource(Enum):
    """编码来源"""
    HUMAN = "human"
    AI = "ai"
    COLLABORATION = "collaboration"


class CodingLevel(Enum):
    """编码层级"""
    OPEN = "open_coding"
    AXIAL = "axial_coding"
    SELECTIVE = "selective_coding"


@dataclass
class TextSegment:
    """文本片段"""
    id: str
    content: str
    source: str                    # 数据来源（受访者ID/文档名）
    position: Tuple[int, int]      # 在原文中的位置 (start, end)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CodeUnit:
    """代码单元"""
    id: str
    text_segment: TextSegment
    code_label: str                # 代码标签
    code_definition: str           # 代码定义/说明
    memo_id: Optional[str] = None
    created_by: CodeSource = CodeSource.HUMAN
    confidence: float = 1.0        # 编码置信度
    created_at: datetime = field(default_factory=datetime.now)
    
    # 轴心编码扩展
    category: Optional[str] = None
    properties: List[str] = field(default_factory=list)
    dimensions: Dict[str, str] = field(default_factory=dict)


@dataclass
class Category:
    """类属（轴心编码产物）"""
    id: str
    name: str
    definition: str
    codes: List[str] = field(default_factory=list)  # 包含的代码ID
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    """代码/类属间关系"""
    id: str
    source_id: str
    target_id: str
    relation_type: str           # 因果、条件、过程、属性等
    description: str = ""
    evidence: List[str] = field(default_factory=list)


@dataclass
class CodebookVersion:
    """代码本版本"""
    version_id: str
    timestamp: datetime
    changes: List[Dict]          # 变更记录
    author: str
    message: str                 # 版本说明
