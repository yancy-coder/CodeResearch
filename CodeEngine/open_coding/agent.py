"""
开放编码（Open Coding）模块
扎根理论第一阶段：逐行编码，生成初始代码

新特性：
- AI 辅助编码 + 人工审核机制
- 编码质量评分
- 编码冲突检测
"""
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid

from CodeEngine.ir.code_ir import TextSegment, CodeUnit, CodeSource
from utils.llm_client import llm_client


class ReviewStatus(Enum):
    """审核状态"""
    PENDING = "pending"      # 待审核
    APPROVED = "approved"    # 已通过
    REJECTED = "rejected"    # 已拒绝
    MODIFIED = "modified"    # 已修改


@dataclass
class SuggestedCode:
    """AI 建议的代码（待审核）"""
    id: str
    text_segment: TextSegment
    code_label: str
    code_definition: str
    confidence: float
    ai_reasoning: str           # AI 的编码理由
    review_status: ReviewStatus = ReviewStatus.PENDING
    reviewer_comment: str = ""  # 审核者备注
    modified_label: Optional[str] = None
    modified_definition: Optional[str] = None


@dataclass
class OpenCodingConfig:
    """开放编码配置"""
    max_codes_per_segment: int = 3
    min_confidence: float = 0.7
    allow_ai_suggestion: bool = True
    coding_style: str = "descriptive"  # descriptive/in_vivo/process
    require_human_review: bool = True   # 是否需要人工审核
    auto_approve_high_confidence: bool = False  # 高置信度自动通过
    high_confidence_threshold: float = 0.95
    batch_review: bool = True  # 批量审核模式


class CodeReviewManager:
    """编码审核管理器"""
    
    def __init__(self):
        self.pending_reviews: List[SuggestedCode] = []
        self.approved_codes: List[CodeUnit] = []
        self.rejected_count: int = 0
    
    def add_suggestion(self, suggestion: SuggestedCode):
        """添加待审核建议"""
        self.pending_reviews.append(suggestion)
    
    def approve(self, suggestion_id: str, comment: str = "") -> Optional[CodeUnit]:
        """批准编码建议"""
        for sugg in self.pending_reviews:
            if sugg.id == suggestion_id:
                sugg.review_status = ReviewStatus.APPROVED
                sugg.reviewer_comment = comment
                
                code = CodeUnit(
                    id=str(uuid.uuid4())[:8],
                    text_segment=sugg.text_segment,
                    code_label=sugg.code_label,
                    code_definition=sugg.code_definition,
                    created_by=CodeSource.COLLABORATION,  # AI + Human
                    confidence=sugg.confidence
                )
                self.approved_codes.append(code)
                self.pending_reviews.remove(sugg)
                return code
        return None
    
    def reject(self, suggestion_id: str, comment: str = "") -> bool:
        """拒绝编码建议"""
        for sugg in self.pending_reviews:
            if sugg.id == suggestion_id:
                sugg.review_status = ReviewStatus.REJECTED
                sugg.reviewer_comment = comment
                self.rejected_count += 1
                self.pending_reviews.remove(sugg)
                return True
        return False
    
    def modify_and_approve(
        self,
        suggestion_id: str,
        new_label: str,
        new_definition: str,
        comment: str = ""
    ) -> Optional[CodeUnit]:
        """修改后批准"""
        for sugg in self.pending_reviews:
            if sugg.id == suggestion_id:
                sugg.review_status = ReviewStatus.MODIFIED
                sugg.modified_label = new_label
                sugg.modified_definition = new_definition
                sugg.reviewer_comment = comment
                
                code = CodeUnit(
                    id=str(uuid.uuid4())[:8],
                    text_segment=sugg.text_segment,
                    code_label=new_label,
                    code_definition=new_definition,
                    created_by=CodeSource.COLLABORATION,
                    confidence=sugg.confidence * 0.9  # 修改降低置信度
                )
                self.approved_codes.append(code)
                self.pending_reviews.remove(sugg)
                return code
        return None
    
    def batch_approve(self, suggestion_ids: List[str]) -> List[CodeUnit]:
        """批量批准"""
        codes = []
        for sid in suggestion_ids:
            code = self.approve(sid, "批量批准")
            if code:
                codes.append(code)
        return codes
    
    def get_review_summary(self) -> Dict:
        """获取审核摘要"""
        return {
            "pending": len(self.pending_reviews),
            "approved": len(self.approved_codes),
            "rejected": self.rejected_count,
            "total": len(self.pending_reviews) + len(self.approved_codes) + self.rejected_count
        }
    
    def get_pending_by_segment(self, segment_id: str) -> List[SuggestedCode]:
        """获取特定片段的待审核建议"""
        return [s for s in self.pending_reviews if s.text_segment.id == segment_id]


