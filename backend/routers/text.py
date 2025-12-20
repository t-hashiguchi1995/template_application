"""
テキスト生成ルーター
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.client import client
from backend.config import DEFAULT_TEXT_MODEL, DEFAULT_CHAT_MODEL

router = APIRouter()


class TextGenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = DEFAULT_TEXT_MODEL
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


class TextGenerateResponse(BaseModel):
    text: str
    model: str


@router.post("/generate", response_model=TextGenerateResponse)
async def generate_text(request: TextGenerateRequest):
    """テキスト生成"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Text generation request received: model={request.model}, prompt_length={len(request.prompt)}")
        
        config = {}
        if request.temperature is not None:
            config["temperature"] = request.temperature
        if request.max_tokens is not None:
            config["max_output_tokens"] = request.max_tokens

        logger.info(f"Calling Gemini API with config: {config}")
        response = client.models.generate_content(
            model=request.model,
            contents=request.prompt,
            config=config if config else None,
        )
        
        logger.info(f"Gemini API response received: response_length={len(response.text) if response.text else 0}")
        return TextGenerateResponse(text=response.text, model=request.model)
    except Exception as e:
        logger.error(f"Error in text generation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = DEFAULT_CHAT_MODEL
    temperature: Optional[float] = 0.7


class ChatResponse(BaseModel):
    message: str
    model: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """チャット形式のテキスト生成"""
    try:
        # メッセージをGemini形式に変換
        contents = []
        for msg in request.messages:
            if msg.role == "user":
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == "assistant":
                contents.append(
                    {"role": "model", "parts": [{"text": msg.content}]}
                )

        response = client.models.generate_content(
            model=request.model,
            contents=contents,
            config={"temperature": request.temperature},
        )
        return ChatResponse(message=response.text, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

