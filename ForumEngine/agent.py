"""
ForumEngine - 编码协作论坛
模拟研究团队编码讨论会
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from CodeEngine.ir.code_ir import CodeUnit


class ParticipantRole(Enum):
    """参与者角色"""
    PRIMARY_CODER = "primary_coder"      # 主编码者（研究者）
    PEER_REVIEWER = "peer_reviewer"      # 同伴编码者
    DEVIL_ADVOCATE = "devil_advocate"    # 质疑者
    AI_ASSISTANT = "ai_assistant"        # AI 助手


@dataclass
class ForumMessage:
    """论坛消息"""
    id: str
    participant: str
    role: ParticipantRole
    content: str
    target_code_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    consensus_reached: bool = False


@dataclass
class DiscussionThread:
    """讨论线程"""
    id: str
    topic: str                          # 讨论主题（通常是代码ID）
    messages: List[ForumMessage] = field(default_factory=list)
    status: str = "open"                # open/resolved/disputed
    final_decision: Optional[str] = None


class Participant:
    """参与者基类"""
    
    def __init__(self, name: str, role: ParticipantRole):
        self.name = name
        self.role = role
    
    def respond(self, context: str, code: CodeUnit) -> str:
        """生成回应"""
        raise NotImplementedError


class DevilAdvocateAgent(Participant):
    """质疑者 Agent - 主动挑战假设"""
    
    def __init__(self):
        super().__init__("DevilAdvocate", ParticipantRole.DEVIL_ADVOCATE)
    
    def respond(self, context: str, code: CodeUnit) -> str:
        """生成质疑"""
        challenges = [
            f"为什么选择 '{code.code_label}' 这个代码？还有其他可能的理解吗？",
            f"这个代码定义是否太宽泛？能否更具体？",
            f"这段文本是否有更深层含义？目前编码是否流于表面？",
            f"是否存在反例或不符合这个代码的情况？",
        ]
        # 简单实现：按顺序返回质疑
        return challenges[hash(code.id) % len(challenges)]


class AIAssistantAgent(Participant):
    """AI 助手 Agent - 提供建议和检查"""
    
    def __init__(self):
        super().__init__("AIAssistant", ParticipantRole.AI_ASSISTANT)
    
    def respond(self, context: str, code: CodeUnit) -> str:
        """生成建议"""
        return f"建议检查 '{code.code_label}' 与已有代码本的一致性，避免概念重叠。"
    
    def check_consistency(self, new_code: CodeUnit, existing_codes: List[CodeUnit]) -> List[str]:
        """检查新代码与现有代码的一致性"""
        issues = []
        for existing in existing_codes:
            if new_code.code_label.lower() == existing.code_label.lower():
                issues.append(f"代码 '{new_code.code_label}' 已存在")
        return issues


class PeerReviewerAgent(Participant):
    """同伴编码者 Agent - 独立编码并比较"""
    
    def __init__(self):
        super().__init__("PeerReviewer", ParticipantRole.PEER_REVIEWER)
        self.independent_codes: Dict[str, List[str]] = {}  # segment_id -> codes
    
    def code_independently(self, segments: List[Dict]) -> None:
        """独立编码"""
        for seg in segments:
            # 模拟独立编码
            self.independent_codes[seg["id"]] = ["code_a", "code_b"]
    
    def calculate_agreement(self, primary_codes: List[str]) -> float:
        """计算编码一致性（简化版 Cohen's Kappa）"""
        # 实际实现需要更复杂的计算
        return 0.75  # 模拟75%一致性


class ForumEngine:
    """论坛引擎主类"""
    
    def __init__(self):
        self.participants: List[Participant] = []
        self.threads: List[DiscussionThread] = []
        self._setup_default_participants()
    
    def _setup_default_participants(self):
        """设置默认参与者"""
        self.participants.extend([
            DevilAdvocateAgent(),
            AIAssistantAgent(),
            PeerReviewerAgent()
        ])
    
    def create_discussion(self, topic: str) -> DiscussionThread:
        """创建讨论线程"""
        import uuid
        thread = DiscussionThread(
            id=str(uuid.uuid4())[:8],
            topic=topic
        )
        self.threads.append(thread)
        return thread
    
    def discuss_code(self, code: CodeUnit, context: str = "") -> DiscussionThread:
        """对特定代码发起讨论"""
        thread = self.create_discussion(f"Code: {code.code_label}")
        
        # 主编码者发言
        thread.messages.append(ForumMessage(
            id="1",
            participant="Researcher",
            role=ParticipantRole.PRIMARY_CODER,
            content=f"我对这段文本编码为 '{code.code_label}'，定义为：{code.code_definition}",
            target_code_id=code.id
        ))
        
        # 各 Agent 回应
        for participant in self.participants:
            response = participant.respond(context, code)
            thread.messages.append(ForumMessage(
                id=str(len(thread.messages) + 1),
                participant=participant.name,
                role=participant.role,
                content=response,
                target_code_id=code.id
            ))
        
        return thread
    
    def reach_consensus(self, thread_id: str, decision: str) -> bool:
        """达成编码共识"""
        for thread in self.threads:
            if thread.id == thread_id:
                thread.status = "resolved"
                thread.final_decision = decision
                return True
        return False
