"""
测试开放编码模块
"""
import pytest
from datetime import datetime

from CodeEngine.open_coding.agent import (
    OpenCodingAgent, OpenCodingConfig,
    SuggestedCode, CodeReviewManager, ReviewStatus
)
from CodeEngine.ir.code_ir import TextSegment, CodeUnit, CodeSource


class TestCodeReviewManager:
    """测试编码审核管理器"""
    
    @pytest.fixture
    def sample_segment(self):
        return TextSegment(
            id="S001",
            content="测试文本片段",
            source="test.txt",
            position=(0, 10)
        )
    
    @pytest.fixture
    def sample_suggestion(self, sample_segment):
        return SuggestedCode(
            id="C001",
            text_segment=sample_segment,
            code_label="测试代码",
            code_definition="这是一个测试代码",
            confidence=0.85,
            ai_reasoning="AI 的编码理由"
        )
    
    def test_add_suggestion(self, sample_suggestion):
        """测试添加待审核建议"""
        manager = CodeReviewManager()
        manager.add_suggestion(sample_suggestion)
        
        assert len(manager.pending_reviews) == 1
        assert manager.pending_reviews[0].id == "C001"
    
    def test_approve_suggestion(self, sample_suggestion):
        """测试批准建议"""
        manager = CodeReviewManager()
        manager.add_suggestion(sample_suggestion)
        
        code = manager.approve("C001", "审核通过")
        
        assert code is not None
        assert code.code_label == "测试代码"
        assert code.created_by == CodeSource.COLLABORATION
        assert len(manager.approved_codes) == 1
        assert len(manager.pending_reviews) == 0
    
    def test_reject_suggestion(self, sample_suggestion):
        """测试拒绝建议"""
        manager = CodeReviewManager()
        manager.add_suggestion(sample_suggestion)
        
        result = manager.reject("C001", "不合适")
        
        assert result == True
        assert manager.rejected_count == 1
        assert len(manager.pending_reviews) == 0
    
    def test_modify_and_approve(self, sample_suggestion):
        """测试修改后批准"""
        manager = CodeReviewManager()
        manager.add_suggestion(sample_suggestion)
        
        code = manager.modify_and_approve(
            "C001",
            "修改后的标签",
            "修改后的定义",
            "需要修改"
        )
        
        assert code is not None
        assert code.code_label == "修改后的标签"
        assert code.confidence == 0.85 * 0.9  # 修改降低置信度
        assert code.created_by == CodeSource.COLLABORATION
    
    def test_batch_approve(self, sample_segment):
        """测试批量批准"""
        manager = CodeReviewManager()
        
        for i in range(5):
            sugg = SuggestedCode(
                id=f"C00{i}",
                text_segment=sample_segment,
                code_label=f"代码{i}",
                code_definition=f"定义{i}",
                confidence=0.8,
                ai_reasoning="AI 理由"
            )
            manager.add_suggestion(sugg)
        
        approved = manager.batch_approve(["C000", "C001", "C002"])
        
        assert len(approved) == 3
        assert len(manager.approved_codes) == 3
        assert len(manager.pending_reviews) == 2
    
    def test_get_review_summary(self, sample_suggestion):
        """测试获取审核摘要"""
        manager = CodeReviewManager()
        manager.add_suggestion(sample_suggestion)
        manager.approve("C001")
        
        # 添加一个已拒绝的
        sugg2 = SuggestedCode(
            id="C002",
            text_segment=sample_suggestion.text_segment,
            code_label="代码2",
            code_definition="定义2",
            confidence=0.8,
            ai_reasoning="AI 理由"
        )
        manager.add_suggestion(sugg2)
        manager.reject("C002")
        
        summary = manager.get_review_summary()
        
        assert summary["pending"] == 0
        assert summary["approved"] == 1
        assert summary["rejected"] == 1
        assert summary["total"] == 2


