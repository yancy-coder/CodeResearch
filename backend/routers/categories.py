"""Categories API router."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import uuid
import json

from database import get_db
from models import Category, CategoryCreate

router = APIRouter()


@router.get("", response_model=List[Category])
async def list_categories(parent_id: Optional[str] = None):
    """获取所有类属"""
    conn = await get_db()
    
    if parent_id is not None:
        cursor = await conn.execute(
            "SELECT * FROM categories WHERE parent_id = ?",
            (parent_id,)
        )
    else:
        cursor = await conn.execute("SELECT * FROM categories")
    
    rows = await cursor.fetchall()
    categories = []
    for row in rows:
        data = dict(row)
        data['properties'] = json.loads(data.get('properties', '[]'))
        data['dimensions'] = json.loads(data.get('dimensions', '{}'))
        categories.append(Category(**data))
    
    return categories


@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: str):
    """获取单个类属"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    
    data = dict(row)
    data['properties'] = json.loads(data.get('properties', '[]'))
    data['dimensions'] = json.loads(data.get('dimensions', '{}'))
    return Category(**data)


@router.post("", response_model=Category)
async def create_category(category: CategoryCreate):
    """创建类属"""
    conn = await get_db()
    cat_id = str(uuid.uuid4())[:8]
    
    await conn.execute(
        """
        INSERT INTO categories (id, name, definition, parent_id, properties, dimensions)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (cat_id, category.name, category.definition, category.parent_id, '[]', '{}')
    )
    await conn.commit()
    
    return Category(id=cat_id, **category.model_dump())
