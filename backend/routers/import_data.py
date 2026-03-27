"""Import API router with PDF and DOCX support - Optimized for interview transcripts."""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import uuid
import io
import re

from database import get_db
from models import TextSegment

router = APIRouter()

# 常见转录文本的说话人模式（按优先级排序）
SPEAKER_PATTERNS = [
    # 1. [时间戳] 说话人： 或 [时间戳]说话人：
    r'^\[\d{1,2}:\d{2}(?::\d{2})?\]\s*(主持人|受访者|访谈者|被访者|记者|专家|Speaker|Interviewee|Interviewer|Participant)\s*\d*\s*[：:]\s*',
    # 2. [时间戳] （纯时间戳）
    r'^\[\d{1,2}:\d{2}(?::\d{2})?\]\s*[：:]?\s*',
    # 3. 说话人： （纯角色名）
    r'^(主持人|受访者|访谈者|被访者|记者|专家|Speaker|Interviewee|Interviewer|Participant)\s*\d*\s*[：:]\s*',
    # 4. 时间数字： （如 00:01:23：）
    r'^\d{1,2}:\d{2}(?::\d{2})?\s*[：:]\s*',
]


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


def detect_speaker(text: str) -> Optional[str]:
    """检测文本是否包含说话人标识，返回识别到的说话人。"""
    for pattern in SPEAKER_PATTERNS:
        match = re.match(pattern, text.strip())
        if match:
            speaker = match.group(0).rstrip('：: ')
            return speaker
    return None


def parse_speaker_turn(text: str) -> tuple[Optional[str], str]:
    """解析文本，返回 (说话人, 内容)。"""
    for pattern in SPEAKER_PATTERNS:
        match = re.match(pattern, text.strip())
        if match:
            speaker = match.group(0).rstrip('：: ')
            content = text[match.end():].strip()
            return speaker, content
    return None, text.strip()


def split_transcript_by_turns(text: str) -> List[dict]:
    """按对话轮次分割转录文本，保留说话人信息。"""
    lines = text.split('\n')
    turns = []
    current_speaker = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        speaker, content = parse_speaker_turn(line)
        
        if speaker:
            # 保存前一个说话人的内容
            if current_speaker and current_content:
                turns.append({
                    'speaker': current_speaker,
                    'content': ' '.join(current_content),
                    'type': 'speech'
                })
            current_speaker = speaker
            current_content = [content]
        else:
            # 续上一句话
            current_content.append(line)
    
    # 保存最后一个说话人的内容
    if current_speaker and current_content:
        turns.append({
            'speaker': current_speaker,
            'content': ' '.join(current_content),
            'type': 'speech'
        })
    
    return turns


def split_transcript_by_qa(text: str) -> List[dict]:
    """按问答对分割（主持人问 -> 受访者答 作为一个片段）。"""
    turns = split_transcript_by_turns(text)
    segments = []
    current_qa = []
    
    for turn in turns:
        speaker = turn['speaker']
        # 判断是否是提问者（主持人/访谈者/记者）
        is_questioner = any(kw in speaker for kw in ['主持', '访谈', '记者', 'Interviewer', 'Question', '主持人'])
        
        if is_questioner and current_qa:
            # 保存上一组问答
            qa_text = '\n'.join([f"{t['speaker']}：{t['content']}" for t in current_qa])
            segments.append({
                'content': qa_text,
                'speaker': current_qa[0]['speaker'] if current_qa else None,
                'type': 'qa_pair'
            })
            current_qa = [turn]
        else:
            current_qa.append(turn)
    
    # 保存最后一组
    if current_qa:
        qa_text = '\n'.join([f"{t['speaker']}：{t['content']}" for t in current_qa])
        segments.append({
            'content': qa_text,
            'speaker': current_qa[0]['speaker'] if current_qa else None,
            'type': 'qa_pair'
        })
    
    return segments


@router.post("/file")
async def import_file(
    file: UploadFile = File(...),
    segment_type: str = Form(default="paragraph")
):
    """
    导入文件（支持 TXT, MD, PDF, DOC, DOCX）
    
    Args:
        segment_type: 分割方式
            - paragraph: 按段落分割（默认）
            - line: 按行分割
            - turn: 按说话人轮次分割（适合转录文本）
            - qa: 按问答对分割（适合访谈）
    """
    print(f"[DEBUG] Received segment_type: {segment_type}")
    
    # Read file content
    content = await file.read()
    
    # Determine file type and extract text
    ext = get_file_extension(file.filename)
    
    if ext in ['txt', 'md', 'markdown']:
        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-16']:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise HTTPException(status_code=400, detail="无法识别文件编码，请使用 UTF-8 或 GBK 编码")
    elif ext == 'pdf':
        text = extract_text_from_pdf(content)
    elif ext in ['doc', 'docx']:
        text = extract_text_from_docx(content)
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式: .{ext}。支持: txt, md, pdf, doc, docx"
        )
    
    # 根据 segment_type 解析片段
    if segment_type == "turn":
        # 按说话人轮次分割
        parsed_turns = split_transcript_by_turns(text)
        raw_segments = [
            f"[{t['speaker']}] {t['content']}" if t['speaker'] else t['content']
            for t in parsed_turns
        ]
    elif segment_type == "qa":
        # 按问答对分割
        parsed_qas = split_transcript_by_qa(text)
        raw_segments = [qa['content'] for qa in parsed_qas]
    elif segment_type == "line":
        raw_segments = [s.strip() for s in text.split('\n') if s.strip()]
    else:  # paragraph
        raw_segments = [s.strip() for s in text.split('\n\n') if s.strip()]
    
    # 创建 TextSegment 对象
    segments: List[TextSegment] = []
    position = 0
    
    for seg_text in raw_segments[:100]:  # Limit to 100 segments
        seg_id = f"seg-{uuid.uuid4().hex[:6]}"
        segments.append(TextSegment(
            id=seg_id,
            content=seg_text[:2000],  # 转录文本可能较长，放宽限制
            source=file.filename,
            position=(position, position + len(seg_text))
        ))
        position += len(seg_text) + 2
    
    # 统计说话人信息
    speaker_count = {}
    if segment_type in ["turn", "qa"]:
        for seg in segments:
            speaker_match = re.match(r'\[([^\]]+)\]', seg.content)
            if speaker_match:
                speaker = speaker_match.group(1)
                speaker_count[speaker] = speaker_count.get(speaker, 0) + 1
    
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
    
    result = {
        "message": f"成功导入 {len(segments)} 个文本片段",
        "count": len(segments),
        "file_type": ext,
        "segment_type": segment_type,
        "segments": [s.model_dump() for s in segments]
    }
    
    if speaker_count:
        result["speakers"] = speaker_count
    
    return result


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
