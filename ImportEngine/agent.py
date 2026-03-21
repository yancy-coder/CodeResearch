"""
ImportEngine - 数据导入与预处理引擎
"""
import os
import re
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
import uuid

from CodeEngine.ir.code_ir import TextSegment


@dataclass
class ImportConfig:
    """导入配置"""
    anonymize: bool = True           # 是否去标识化
    segment_by: str = "paragraph"    # 分段方式: paragraph/turn/fixed
    min_segment_length: int = 50
    max_segment_length: int = 500


class TextCleaner:
    """文本清洗工具"""
    
    @staticmethod
    def remove_identifiers(text: str) -> str:
        """去除可能的身份信息"""
        # 手机号
        text = re.sub(r'1[3-9]\d{9}', '[PHONE]', text)
        # 邮箱
        text = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', text)
        # 身份证号
        text = re.sub(r'\d{17}[\dXx]', '[ID]', text)
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """规范化空白字符"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def remove_noise(text: str) -> str:
        """去除噪音（如转录中的语气词重复）"""
        # 重复语气词
        text = re.sub(r'(啊|呢|吧|嘛)\1+', r'\1', text)
        return text


class Segmenter:
    """文本分段器"""
    
    def __init__(self, config: ImportConfig):
        self.config = config
    
    def segment_by_paragraph(self, text: str, source: str) -> List[TextSegment]:
        """按段落分段"""
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        segments = []
        
        position = 0
        for para in paragraphs:
            if len(para) >= self.config.min_segment_length:
                seg = TextSegment(
                    id=str(uuid.uuid4())[:8],
                    content=para,
                    source=source,
                    position=(position, position + len(para))
                )
                segments.append(seg)
            position += len(para) + 1
        
        return segments
    
    def segment_by_turn(self, text: str, source: str) -> List[TextSegment]:
        """按对话轮次分段（适用于访谈）"""
        # 识别常见的对话标记
        patterns = [
            r'([访访]|[访者]|Q|问)\s*[:：]\s*(.+?)(?=([访访]|[受访者]|A|答)\s*[:：]|$)',
            r'(A|答|受访者)\s*[:：]\s*(.+?)(?=(Q|问|访)\s*[:：]|$)'
        ]
        
        segments = []
        position = 0
        
        # 简化实现：按换行+关键词分段
        lines = text.split('\n')
        current_speaker = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测说话人
            if re.match(r'^(访|问|Q|A|答|受访者)', line):
                if current_content:
                    content = ' '.join(current_content)
                    if len(content) >= self.config.min_segment_length:
                        seg = TextSegment(
                            id=str(uuid.uuid4())[:8],
                            content=content,
                            source=f"{source}_{current_speaker}",
                            position=(position, position + len(content)),
                            metadata={"speaker": current_speaker}
                        )
                        segments.append(seg)
                
                current_speaker = "interviewer" if line[0] in "访问Q" else "interviewee"
                current_content = [re.sub(r'^.+?[:：]\s*', '', line)]
            else:
                current_content.append(line)
            
            position += len(line) + 1
        
        return segments


class ImportEngine:
    """导入引擎主类"""
    
    def __init__(self, config: Optional[ImportConfig] = None):
        self.config = config or ImportConfig()
        self.cleaner = TextCleaner()
        self.segmenter = Segmenter(self.config)
    
    def import_text(self, text: str, source: str, segment_type: str = "paragraph") -> List[TextSegment]:
        """导入文本并分段"""
        # 1. 清洗
        if self.config.anonymize:
            text = self.cleaner.remove_identifiers(text)
        text = self.cleaner.normalize_whitespace(text)
        text = self.cleaner.remove_noise(text)
        
        # 2. 分段
        if segment_type == "turn":
            segments = self.segmenter.segment_by_turn(text, source)
        else:
            segments = self.segmenter.segment_by_paragraph(text, source)
        
        return segments
    
    def import_file(self, file_path: str, segment_type: str = "paragraph") -> List[TextSegment]:
        """从文件导入"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 根据扩展名选择读取方式
        suffix = path.suffix.lower()
        
        if suffix == '.txt':
            text = path.read_text(encoding='utf-8')
        elif suffix in ['.md', '.markdown']:
            text = path.read_text(encoding='utf-8')
            # 简单去除 markdown 标记
            text = re.sub(r'[#*_`\[\]]', '', text)
        elif suffix == '.docx':
            from docx import Document
            doc = Document(file_path)
            text = '\n'.join(para.text for para in doc.paragraphs if para.text.strip())
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
        
        return self.import_text(text, path.stem, segment_type)
