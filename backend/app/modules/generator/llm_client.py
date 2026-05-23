#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - LLM客户端封装
支持DeepSeek、OpenAI、智谱AI(GLM-4)、通义千问(DashScope) API
"""
import asyncio
import json
import os
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import httpx
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# 环境变量自动加载
# ---------------------------------------------------------------------------

def _load_env_if_missing() -> None:
    """尝试从 .env 文件加载环境变量（仅在尚未加载时）"""
    if os.getenv("AI_PROVIDER"):
        return  # 已经有值，不需要重复加载
    try:
        from dotenv import load_dotenv
        # 查找 .env 文件：优先当前工作目录，其次项目根目录
        for candidate in (".env", os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")):
            candidate = os.path.normpath(candidate)
            if os.path.isfile(candidate):
                load_dotenv(candidate, override=False)
                break
    except ImportError:
        pass  # python-dotenv 未安装，跳过


_load_env_if_missing()


# ---------------------------------------------------------------------------
# 预设提供商配置表（模块级常量，供 LLMConfig 和工厂共用）
# ---------------------------------------------------------------------------

PROVIDER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "deepseek": {
        "api_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "openai": {
        "api_url": "https://api.openai.com/v1",
        "model": "gpt-4",
        "env_key": "OPENAI_API_KEY",
    },
    "zhipu": {
        "api_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4",
        "env_key": "ZHIPU_API_KEY",
    },
    "dashscope": {
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "env_key": "DASHSCOPE_API_KEY",
    },
}


# ---------------------------------------------------------------------------
# LLM 配置
# ---------------------------------------------------------------------------

@dataclass
class LLMConfig:
    """LLM配置"""

    provider: str = "deepseek"  # deepseek / openai / zhipu / dashscope
    api_key: str = ""
    api_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60

    def __post_init__(self):
        """初始化后自动从环境变量补全缺失的配置"""
        # 如果 api_key 为空，尝试从环境变量获取
        if not self.api_key:
            self.api_key = self._resolve_api_key()
        # 如果 api_url / model 仍是默认值但 provider 已变更，使用预设
        preset = PROVIDER_CONFIGS.get(self.provider)
        if preset:
            if self.api_url == "https://api.deepseek.com/v1" and self.provider != "deepseek":
                self.api_url = preset["api_url"]
            if self.model == "deepseek-chat" and self.provider != "deepseek":
                self.model = preset["model"]

    def _resolve_api_key(self) -> str:
        """按优先级解析 API Key"""
        # 1. 通用环境变量 AI_API_KEY
        key = os.getenv("AI_API_KEY", "")
        if key:
            return key
        # 2. 提供商专属环境变量
        preset = PROVIDER_CONFIGS.get(self.provider)
        if preset:
            key = os.getenv(preset["env_key"], "")
            if key:
                return key
        # 3. 兼容旧配置 LLM_API_KEY
        return os.getenv("LLM_API_KEY", "")

    @classmethod
    def from_env(cls, provider: Optional[str] = None) -> "LLMConfig":
        """从环境变量创建配置的便捷方法"""
        provider = provider or os.getenv("AI_PROVIDER", os.getenv("LLM_PROVIDER", "deepseek"))
        preset = PROVIDER_CONFIGS.get(provider, {})
        return cls(
            provider=provider,
            api_url=preset.get("api_url", ""),
            model=preset.get("model", ""),
        )


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system / user / assistant
    content: str


# ---------------------------------------------------------------------------
# 基类
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# DeepSeek 客户端
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# OpenAI 客户端
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 智谱AI (GLM-4) 客户端
# ---------------------------------------------------------------------------

class ZhipuClient(BaseLLMClient):
    """智谱AI (GLM-4) API客户端

    兼容 OpenAI 接口规范，base_url: https://open.bigmodel.cn/api/paas/v4
    支持 glm-4、glm-4-plus、glm-4-flash 等模型。
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.config.api_url = config.api_url or "https://open.bigmodel.cn/api/paas/v4"
        self.config.model = config.model or "glm-4"
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


# ---------------------------------------------------------------------------
# 通义千问 (DashScope) 客户端
# ---------------------------------------------------------------------------

class DashScopeClient(BaseLLMClient):
    """通义千问 (DashScope) API客户端

    通过 DashScope 兼容模式调用，接口规范与 OpenAI 一致。
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    支持 qwen-turbo、qwen-plus、qwen-max 等模型。
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.config.api_url = config.api_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.config.model = config.model or "qwen-plus"
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


# ---------------------------------------------------------------------------
# 工厂
# ---------------------------------------------------------------------------

class LLMClientFactory:
    """LLM客户端工厂"""

    # 提供商名称 -> 客户端类 映射
    _CLIENT_MAP: Dict[str, type] = {
        "deepseek": DeepSeekClient,
        "openai": OpenAIClient,
        "zhipu": ZhipuClient,
        "dashscope": DashScopeClient,
    }

    @staticmethod
    def create(config: LLMConfig) -> BaseLLMClient:
        """创建LLM客户端"""
        client_cls = LLMClientFactory._CLIENT_MAP.get(config.provider)
        if client_cls is None:
            supported = ", ".join(sorted(LLMClientFactory._CLIENT_MAP.keys()))
            raise ValueError(
                f"不支持的LLM提供商: {config.provider}，"
                f"当前支持: {supported}"
            )
        return client_cls(config)

    @staticmethod
    def supported_providers() -> List[str]:
        """返回所有支持的提供商名称"""
        return sorted(LLMClientFactory._CLIENT_MAP.keys())


# ---------------------------------------------------------------------------
# LLM 服务封装
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 便捷函数
# ---------------------------------------------------------------------------

def create_llm_service(
    api_key: str = "",
    provider: str = "",
    model: str = "",
    **kwargs
) -> LLMService:
    """创建LLM服务的便捷函数

    优先级：
    1. 显式传入的参数
    2. 环境变量 (AI_PROVIDER / LLM_PROVIDER)
    3. 默认值 (deepseek)
    """
    provider = provider or os.getenv("AI_PROVIDER", os.getenv("LLM_PROVIDER", "deepseek"))
    config = LLMConfig.from_env(provider)
    # 显式参数覆盖环境变量
    if api_key:
        config.api_key = api_key
    if model:
        config.model = model
    for k, v in kwargs.items():
        if hasattr(config, k):
            setattr(config, k, v)
    return LLMService(config)


# ---------------------------------------------------------------------------
# 测试代码
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    async def test_llm():
        # 测试从环境变量自动加载
        provider = os.getenv("AI_PROVIDER", os.getenv("LLM_PROVIDER", "deepseek"))
        print(f"当前提供商: {provider}")
        print(f"支持的提供商: {LLMClientFactory.supported_providers()}")

        service = create_llm_service()

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
