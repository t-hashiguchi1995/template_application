"""
FastAPI メインアプリケーション
Gemini APIの各種機能を提供するエンドポイント
"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.routers import (
    text,
    image,
    video,
    audio,
    embedding,
    function_calling,
    structured_output,
    document,
    agent,
)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gemini API Backend",
    description="Gemini APIの各種機能を提供するバックエンドAPI",
    version="0.1.0",
)

# リクエストログミドルウェア
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(text.router, prefix="/api/text", tags=["text"])
app.include_router(image.router, prefix="/api/image", tags=["image"])
app.include_router(video.router, prefix="/api/video", tags=["video"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(embedding.router, prefix="/api/embedding", tags=["embedding"])
app.include_router(
    function_calling.router, prefix="/api/function-calling", tags=["function-calling"]
)
app.include_router(
    structured_output.router,
    prefix="/api/structured-output",
    tags=["structured-output"],
)
app.include_router(document.router, prefix="/api/document", tags=["document"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])


@app.get("/")
async def root():
    return {"message": "Gemini API Backend", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

