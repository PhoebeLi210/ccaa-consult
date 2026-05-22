#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鏅鸿川閫毬峰挩璇㈢増 - 涓诲叆鍙?

FastAPI搴旂敤鍏ュ彛
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import templates, generator, company, materials, projects, parse, auth, analyzer, uploads, conversation, flowcharts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """搴旂敤鐢熷懡鍛ㄦ湡"""
    # 鍚姩鏃跺垵濮嬪寲鏁版嵁搴?
    print("鏅鸿川閫毬峰挩璇㈢増 鍚姩涓?..")
    print("鍒濆鍖栨暟鎹簱...")
    init_db()
    print("鏁版嵁搴撳垵濮嬪寲瀹屾垚")
    yield
    # 鍏抽棴鏃?
    print("鏅鸿川閫毬峰挩璇㈢増 鍏抽棴涓?..")


app = FastAPI(
    title="鏅鸿川閫毬峰挩璇㈢増 API",
    description="闈㈠悜ISO鍜ㄨ椤鹃棶鐨凙I鏅鸿兘鏂囦功宸ヤ綔绔?,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS閰嶇疆
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 娉ㄥ唽璺敱
app.include_router(templates.router, prefix="/api/v1")
app.include_router(generator.router, prefix="/api/v1")
app.include_router(company.router, prefix="/api/v1")
app.include_router(materials.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(parse.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(analyzer.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(conversation.router, prefix="/api/v1")
app.include_router(flowcharts.router, prefix="/api/v1")


@app.get("/")
async def root():
    """鏍硅矾寰?""
    return {
        "name": "鏅鸿川閫毬峰挩璇㈢増",
        "version": "1.0.0",
        "description": "闈㈠悜ISO鍜ㄨ椤鹃棶鐨凙I鏅鸿兘鏂囦功宸ヤ綔绔?,
        "endpoints": {
            "auth": "/api/v1/auth - 鐢ㄦ埛璁よ瘉锛堟敞鍐?鐧诲綍锛?,
            "projects": "/api/v1/projects - 椤圭洰绠＄悊",
            "generator": "/api/v1/generator - 鏂囨。鐢熸垚涓庡鍑?,
            "templates": "/api/v1/templates - 妯℃澘绠＄悊",
            "materials": "/api/v1/materials - 鏉愭枡绠＄悊",
            "parse": "/api/v1/parse - 鑷劧璇█瑙ｆ瀽",
            "analyzer": "/api/v1/analyzer - 缂哄け椤瑰垎鏋?,
            "uploads": "/api/v1/uploads - 鏂囦欢涓婁紶涓嶦xcel瑙ｆ瀽",
            "company": "/api/v1/company - 浼佷笟绠＄悊",
        },
        "features": [
            "JWT鐢ㄦ埛璁よ瘉",
            "鏁版嵁搴撴寔涔呭寲锛圫QLite锛?,
            "LLM鑷劧璇█瑙ｆ瀽锛圖eepSeek锛?,
            "AI鎵╁啓鎻忚堪鎬у唴瀹?,
            "琛屼笟妯℃澘鑷姩鍖归厤锛?涓涓氾級",
            "鏂囨。瀵煎嚭涓?docx/ZIP",
            "Excel鏀堕泦琛ㄤ笂浼犺В鏋?,
            "ISO鏉℃瑕嗙洊妫€鏌?,
        ]
    }


@app.get("/health")
async def health():
    """鍋ュ悍妫€鏌?""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

