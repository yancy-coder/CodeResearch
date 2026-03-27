"""Sessions API router."""
from fastapi import APIRouter, HTTPException
import json

from database import get_db
from models import Session

router = APIRouter()


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str = "default"):
    """获取会话"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = await cursor.fetchone()
    
    if not row:
        # Create default session
        await conn.execute(
            "INSERT INTO sessions (id, data) VALUES (?, ?)",
            (session_id, '{}')
        )
        await conn.commit()
        return Session(id=session_id, data={}, created_at=None, updated_at=None)
    
    data = dict(row)
    data['data'] = json.loads(data.get('data', '{}'))
    return Session(**data)


@router.put("/{session_id}")
async def update_session(session_id: str, data: dict):
    """更新会话"""
    conn = await get_db()
    
    await conn.execute(
        """
        INSERT INTO sessions (id, data, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET 
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
        """,
        (session_id, json.dumps(data))
    )
    await conn.commit()
    
    return {"message": "Session updated", "id": session_id}
