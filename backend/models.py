"""Pydantic models for API."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CodeBase(BaseModel):
    label: str
    definition: str = ""
    level: str = "open"
    category_id: Optional[str] = None


class CodeCreate(CodeBase):
    id: Optional[str] = None
    created_by: str = "human"


class Code(CodeBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: str
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    definition: str = ""
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    id: Optional[str] = None


class Category(CategoryBase):
    id: str
    properties: List[str] = []
    dimensions: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class TextSegment(BaseModel):
    id: str
    content: str
    source: str
    position: tuple[int, int]


class Session(BaseModel):
    id: str
    data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
