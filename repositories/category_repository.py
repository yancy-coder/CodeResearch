"""Category repository implementation."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from repositories.base import Repository
from CodebookDB.db import CodebookDB


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
            session.merge(cat)
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
        """获取子类属"""
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