class OpenCodingAgent:
    """开放编码 Agent（带人工审核）"""
    
    def __init__(self, config: Optional[OpenCodingConfig] = None):
        self.config = config or OpenCodingConfig()
        self.review_manager = CodeReviewManager()
        self.coding_history: List[Dict] = []
    
    def code_segment(
        self,
        segment: TextSegment,
        context: str = "",
        auto_review: Optional[bool] = None
    ) -> List[CodeUnit]:
        """对单个文本片段进行编码
        
        Args:
            segment: 文本片段
            context: 上下文信息
            auto_review: 是否自动审核（覆盖配置）
            
        Returns:
            已批准的代码列表（如果有）
        """
        should_review = auto_review if auto_review is not None else self.config.require_human_review
        
        if not self.config.allow_ai_suggestion:
            # 纯人工模式，返回空列表
            return []
        
        # 获取 AI 建议
        suggestions = self._get_ai_suggestions(segment, context)
        
        # 创建建议对象
        for sugg_data in suggestions:
            if sugg_data["confidence"] >= self.config.min_confidence:
                suggestion = SuggestedCode(
                    id=str(uuid.uuid4())[:8],
                    text_segment=segment,
                    code_label=sugg_data["code_label"],
                    code_definition=sugg_data["code_definition"],
                    confidence=sugg_data["confidence"],
                    ai_reasoning=sugg_data.get("reasoning", "")
                )
                
                # 判断是否自动通过
                if (self.config.auto_approve_high_confidence and 
                    suggestion.confidence >= self.config.high_confidence_threshold):
                    suggestion.review_status = ReviewStatus.APPROVED
                    code = CodeUnit(
                        id=str(uuid.uuid4())[:8],
                        text_segment=segment,
                        code_label=suggestion.code_label,
                        code_definition=suggestion.code_definition,
                        created_by=CodeSource.AI,
                        confidence=suggestion.confidence
                    )
                    self.review_manager.approved_codes.append(code)
                else:
                    self.review_manager.add_suggestion(suggestion)
        
        # 如果需要人工审核，返回已批准的（此时可能为空）
        # 如果不需要审核，自动批准所有待审建议
        if not should_review:
            pending_ids = [s.id for s in self.review_manager.pending_reviews]
            self.review_manager.batch_approve(pending_ids)
        
        return self.review_manager.approved_codes
    
    def _get_ai_suggestions(
        self,
        segment: TextSegment,
        context: str
    ) -> List[Dict]:
        """获取 AI 编码建议"""
        
        codebook_summary = self._get_current_codebook_summary()

        prompt = f"""你是一位质性研究专家，正在进行扎根理论的开放编码（Open Coding）。

请对以下文本片段进行分析，生成 {self.config.coding_style} 风格的初始代码：

【文本片段】
{segment.content}

【上下文】
{context}

【已有代码本】
{codebook_summary}
如果以下代码可以归入已有标签，请优先复用已有标签而非创建新标签。

【编码风格说明】
- descriptive: 描述性代码，概括文本内容
- in_vivo: 使用受访者原话作为代码
- process: 关注过程和行动

要求：
1. 代码应简洁、具体、贴近数据（10字以内）
2. 为每个代码提供简短定义（30字以内）
3. 提供编码理由（为什么选择这个代码）
4. 置信度 0-1 之间
5. 最多返回{self.config.max_codes_per_segment}个最相关的代码
6. 如果文本内容与已有代码标签匹配，请复用已有标签

返回 JSON 格式：
{{
    "codes": [
        {{
            "code_label": "代码标签",
            "code_definition": "代码定义",
            "confidence": 0.85,
            "reasoning": "编码理由"
        }}
    ]
}}
"""
        
        result = llm_client.generate_json(prompt, temperature=0.3)
        
        if "error" in result:
            # 返回模拟数据
            return self._generate_mock_suggestions(segment)
        
        return result.get("codes", [])
    
    def _generate_mock_suggestions(self, segment: TextSegment) -> List[Dict]:
        """生成模拟建议（API 失败时）"""
        return [
            {
                "code_label": f"代码_{segment.id}",
                "code_definition": "基于文本内容生成的模拟代码定义",
                "confidence": 0.75,
                "reasoning": "API 调用失败，使用模拟数据"
            }
        ]
    
    def batch_code(
        self,
        segments: List[TextSegment],
        progress_callback=None,
        review_callback=None
    ) -> Dict:
        """批量编码（支持中断和审核）
        
        Args:
            segments: 文本片段列表
            progress_callback: 进度回调函数 (current, total, segment)
            review_callback: 审核回调函数 (suggestions) -> approved_ids
            
        Returns:
            编码结果统计
        """
        total = len(segments)
        processed = 0
        
        for i, segment in enumerate(segments):
            # 编码单个片段
            self.code_segment(segment, auto_review=False)
            processed += 1
            
            # 进度回调
            if progress_callback:
                progress_callback(i + 1, total, segment)
            
            # 批量审核检查
            if (self.config.batch_review and 
                review_callback and 
                len(self.review_manager.pending_reviews) >= 5):
                # 触发批量审核
                approved_ids = review_callback(self.review_manager.pending_reviews)
                self.review_manager.batch_approve(approved_ids)
        
        # 最终审核
        if review_callback and self.review_manager.pending_reviews:
            approved_ids = review_callback(self.review_manager.pending_reviews)
            self.review_manager.batch_approve(approved_ids)
        
        return {
            "total_segments": total,
            "processed": processed,
            "approved_codes": len(self.review_manager.approved_codes),
            "pending_reviews": len(self.review_manager.pending_reviews),
            "review_summary": self.review_manager.get_review_summary()
        }
    
    def suggest_in_vivo_code(self, text: str) -> Optional[str]:
        """提取受访者原话作为 in-vivo 代码"""
        if len(text) <= 20:
            return text
        
        # 使用 AI 提取关键短语
        prompt = f"""从以下文本中提取最精炼的关键短语（in-vivo code），长度不超过15个字：

文本：{text}

直接返回短语，不要解释。"""
        
        result = llm_client.chat([
            {"role": "system", "content": "你是质性研究专家，擅长提取关键短语。"},
            {"role": "user", "content": prompt}
        ], temperature=0.3)
        
        result = result.strip().strip('"').strip("'")
        return result if len(result) <= 20 else None
    
    def detect_coding_conflicts(self, codes: List[CodeUnit]) -> List[Dict]:
        """检测编码冲突（相似代码）"""
        conflicts = []
        
        for i, code1 in enumerate(codes):
            for code2 in codes[i+1:]:
                # 简单的相似度检查
                label_sim = self._text_similarity(code1.code_label, code2.code_label)
                def_sim = self._text_similarity(code1.code_definition, code2.code_definition)
                
                if label_sim > 0.8 or def_sim > 0.7:
                    conflicts.append({
                        "type": "similar_code",
                        "code1": code1.code_label,
                        "code2": code2.code_label,
                        "similarity": max(label_sim, def_sim),
                        "recommendation": "考虑合并或区分定义"
                    })
        
        return conflicts
    
    def _get_current_codebook_summary(self) -> str:
        """Return a summary of already-approved code labels for the LLM prompt."""
        if not self.review_manager.approved_codes:
            return "（尚无已有代码）"
        labels = {}
        for c in self.review_manager.approved_codes:
            if c.code_label not in labels:
                labels[c.code_label] = c.code_definition
        lines = [f"- {label}: {defn}" for label, defn in labels.items()]
        return "\n".join(lines)

    def _text_similarity(self, text1: str, text2: str) -> float:
        """词级 Jaccard 相似度（支持中文分词）"""
        try:
            import jieba
            words1 = set(jieba.lcut(text1.lower()))
            words2 = set(jieba.lcut(text2.lower()))
        except ImportError:
            # fallback: split on whitespace for non-Chinese
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

        # Remove single-char stopwords
        stopwords = {'的', '了', '是', '在', '和', '与', '对', '有', ' '}
        words1 -= stopwords
        words2 -= stopwords

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
    
    def export_coding_log(self, output_path: str):
        """导出编码日志（用于审计）"""
        log_data = {
            "config": {
                "max_codes_per_segment": self.config.max_codes_per_segment,
                "min_confidence": self.config.min_confidence,
                "coding_style": self.config.coding_style,
                "require_human_review": self.config.require_human_review
            },
            "review_summary": self.review_manager.get_review_summary(),
            "approved_codes": [
                {
                    "id": c.id,
                    "label": c.code_label,
                    "definition": c.code_definition,
                    "confidence": c.confidence,
                    "segment_id": c.text_segment.id
                }
                for c in self.review_manager.approved_codes
            ],
            "coding_history": self.coding_history
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        return output_path
