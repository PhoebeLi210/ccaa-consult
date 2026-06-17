#!/usr/bin/env python3
"""
语音识别API
支持多种后端：Groq Whisper、本地Whisper、浏览器Web Speech API
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import base64
import io

from app.core.config import settings
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/speech", tags=["语音识别"])


class SpeechRecognizeRequest(BaseModel):
    """语音识别请求"""
    audio_base64: str
    language: str = "zh"
    format: str = "webm"


class SpeechRecognizeResponse(BaseModel):
    """语音识别响应"""
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None


@router.post("/recognize", response_model=SpeechRecognizeResponse, summary="语音识别")
async def recognize_speech(request: SpeechRecognizeRequest):
    """
    将音频转换为文字
    
    支持多种后端：
    1. Groq Whisper API (需要 GROQ_API_KEY)
    2. 本地 Whisper (需要安装 whisper)
    3. 返回错误提示用户使用其他方式
    """
    audio_bytes = base64.b64decode(request.audio_base64)
    
    # 尝试1: Groq Whisper API
    if hasattr(settings, 'GROQ_API_KEY') and settings.GROQ_API_KEY:
        try:
            text = await _recognize_with_groq(audio_bytes, request.language)
            return SpeechRecognizeResponse(text=text, confidence=0.9, language=request.language)
        except Exception as e:
            print(f"Groq识别失败: {e}")
    
    # 尝试2: 本地 Whisper
    try:
        text = await _recognize_with_local_whisper(audio_bytes, request.language)
        return SpeechRecognizeResponse(text=text, confidence=0.85, language=request.language)
    except Exception as e:
        print(f"本地Whisper识别失败: {e}")
    
    # 尝试3: 返回提示
    raise HTTPException(
        status_code=503,
        detail="语音识别服务暂不可用，请配置 GROQ_API_KEY 或安装 openai-whisper"
    )


async def _recognize_with_groq(audio_bytes: bytes, language: str) -> str:
    """使用 Groq Whisper API 识别"""
    import httpx
    
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
    }
    
    # Groq API endpoint
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    files = {
        "file": ("audio.webm", io.BytesIO(audio_bytes), "audio/webm"),
    }
    data = {
        "model": "whisper-large-v3",
        "language": language,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")


async def _recognize_with_local_whisper(audio_bytes: bytes, language: str) -> str:
    """使用本地 Whisper 识别"""
    try:
        import whisper
        import tempfile
        import os
        
        # 保存音频到临时文件
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            # 加载模型（base模型，约140MB，准确率更高）
            model = whisper.load_model("base")
            result = model.transcribe(temp_path, language=language)
            return result.get("text", "")
        finally:
            os.unlink(temp_path)
    except ImportError:
        raise Exception("whisper not installed")


@router.get("/status", summary="获取语音识别服务状态")
async def get_speech_status():
    """获取语音识别服务可用状态"""
    status = {
        "groq_available": bool(getattr(settings, 'GROQ_API_KEY', None)),
        "local_whisper_available": False,
    }
    
    try:
        import whisper
        status["local_whisper_available"] = True
    except ImportError:
        pass
    
    return status
