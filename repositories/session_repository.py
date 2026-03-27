"""Session repository implementation."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from repositories.base import Repository
from CodebookDB.db import CodebookDB


@dataclass
class SessionEntity:
    """会话实体"""
    id: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SessionRepository(Repository[SessionEntity]):
    """会话 Repository"""
    
    def __init__(self, db: CodebookDB):
        self.db = db
    
    def get(self, id: str = "default") -> Optional[SessionEntity]:
        """获取会话实体"""
        from CodebookDB.db import SessionModel
        session = self.db.Session()
        try:
            record = session.query(SessionModel).filter_by(id=id).first()
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
    
    def list(self, **filters) -> list:
        """列出所有会话"""
        from CodebookDB.db import SessionModel
        session = self.db.Session()
        try:
            records = session.query(SessionModel).all()
            return [
                SessionEntity(
                    id=r.id,
                    data=r.data or {},
                    created_at=r.created_at,
                    updated_at=r.updated_at
                )
                for r in records
            ]
        finally:
            session.close()
    
    def save(self, entity: SessionEntity) -> str:
        """保存会话实体"""
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
    
    def delete(self, id: str) -> bool:
        """删除会话"""
        from CodebookDB.db import SessionModel
        session = self.db.Session()
        try:
            record = session.query(SessionModel).filter_by(id=id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        finally:
            session.close()
