"""
MemoEngine - 备忘录撰写与反思
"""
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from utils.llm_client import llm_client


class MemoType(Enum):
    """备忘录类型"""
    CODE = "code_memo"           # 代码备忘录
    THEORETICAL = "theoretical_memo"  # 理论备忘录
    OPERATIONAL = "operational_memo"  # 操作备忘录
    REFLECTIVE = "reflective_memo"    # 反思备忘录


@dataclass
class Memo:
    """备忘录"""
    id: str
    type: MemoType
    title: str
    content: str
    related_codes: List[str] = field(default_factory=list)
    related_categories: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = "researcher"
    tags: List[str] = field(default_factory=list)


class MemoEngine:
    """备忘录引擎"""
    
    def __init__(self):
        self.memos: Dict[str, Memo] = {}
    
    def create_code_memo(self, code_label: str, code_definition: str,
                         text_examples: List[str]) -> Memo:
        """创建代码备忘录"""
        
        prompt = f"""为以下代码撰写详细的代码备忘录（Code Memo）：

代码标签：{code_label}
初始定义：{code_definition}

文本示例：
{chr(10).join([f"- {ex[:100]}..." for ex in text_examples[:3]])}

备忘录应包含：
1. 代码的详细定义和边界
2. 包含/不包含什么情况
3. 与其他代码的区分
4. 典型示例和边缘案例

直接返回备忘录正文内容。
"""
        
        content = llm_client.chat([
            {"role": "system", "content": "你是一位质性研究专家。"},
            {"role": "user", "content": prompt}
        ])
        
        memo = Memo(
            id=str(uuid.uuid4())[:8],
            type=MemoType.CODE,
            title=f"代码备忘录: {code_label}",
            content=content,
            related_codes=[code_label]
        )
        
        self.memos[memo.id] = memo
        return memo
    
    def create_theoretical_memo(self, category_name: str, 
                                related_codes: List[str],
                                relationships: str) -> Memo:
        """创建理论备忘录"""
        
        prompt = f"""为以下类属撰写理论备忘录（Theoretical Memo）：

类属名称：{category_name}
相关代码：{', '.join(related_codes)}
关系描述：{relationships}

备忘录应包含：
1. 概念的理论意义
2. 与现有文献的对话
3. 可能的理论贡献
4. 需要进一步探索的问题

直接返回备忘录正文内容。
"""
        
        content = llm_client.chat([
            {"role": "system", "content": "你是一位质性研究理论家。"},
            {"role": "user", "content": prompt}
        ])
        
        memo = Memo(
            id=str(uuid.uuid4())[:8],
            type=MemoType.THEORETICAL,
            title=f"理论备忘录: {category_name}",
            content=content,
            related_categories=[category_name]
        )
        
        self.memos[memo.id] = memo
        return memo
    
    def create_reflective_memo(self, stage: str, reflections: str) -> Memo:
        """创建反思备忘录"""
        
        memo = Memo(
            id=str(uuid.uuid4())[:8],
            type=MemoType.REFLECTIVE,
            title=f"反思备忘录: {stage}",
            content=reflections,
            tags=["reflection", stage]
        )
        
        self.memos[memo.id] = memo
        return memo
    
    def auto_draft_memo(self, memo_type: MemoType, context: Dict) -> Memo:
        """自动生成备忘录草稿"""
        
        if memo_type == MemoType.CODE:
            return self.create_code_memo(
                context.get("code_label", ""),
                context.get("code_definition", ""),
                context.get("examples", [])
            )
        elif memo_type == MemoType.THEORETICAL:
            return self.create_theoretical_memo(
                context.get("category_name", ""),
                context.get("related_codes", []),
                context.get("relationships", "")
            )
        else:
            return self.create_reflective_memo(
                context.get("stage", "general"),
                context.get("reflections", "")
            )
    
    def get_memo(self, memo_id: str) -> Optional[Memo]:
        """获取备忘录"""
        return self.memos.get(memo_id)
    
    def list_memos(self, memo_type: Optional[MemoType] = None) -> List[Memo]:
        """列出自备忘录"""
        if memo_type:
            return [m for m in self.memos.values() if m.type == memo_type]
        return list(self.memos.values())
    
    def link_memo_to_code(self, memo_id: str, code_id: str):
        """将备忘录链接到代码"""
        if memo_id in self.memos:
            if code_id not in self.memos[memo_id].related_codes:
                self.memos[memo_id].related_codes.append(code_id)
    
    def export_memos(self, output_path: str):
        """导出所有备忘录"""
        import json
        
        data = []
        for memo in self.memos.values():
            data.append({
                "id": memo.id,
                "type": memo.type.value,
                "title": memo.title,
                "content": memo.content,
                "related_codes": memo.related_codes,
                "created_at": memo.created_at.isoformat()
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
