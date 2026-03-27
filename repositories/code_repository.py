"""Code repository implementation."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from repositories.base import Repository
from CodebookDB.db import CodebookDB


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
            "created_by": entity.created_by,
            "category_id": entity.category_id,
            "version": entity.version
        }
        return self.db.save_code(data)
    
    def delete(self, id: str) -> bool:
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
        def parse_datetime(val):
            if isinstance(val, str):
                return datetime.fromisoformat(val)
            return val or datetime.now()
        
        return CodeEntity(
            id=data["id"],
            label=data["label"],
            definition=data.get("definition", ""),
            level=data.get("level", "open"),
            category_id=data.get("category_id"),
            created_by=data.get("created_by", "human"),
            created_at=parse_datetime(data.get("created_at")),
            updated_at=parse_datetime(data.get("updated_at")),
            version=data.get("version", "1.0")
        )
