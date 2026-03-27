"""Import API router with PDF and DOCX support."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
import io

from database import get_db
from models import TextSegment

router = APIRouter()


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOCX extraction failed: {str(e)}")


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return filename.split('.')[-1].lower() if '.' in filename else ''


@router.post("/file")
async def import_file(
    file: UploadFile = File(...),
    segment_type: str = "paragraph"
):
    """导入文件（支持 TXT, MD, PDF, DOC, DOCX）"""
    # Read file content
    content = await file.read()
    
    # Determine file type and extract text
    ext = get_file_extension(file.filename)
    
    if ext in ['txt', 'md', 'markdown']:
        text = content.decode('utf-8')
    elif ext == 'pdf':
        text = extract_text_from_pdf(content)
    elif ext in ['doc', 'docx']:
        text = extract_text_from_docx(content)
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format: .{ext}. Supported: txt, md, pdf, doc, docx"
        )
    
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
        "message": f"成功导入 {len(segments)} 个文本片段",
        "count": len(segments),
        "file_type": ext,
        "segments": [s.model_dump() for s in segments]
    }


# Keep old endpoint for backward compatibility
@router.post("/text")
async def import_text(
    file: UploadFile = File(...),
    segment_type: str = "paragraph"
):
    """导入文本文件（兼容旧版本）"""
    return await import_file(file, segment_type)


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
