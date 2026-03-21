"""
测试 LLM 客户端
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from utils.llm_client import LLMClient, LLMProvider, LLMResponse


class TestLLMClient:
    """测试 LLM 客户端功能"""
    
    def test_init_with_mock_provider(self):
        """测试使用模拟提供商初始化"""
        client = LLMClient(
            api_key="",
            provider=LLMProvider.MOCK
        )
        assert client.provider == LLMProvider.MOCK
    
    def test_provider_detection_moonshot(self):
        """测试 Moonshot 提供商自动检测"""
        client = LLMClient(
            api_key="test_key",
            base_url="https://api.moonshot.cn/v1"
        )
        assert client.provider == LLMProvider.MOONSHOT
    
    def test_provider_detection_openai(self):
        """测试 OpenAI 提供商自动检测"""
        client = LLMClient(
            api_key="test_key",
            base_url="https://api.openai.com/v1"
        )
        assert client.provider == LLMProvider.OPENAI
    
    def test_mock_response_generation(self):
        """测试模拟响应生成"""
        client = LLMClient(provider=LLMProvider.MOCK)
        
        messages = [{"role": "user", "content": "测试"}]
        response = client.chat(messages)
        
        assert "模拟响应" in response
        assert "API 未配置" in response
    
    def test_mock_json_response(self):
        """测试模拟 JSON 响应"""
        client = LLMClient(provider=LLMProvider.MOCK)
        
        messages = [{"role": "user", "content": "返回 JSON"}]
        response = client.chat(messages)
        
        # 应该能解析为 JSON
        data = json.loads(response)
        assert "mock" in data
        assert data["mock"] == True
    
    @patch('utils.llm_client.requests.get')
    def test_ollama_health_check_available(self, mock_get):
        """测试 Ollama 健康检查 - 可用"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = LLMClient(provider=LLMProvider.OLLAMA)
        assert client._check_ollama_available() == True
    
    @patch('utils.llm_client.requests.get')
    def test_ollama_health_check_unavailable(self, mock_get):
        """测试 Ollama 健康检查 - 不可用"""
        mock_get.side_effect = Exception("Connection refused")
        
        client = LLMClient(provider=LLMProvider.OLLAMA)
        assert client._check_ollama_available() == False
    
    def test_health_check_structure(self):
        """测试健康检查返回结构"""
        client = LLMClient(provider=LLMProvider.MOCK)
        health = client.health_check()
        
        assert "current_provider" in health
        assert "model" in health
        assert "providers" in health
        assert "ollama" in health["providers"]
    
    def test_clean_json_content(self):
        """测试 JSON 内容清理"""
        client = LLMClient(provider=LLMProvider.MOCK)
        
        # 测试 markdown 代码块
        content = "```json\n{\"key\": \"value\"}\n```"
        cleaned = client._clean_json_content(content)
        assert cleaned.strip() == '{"key": "value"}'
        
        # 测试普通 markdown
        content = "```\n{\"key\": \"value\"}\n```"
        cleaned = client._clean_json_content(content)
        assert cleaned.strip() == '{"key": "value"}'
    
    def test_text_similarity(self):
        """测试文本相似度计算（使用 OpenCodingAgent 的方法）"""
        from CodeEngine.open_coding.agent import OpenCodingAgent
        
        agent = OpenCodingAgent()
        
        # 相同文本
        sim = agent._text_similarity("hello", "hello")
        assert sim == 1.0
        
        # 完全不同
        sim = agent._text_similarity("abc", "xyz")
        assert sim < 0.5
        
        # 部分相似
        sim = agent._text_similarity("hello world", "hello there")
        assert 0 < sim < 1


class TestLLMClientRetry:
    """测试重试机制"""
    
    @patch('utils.llm_client.OpenAI')
    def test_retry_on_rate_limit(self, mock_openai_class):
        """测试限流时重试"""
        from openai import RateLimitError
        
        mock_client = Mock()
        # 前两次调用抛出 RateLimitError，第三次成功
        mock_client.chat.completions.create.side_effect = [
            RateLimitError("Rate limited", response=Mock(), body=None),
            RateLimitError("Rate limited", response=Mock(), body=None),
            Mock(choices=[Mock(message=Mock(content="Success"))])
        ]
        mock_openai_class.return_value = mock_client
        
        client = LLMClient(
            api_key="test_key",
            provider=LLMProvider.OPENAI,
            max_retries=3,
            retry_delay=0.1  # 快速测试
        )
        
        messages = [{"role": "user", "content": "测试"}]
        response = client.chat(messages)
        
        assert response == "Success"
        assert mock_client.chat.completions.create.call_count == 3


class TestLLMClientStream:
    """测试流式输出"""
    
    def test_stream_with_mock(self):
        """测试模拟流式输出"""
        client = LLMClient(provider=LLMProvider.MOCK)
        
        messages = [{"role": "user", "content": "测试"}]
        chunks = list(client.chat_stream(messages))
        
        assert len(chunks) == 1
        assert "模拟响应" in chunks[0]