class TestOpenCodingAgent:
    """测试开放编码 Agent"""
    
    @pytest.fixture
    def agent(self):
        return OpenCodingAgent(OpenCodingConfig(
            allow_ai_suggestion=True,
            require_human_review=True,
            min_confidence=0.7
        ))
    
    @pytest.fixture
    def sample_segments(self):
        return [
            TextSegment(
                id=f"S00{i}",
                content=f"这是第{i}个测试文本片段，用于测试编码功能。",
                source="test.txt",
                position=(i*20, (i+1)*20)
            )
            for i in range(3)
        ]
    
    def test_initialization(self, agent):
        """测试初始化"""
        assert agent.config.allow_ai_suggestion == True
        assert agent.config.require_human_review == True
        assert agent.review_manager is not None
    
    def test_config_variations(self):
        """测试不同配置"""
        # 纯人工模式
        config = OpenCodingConfig(allow_ai_suggestion=False)
        agent = OpenCodingAgent(config)
        assert agent.config.allow_ai_suggestion == False
        
        # 自动审核模式
        config = OpenCodingConfig(
            require_human_review=False,
            auto_approve_high_confidence=True
        )
        agent = OpenCodingAgent(config)
        assert agent.config.require_human_review == False
    
    def test_detect_coding_conflicts(self):
        """测试编码冲突检测"""
        agent = OpenCodingAgent()
        
        segments = [
            TextSegment(id="S001", content="文本1", source="t.txt", position=(0, 5)),
            TextSegment(id="S002", content="文本2", source="t.txt", position=(5, 10))
        ]
        
        codes = [
            CodeUnit(id="C1", text_segment=segments[0], 
                    code_label="相似代码A", code_definition="定义A",
                    created_by=CodeSource.AI, confidence=0.8),
            CodeUnit(id="C2", text_segment=segments[1],
                    code_label="相似代码A", code_definition="定义B",  # 标签相似
                    created_by=CodeSource.AI, confidence=0.8),
            CodeUnit(id="C3", text_segment=segments[0],
                    code_label="完全不同的代码", code_definition="定义C",
                    created_by=CodeSource.AI, confidence=0.8)
        ]
        
        conflicts = agent.detect_coding_conflicts(codes)
        
        assert len(conflicts) >= 1  # 至少检测到一个冲突
        assert any(c["code1"] == "相似代码A" and c["code2"] == "相似代码A" for c in conflicts)
    
    def test_text_similarity(self):
        """测试文本相似度计算"""
        agent = OpenCodingAgent()
        
        # 完全相同
        assert agent._text_similarity("hello", "hello") == 1.0
        
        # 完全不同
        sim = agent._text_similarity("abc", "xyz")
        assert sim < 0.5
        
        # 空字符串
        assert agent._text_similarity("", "hello") == 0.0
        assert agent._text_similarity("hello", "") == 0.0
    
    def test_coding_log_export(self, agent, tmp_path):
        """测试编码日志导出"""
        # 添加一些模拟数据
        segment = TextSegment(id="S001", content="测试", source="t.txt", position=(0, 2))
        code = CodeUnit(
            id="C001",
            text_segment=segment,
            code_label="测试代码",
            code_definition="测试定义",
            created_by=CodeSource.AI,
            confidence=0.8
        )
        agent.review_manager.approved_codes.append(code)
        
        log_path = str(tmp_path / "test_log.json")
        result = agent.export_coding_log(log_path)
        
        assert result == log_path
        import os
        assert os.path.exists(log_path)


class TestOpenCodingIntegration:
    """集成测试"""
    
    def test_full_coding_workflow(self):
        """测试完整编码工作流"""
        agent = OpenCodingAgent(OpenCodingConfig(
            allow_ai_suggestion=True,
            require_human_review=False  # 自动审核
        ))
        
        segments = [
            TextSegment(id="S001", content="用户反馈产品质量很好", source="feedback.txt", position=(0, 15)),
            TextSegment(id="S002", content="客服响应速度很快", source="feedback.txt", position=(15, 28))
        ]
        
        # 编码所有片段
        for seg in segments:
            agent.code_segment(seg, auto_review=False)
        
        # 自动批准所有待审建议
        pending_ids = [s.id for s in agent.review_manager.pending_reviews]
        agent.review_manager.batch_approve(pending_ids)
        
        # 验证结果
        summary = agent.review_manager.get_review_summary()
        assert summary["pending"] == 0
        assert summary["approved"] >= 0


class TestWordLevelSimilarity:
    """测试词级相似度算法"""

    def test_word_level_similarity_chinese(self):
        """测试中文词级相似度"""
        agent = OpenCodingAgent()

        # 相似标签应该得分高
        sim = agent._text_similarity("AI工具使用", "使用AI工具")
        assert sim > 0.5, f"Expected high similarity, got {sim}"

        # 完全不同的标签应该得分低
        sim = agent._text_similarity("AI工具使用", "情感支持需求")
        assert sim < 0.3, f"Expected low similarity, got {sim}"

    def test_identical_text(self):
        """完全相同的文本相似度应为 1.0"""
        agent = OpenCodingAgent()
        sim = agent._text_similarity("编码标签", "编码标签")
        assert sim == 1.0

    def test_empty_text(self):
        """空文本相似度应为 0.0"""
        agent = OpenCodingAgent()
        assert agent._text_similarity("", "hello") == 0.0
        assert agent._text_similarity("hello", "") == 0.0


class TestCodebookSummary:
    """测试代码本摘要功能"""

    def test_codebook_summary_empty(self):
        """无已批准代码时返回占位符"""
        agent = OpenCodingAgent()
        summary = agent._get_current_codebook_summary()
        assert "尚无已有代码" in summary

    def test_codebook_summary_populated(self):
        """有已批准代码时返回代码列表"""
        agent = OpenCodingAgent()

        segment = TextSegment(id="S001", content="测试文本", source="t.txt", position=(0, 4))
        code1 = CodeUnit(
            id="C001", text_segment=segment,
            code_label="AI工具依赖", code_definition="对AI工具的高频使用",
            created_by=CodeSource.AI, confidence=0.9
        )
        code2 = CodeUnit(
            id="C002", text_segment=segment,
            code_label="情感支持", code_definition="寻求情感上的安慰",
            created_by=CodeSource.AI, confidence=0.85
        )
        agent.review_manager.approved_codes.extend([code1, code2])

        summary = agent._get_current_codebook_summary()
        assert "AI工具依赖" in summary
        assert "情感支持" in summary
        assert "对AI工具的高频使用" in summary

    def test_codebook_summary_deduplicates(self):
        """重复标签只保留一次"""
        agent = OpenCodingAgent()

        segment = TextSegment(id="S001", content="测试文本", source="t.txt", position=(0, 4))
        for i in range(3):
            code = CodeUnit(
                id=f"C{i}", text_segment=segment,
                code_label="重复标签", code_definition="定义",
                created_by=CodeSource.AI, confidence=0.9
            )
            agent.review_manager.approved_codes.append(code)

        summary = agent._get_current_codebook_summary()
        assert summary.count("重复标签") == 1

