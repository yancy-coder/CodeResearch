"""Import API router."""
from fastapi import APIRouter, UploadFile, File
from typing import List
import uuid

from database import get_db
from models import TextSegment

router = APIRouter()


@router.post("/text")
async def import_text(
    file: UploadFile = File(...),
    segment_type: str = "paragraph"
):
    """导入文本文件"""
    content = await file.read()
    text = content.decode('utf-8')
    
    # Parse segments
    if segment_type == "paragraph":
        raw_segments = [s.strip() for s in text.split('\n\n') if s.strip()]
    else:
        raw_segments = [s.strip() for s in text.split('\n') if s.strip()]
    
    segments: List[TextSegment] = []
    position = 0
    
    for seg_text in raw_segments[:100]:  # Limit to 100 segments
        seg_id = f"seg-{uuid.uuid4().hex[:6]}"
        segments.append(TextSegment(
            id=seg_id,
            content=seg_text[:1000],  # Limit length
            source=file.filename,
            position=(position, position + len(seg_text))
        ))
        position += len(seg_text) + 2
    
    # Save to database
    conn = await get_db()
    for seg in segments:
        await conn.execute(
            """
            INSERT INTO segments (id, content, source, position_start, position_end)
            VALUES (?, ?, ?, ?, ?)
            """,
            (seg.id, seg.content, seg.source, seg.position[0], seg.position[1])
        )
    await conn.commit()
    
    return {
        "message": f"Imported {len(segments)} segments",
        "count": len(segments),
        "segments": [s.model_dump() for s in segments]
    }


@router.get("/segments")
async def list_segments():
    """获取所有文本片段"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM segments ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    
    segments = []
    for row in rows:
        data = dict(row)
        segments.append(TextSegment(
            id=data['id'],
            content=data['content'],
            source=data['source'],
            position=(data['position_start'], data['position_end'])
        ))
    
    return segments


@router.delete("/segments")
async def clear_segments():
    """清空所有文本片段"""
    conn = await get_db()
    await conn.execute("DELETE FROM segments")
    await conn.commit()
    return {"message": "All segments cleared"}
