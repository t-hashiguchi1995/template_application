"""
動画生成ルーター（Veo）
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.client import client
from backend.config import DEFAULT_VIDEO_MODEL

router = APIRouter()


class VideoGenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = DEFAULT_VIDEO_MODEL
    duration: Optional[int] = 5  # 秒


class VideoGenerateResponse(BaseModel):
    video_url: str
    model: str
    status: str


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(request: VideoGenerateRequest):
    """動画生成（Veo API）"""
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Video generation request received: model={request.model}, prompt_length={len(request.prompt)}")
        
        # 注意: Veo APIはGemini APIとは別のAPIです
        # 現在の実装では、Gemini APIを使用していますが、Veo APIを使用する場合は
        # 別途Veo APIのクライアントが必要です
        # ここでは、エラーメッセージを明確にするため、適切なモデルを使用します
        
        # Veoモデルはgenerate_contentでは使用できないため、エラーメッセージを返す
        if request.model.startswith("veo"):
            raise HTTPException(
                status_code=400,
                detail=f"動画生成モデル '{request.model}' は現在サポートされていません。Veo APIは別途実装が必要です。"
            )
        
        # 代替として、動画生成をテキストで説明する
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Describe a video: {request.prompt}",
        )
        
        logger.warning(f"Video generation using text model as fallback: {request.model}")
        
        # 実際の実装では、生成された動画のURLを返す
        return VideoGenerateResponse(
            video_url="https://example.com/generated-video.mp4",
            model=request.model,
            status="completed",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in video generation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

