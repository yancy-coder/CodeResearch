"""
CodebookDB - 代码本数据库与版本控制
"""
from sqlalchemy import create_engine, Column, String, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
from typing import List, Dict, Optional

from config import settings

Base = declarative_base()


class CodeModel(Base):
    """代码数据库模型"""
    __tablename__ = "codes"
    
    id = Column(String, primary_key=True)
    label = Column(String, nullable=False, index=True)
    definition = Column(Text)
    level = Column(String, default="open")  # open/axial/selective
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String, default="human")  # human/ai/collaboration
    version = Column(String, default="1.0")
    
    # 关系
    category = relationship("CategoryModel", back_populates="codes")
    occurrences = relationship("CodeOccurrenceModel", back_populates="code")


class CategoryModel(Base):
    """类属数据库模型"""
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    definition = Column(Text)
    parent_id = Column(String, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    properties = Column(JSON, default=list)  # 属性列表
    dimensions = Column(JSON, default=dict)  # 维度信息
    
    # 关系
    codes = relationship("CodeModel", back_populates="category")
    children = relationship("CategoryModel", backref="parent", remote_side=[id])


class CodeOccurrenceModel(Base):
    """代码出现位置记录"""
    __tablename__ = "code_occurrences"
    
    id = Column(String, primary_key=True)
    code_id = Column(String, ForeignKey("codes.id"), nullable=False)
    source = Column(String, nullable=False)  # 数据来源
    segment_content = Column(Text)           # 文本片段内容
    position_start = Column(Float)
    position_end = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    memo_id = Column(String, nullable=True)
    
    # 关系
    code = relationship("CodeModel", back_populates="occurrences")


class VersionHistoryModel(Base):
    """版本历史记录"""
    __tablename__ = "version_history"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    entity_type = Column(String)  # code/category/relationship
    entity_id = Column(String)
    action = Column(String)       # create/update/merge/split/delete
    changes = Column(JSON)        # 变更详情
    author = Column(String)
    message = Column(Text)


class CodebookDB:
    """代码本数据库管理类"""
    
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or settings.database_url
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_code(self, code_data: Dict, author: str = "system") -> str:
        """保存代码到数据库"""
        session = self.Session()
        try:
            code = CodeModel(
                id=code_data["id"],
                label=code_data["label"],
                definition=code_data.get("definition", ""),
                level=code_data.get("level", "open"),
                created_by=code_data.get("created_by", "human")
            )
            session.add(code)
            
            # 记录版本历史
            history = VersionHistoryModel(
                id=str(datetime.now().timestamp()),
                entity_type="code",
                entity_id=code_data["id"],
                action="create",
                changes=code_data,
                author=author,
                message=f"创建代码: {code_data['label']}"
            )
            session.add(history)
            
            session.commit()
            return code.id
        finally:
            session.close()
    
    def get_code(self, code_id: str) -> Optional[Dict]:
        """获取代码详情"""
        session = self.Session()
        try:
            code = session.query(CodeModel).filter_by(id=code_id).first()
            if code:
                return {
                    "id": code.id,
                    "label": code.label,
                    "definition": code.definition,
                    "level": code.level,
                    "created_by": code.created_by,
                    "created_at": code.created_at.isoformat() if code.created_at else None
                }
            return None
        finally:
            session.close()
    
    def list_codes(self, level: Optional[str] = None) -> List[Dict]:
        """列出所有代码"""
        session = self.Session()
        try:
            query = session.query(CodeModel)
            if level:
                query = query.filter_by(level=level)
            
            codes = query.all()
            return [
                {
                    "id": c.id,
                    "label": c.label,
                    "definition": c.definition,
                    "level": c.level
                }
                for c in codes
            ]
        finally:
            session.close()
    
    def merge_codes(self, source_ids: List[str], target_label: str, author: str) -> str:
        """合并多个代码"""
        session = self.Session()
        try:
            # 创建新代码
            import uuid
            new_code = CodeModel(
                id=str(uuid.uuid4())[:8],
                label=target_label,
                definition=f"合并代码: {', '.join(source_ids)}",
                level="axial"
            )
            session.add(new_code)
            
            # 记录历史
            history = VersionHistoryModel(
                id=str(datetime.now().timestamp()),
                entity_type="code",
                entity_id=new_code.id,
                action="merge",
                changes={"sources": source_ids, "target": target_label},
                author=author,
                message=f"合并代码: {source_ids} -> {target_label}"
            )
            session.add(history)
            
            session.commit()
            return new_code.id
        finally:
            session.close()
    
    def get_code_evolution(self, code_id: str) -> List[Dict]:
        """获取代码演化历史"""
        session = self.Session()
        try:
            histories = session.query(VersionHistoryModel).filter_by(
                entity_id=code_id
            ).order_by(VersionHistoryModel.timestamp).all()
            
            return [
                {
                    "timestamp": h.timestamp.isoformat() if h.timestamp else None,
                    "action": h.action,
                    "changes": h.changes,
                    "author": h.author,
                    "message": h.message
                }
                for h in histories
            ]
        finally:
            session.close()
