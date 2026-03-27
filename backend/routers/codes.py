"""Codes API router."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid

from database import get_db
from models import Code, CodeCreate

router = APIRouter()


@router.get("", response_model=List[Code])
async def list_codes(
    level: Optional[str] = Query(None, description="Filter by level: open, axial, selective")
):
    """获取所有代码"""
    conn = await get_db()
    
    if level:
        cursor = await conn.execute(
            "SELECT * FROM codes WHERE level = ? ORDER BY created_at DESC",
            (level,)
        )
    else:
        cursor = await conn.execute("SELECT * FROM codes ORDER BY created_at DESC")
    
    rows = await cursor.fetchall()
    return [Code(**dict(row)) for row in rows]


@router.get("/{code_id}", response_model=Code)
async def get_code(code_id: str):
    """获取单个代码"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM codes WHERE id = ?", (code_id,))
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Code not found")
    
    return Code(**dict(row))


@router.post("", response_model=Code)
async def create_code(code: CodeCreate):
    """创建新代码"""
    conn = await get_db()
    code_id = code.id or str(uuid.uuid4())[:8]
    
    await conn.execute(
        """
        INSERT INTO codes (id, label, definition, level, category_id, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (code_id, code.label, code.definition, code.level, code.category_id, code.created_by)
    )
    await conn.commit()
    
    return await get_code(code_id)


@router.put("/{code_id}", response_model=Code)
async def update_code(code_id: str, code: CodeCreate):
    """更新代码"""
    conn = await get_db()
    
    # Check exists
    cursor = await conn.execute("SELECT id FROM codes WHERE id = ?", (code_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Code not found")
    
    await conn.execute(
        """
        UPDATE codes 
        SET label = ?, definition = ?, level = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (code.label, code.definition, code.level, code.category_id, code_id)
    )
    await conn.commit()
    
    return await get_code(code_id)


@router.delete("/{code_id}")
async def delete_code(code_id: str):
    """删除代码"""
    conn = await get_db()
    
    cursor = await conn.execute("SELECT id FROM codes WHERE id = ?", (code_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Code not found")
    
    await conn.execute("DELETE FROM codes WHERE id = ?", (code_id,))
    await conn.commit()
    
    return {"message": "Code deleted", "id": code_id}
