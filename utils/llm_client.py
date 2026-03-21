"""
统一的 LLM 客户端封装
支持 OpenAI 兼容接口（Moonshot/Kimi）和本地 Ollama 模型
"""
import os
import time
import logging
from typing import List, Dict, Optional, Iterator, Union
from dataclasses import dataclass
from enum import Enum
import json
import requests

try:
    from openai import OpenAI, APIError, RateLimitError, APITimeoutError
except ImportError:
    OpenAI = None
    APIError = Exception
    RateLimitError = Exception
    APITimeoutError = Exception

from config import settings

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM 提供商类型"""
    OPENAI = "openai"
    MOONSHOT = "moonshot"
    OLLAMA = "ollama"
    MOCK = "mock"


@dataclass
class LLMResponse:
    """统一的 LLM 响应格式"""
    content: str
    provider: LLMProvider
    model: str
    latency_ms: float
    success: bool
    error_message: Optional[str] = None


class LLMClient:
    """增强版 LLM 客户端
    
    特性：
    - 支持多提供商（OpenAI、Moonshot、Ollama）
    - 自动重试机制（指数退避）
    - 降级策略（远程失败时切换本地模型）
    - 详细的错误处理和日志
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[LLMProvider] = None,
        ollama_host: str = "http://localhost:11434",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.api_key = api_key or settings.openai_api_key
        self.base_url = base_url or settings.openai_base_url
        self.model = model or settings.default_model
        self.provider = provider or self._detect_provider()
        self.ollama_host = ollama_host
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 初始化客户端
        self._openai_client = None
        self._ollama_available = None  # 延迟检测
        
        if self.provider in [LLMProvider.OPENAI, LLMProvider.MOONSHOT]:
            if OpenAI and self.api_key:
                self._openai_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                logger.warning("OpenAI 客户端未初始化，将使用模拟模式或 Ollama")
                self.provider = LLMProvider.MOCK
    
    def _detect_provider(self) -> LLMProvider:
        """根据配置自动检测提供商"""
        if not self.api_key:
            return LLMProvider.OLLAMA
        if "moonshot" in self.base_url.lower():
            return LLMProvider.MOONSHOT
        return LLMProvider.OPENAI
    
    def _check_ollama_available(self) -> bool:
        """检查 Ollama 是否可用"""
        if self._ollama_available is not None:
            return self._ollama_available
        
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            self._ollama_available = response.status_code == 200
            if self._ollama_available:
                logger.info(f"Ollama 服务可用: {self.ollama_host}")
        except Exception as e:
            logger.debug(f"Ollama 检查失败: {e}")
            self._ollama_available = False
        
        return self._ollama_available
    
    def _call_openai(
        self,
        messages: List[Dict],
        temperature: float,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """调用 OpenAI 兼容 API"""
        if not self._openai_client:
            raise ValueError("OpenAI 客户端未初始化")
        
        response = self._openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=stream
        )
        
        if stream:
            return response
        return response.choices[0].message.content
    
    def _call_ollama(
        self,
        messages: List[Dict],
        temperature: float,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """调用本地 Ollama 服务"""
        url = f"{self.ollama_host}/api/chat"
        
        # 转换消息格式
        ollama_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            ollama_messages.append({"role": role, "content": content})
        
        payload = {
            "model": self._get_ollama_model(),
            "messages": ollama_messages,
            "stream": stream,
            "options": {"temperature": temperature}
        }
        
        if stream:
            return self._ollama_stream(url, payload)
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def _ollama_stream(self, url: str, payload: Dict) -> Iterator[str]:
        """Ollama 流式输出"""
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
    
    def _get_ollama_model(self) -> str:
        """获取对应的 Ollama 模型名称"""
        # 常见模型映射
        model_map = {
            "gpt-4": "llama2:13b",
            "gpt-3.5-turbo": "llama2:7b",
            "gpt-4o": "llama3:8b",
            "gpt-4o-mini": "llama3:8b",
        }
        return model_map.get(self.model, "llama2:7b")
    
    def _execute_with_retry(
        self,
        func,
        *args,
        **kwargs
    ) -> LLMResponse:
        """带重试机制的执行器"""
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                
                return LLMResponse(
                    content=result if isinstance(result, str) else "",
                    provider=self.provider,
                    model=self.model,
                    latency_ms=latency,
                    success=True
                )
                
            except (RateLimitError, APITimeoutError) as e:
                # 可重试错误
                last_error = e
                wait_time = self.retry_delay * (2 ** attempt)  # 指数退避
                logger.warning(f"API 限流/超时，第 {attempt + 1} 次重试，等待 {wait_time}s: {e}")
                time.sleep(wait_time)
                
            except APIError as e:
                # API 错误，尝试降级
                last_error = e
                logger.error(f"API 错误: {e}")
                if attempt < self.max_retries - 1 and self._check_ollama_available():
                    logger.info("尝试降级到 Ollama...")
                    self.provider = LLMProvider.OLLAMA
                    continue
                break
                
            except Exception as e:
                last_error = e
                logger.error(f"意外错误: {e}")
                break
        
        # 所有重试失败
        latency = (time.time() - start_time) * 1000
        return LLMResponse(
            content=self._mock_response(args[0] if args else []),
            provider=LLMProvider.MOCK,
            model="mock",
            latency_ms=latency,
            success=False,
            error_message=str(last_error)
        )
    
    def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """发送聊天请求（带重试和降级）
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            stream: 是否流式输出
            
        Returns:
            响应文本（失败时返回模拟响应）
        """
        if stream:
            return self._chat_stream(messages, temperature)
        
        response = self._execute_with_retry(
            self._chat_single,
            messages,
            temperature
        )
        
        if not response.success:
            logger.warning(f"请求失败，使用模拟响应。错误: {response.error_message}")
        
        return response.content
    
    def _chat_single(self, messages: List[Dict], temperature: float) -> str:
        """单次聊天请求"""
        if self.provider == LLMProvider.OLLAMA and self._check_ollama_available():
            return self._call_ollama(messages, temperature, stream=False)
        elif self.provider in [LLMProvider.OPENAI, LLMProvider.MOONSHOT]:
            return self._call_openai(messages, temperature, stream=False)
        else:
            return self._mock_response(messages)
    
    def _chat_stream(self, messages: List[Dict], temperature: float) -> Iterator[str]:
        """流式聊天请求"""
        try:
            if self.provider == LLMProvider.OLLAMA and self._check_ollama_available():
                yield from self._call_ollama(messages, temperature, stream=True)
            elif self.provider in [LLMProvider.OPENAI, LLMProvider.MOONSHOT]:
                response = self._call_openai(messages, temperature, stream=True)
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield self._mock_response(messages)
        except Exception as e:
            logger.error(f"流式请求失败: {e}")
            yield self._mock_response(messages)
    
    def chat_stream(self, messages: List[Dict], temperature: float = 0.7) -> Iterator[str]:
        """流式输出接口"""
        return self._chat_stream(messages, temperature)
    
    def _mock_response(self, messages: List[Dict]) -> str:
        """模拟响应（API 不可用时）
        
        根据消息内容生成更智能的模拟响应
        """
        # 尝试从消息中提取一些上下文
        last_message = messages[-1].get("content", "") if messages else ""
        
        # 如果是 JSON 生成请求
        if "JSON" in last_message or "json" in last_message:
            return json.dumps({
                "mock": True,
                "message": "这是模拟响应。请配置有效的 API Key 或启动 Ollama 服务。",
                "hint": "支持的提供商: OpenAI, Moonshot(Kimi), Ollama(本地)"
            }, ensure_ascii=False)
        
        return "[模拟响应] API 未配置或调用失败。请检查：\n" \
               "1. 已设置 OPENAI_API_KEY 环境变量\n" \
               "2. 或启动本地 Ollama 服务 (http://localhost:11434)\n" \
               "当前将使用模拟数据继续演示。"
    
    def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        temperature: float = 0.3,
        max_parse_retries: int = 2
    ) -> Dict:
        """生成结构化 JSON（带重试和修复）
        
        Args:
            prompt: 提示词
            schema: JSON Schema
            temperature: 温度参数
            max_parse_retries: JSON 解析失败时的最大重试次数
            
        Returns:
            解析后的字典（失败时包含 error 字段）
        """
        system_msg = (
            "你是一个专业的质性研究助手。请严格按照 JSON 格式返回结果，"
            "不要包含任何 markdown 代码块标记（如 ```json），直接返回原始 JSON。"
        )
        if schema:
            system_msg += f"\nJSON Schema: {json.dumps(schema, ensure_ascii=False)}"
        
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
        
        for attempt in range(max_parse_retries):
            content = self.chat(messages, temperature=temperature)
            
            # 清理 markdown 代码块
            cleaned = self._clean_json_content(content)
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON 解析失败 (尝试 {attempt + 1}/{max_parse_retries}): {e}")
                
                # 尝试修复常见的 JSON 问题
                if attempt < max_parse_retries - 1:
                    # 提示 LLM 重新生成
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user",
                        "content": f"上面的响应不是有效的 JSON，请修正后重新返回。错误: {str(e)[:100]}"
                    })
        
        logger.error(f"JSON 解析最终失败，原始内容: {content[:200]}")
        return {
            "error": "JSON 解析失败",
            "raw": content,
            "hint": "请检查 LLM 响应格式或降低 temperature 参数"
        }
    
    def _clean_json_content(self, content: str) -> str:
        """清理 JSON 内容中的 markdown 标记"""
        content = content.strip()
        
        # 移除开头的 ```json 或 ```
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        
        # 移除结尾的 ```
        if content.endswith("```"):
            content = content[:-3]
        
        # 移除可能的注释（JSON 标准不允许）
        lines = []
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line.startswith('//') and not line.startswith('#'):
                lines.append(line)
        
        return '\n'.join(lines)
    
    def health_check(self) -> Dict:
        """健康检查，返回各提供商状态"""
        result = {
            "current_provider": self.provider.value,
            "model": self.model,
            "providers": {}
        }
        
        # 检查 OpenAI
        if self._openai_client:
            try:
                # 简单测试（不实际调用）
                result["providers"]["openai"] = {
                    "available": True,
                    "model": self.model
                }
            except Exception as e:
                result["providers"]["openai"] = {
                    "available": False,
                    "error": str(e)
                }
        else:
            result["providers"]["openai"] = {
                "available": False,
                "reason": "API Key 未设置"
            }
        
        # 检查 Ollama
        result["providers"]["ollama"] = {
            "available": self._check_ollama_available(),
            "host": self.ollama_host,
            "model": self._get_ollama_model()
        }
        
        return result


# 全局 LLM 客户端实例
llm_client = LLMClient()
