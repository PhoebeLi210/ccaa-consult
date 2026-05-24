#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - LLM客户端封装
支持DeepSeek和OpenAI API
"""
import asyncio
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import httpx
from abc import ABC, abstractmethod


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "deepseek"  # deepseek / openai
    api_key: str = ""
    api_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system / user / assistant
    content: str


class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> str:
        """发送聊天请求"""
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        pass


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    async def chat(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> str:
        """发送聊天请求"""
        url = f"{self.config.api_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        url = f"{self.config.api_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True
        }
        
        async with self.client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk["choices"][0].get("delta", {}).get("content"):
                            yield chunk["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.config.api_url = config.api_url or "https://api.openai.com/v1"
        self.config.model = config.model or "gpt-4"
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    async def chat(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> str:
        """发送聊天请求"""
        url = f"{self.config.api_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        url = f"{self.config.api_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True
        }
        
        async with self.client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk["choices"][0].get("delta", {}).get("content"):
                            yield chunk["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class LLMClientFactory:
    """LLM客户端工厂"""
    
    @staticmethod
    def create(config: LLMConfig) -> BaseLLMClient:
        """创建LLM客户端"""
        if config.provider == "deepseek":
            return DeepSeekClient(config)
        elif config.provider == "openai":
            return OpenAIClient(config)
        else:
            raise ValueError(f"不支持的LLM提供商: {config.provider}")


class LLMService:
    """LLM服务封装"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = LLMClientFactory.create(config)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """生成文本"""
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=prompt))
        
        return await self.client.chat(messages, **kwargs)
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成JSON格式响应"""
        # 添加JSON格式要求
        json_prompt = f"{prompt}\n\n请以JSON格式输出，不要包含其他内容。"
        
        response = await self.generate(json_prompt, system_prompt, **kwargs)
        
        # 尝试解析JSON
        try:
            # 移除可能的markdown代码块标记
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return {"error": "JSON解析失败", "raw_response": response}
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=prompt))
        
        async for chunk in self.client.chat_stream(messages, **kwargs):
            yield chunk
    
    async def close(self):
        """关闭客户端"""
        if hasattr(self.client, 'close'):
            await self.client.close()


# 便捷函数
def create_llm_service(
    api_key: str,
    provider: str = "deepseek",
    model: str = "deepseek-chat",
    **kwargs
) -> LLMService:
    """创建LLM服务的便捷函数"""
    config = LLMConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        **kwargs
    )
    return LLMService(config)


# 测试代码
if __name__ == "__main__":
    import os
    
    async def test_llm():
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            print("请设置DEEPSEEK_API_KEY环境变量")
            return
        
        service = create_llm_service(api_key, provider="deepseek")
        
        # 测试生成
        response = await service.generate(
            "请用一句话介绍ISO9001质量管理体系",
            system_prompt="你是一个ISO体系咨询专家"
        )
        print(f"响应: {response}")
        
        # 测试JSON生成
        json_response = await service.generate_json(
            "提取以下企业信息：武汉鑫辰宇物业服务有限公司，员工50人，主要从事物业管理服务",
            system_prompt="你是一个信息提取专家，请从文本中提取企业名称、员工人数、主营业务"
        )
        print(f"JSON响应: {json_response}")
        
        await service.close()
    
    asyncio.run(test_llm())
