"""Repository pattern base classes."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Repository 模式基类"""
    
    @abstractmethod
    def get(self, id: str) -> Optional[T]: 
        ...
    
    @abstractmethod
    def list(self, **filters) -> List[T]: 
        ...
    
    @abstractmethod
    def save(self, entity: T) -> str: 
        ...
    
    @abstractmethod
    def delete(self, id: str) -> bool: 
        ...

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
