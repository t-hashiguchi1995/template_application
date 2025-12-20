"""
画像生成・理解ルーター
Nano Banana機能を実装
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import Optional, List, Literal
from backend.client import client
from backend.config import DEFAULT_IMAGE_MODEL, DEFAULT_TEXT_MODEL, DEFAULT_ANALYSIS_MODEL, DEFAULT_IMAGE_ANALYSIS_MODEL
import base64
from google.genai import types

router = APIRouter()

# アスペクト比の選択肢
ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
# 解像度の選択肢
RESOLUTIONS = ["1K", "2K", "4K"]


class ImageGenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = DEFAULT_IMAGE_MODEL
    aspect_ratio: Optional[Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]] = None
    resolution: Optional[Literal["1K", "2K", "4K"]] = None


class ImageGenerateResponse(BaseModel):
    image_url: str
    model: str
    aspect_ratio: Optional[str] = None
    resolution: Optional[str] = None


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(request: ImageGenerateRequest):
    """画像生成（Nano Banana）
    
    高解像度・アスペクト比指定に対応
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Image generation request received: model={request.model}, prompt_length={len(request.prompt)}, aspect_ratio={request.aspect_ratio}, resolution={request.resolution}")
        
        # Nano Bananaモデルを使用して画像を生成
        # 仕様: https://ai.google.dev/gemini-api/docs/nanobanana
        # サポートされているモデル: gemini-2.5-flash-image, gemini-3-pro-image-preview
        model = request.model
        
        # サポートされていないモデルをチェック
        if model.startswith("imagen") or model == "imagen-4.0":
            raise HTTPException(
                status_code=400,
                detail=f"画像生成モデル '{request.model}' は現在サポートされていません。Nano Bananaモデル（gemini-2.5-flash-image または gemini-3-pro-image-preview）を使用してください。"
            )
        
        # デフォルトモデルをNano Bananaに設定（空文字列や無効な値の場合）
        if not model or not model.startswith("gemini"):
            model = "gemini-2.5-flash-image"
            logger.info(f"Model not specified or invalid, using default: {model}")
        
        # 有効なNano Bananaモデルかチェック
        valid_models = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
        if model not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"無効なモデル '{model}' が指定されました。有効なモデル: {', '.join(valid_models)}"
            )
        
        # 画像生成設定（解像度・アスペクト比）
        config = None
        if request.aspect_ratio or request.resolution:
            image_config = types.ImageConfig()
            if request.aspect_ratio:
                image_config.aspect_ratio = request.aspect_ratio
            if request.resolution:
                image_config.image_size = request.resolution
            config = types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=image_config
            )
        
        # 画像生成APIを呼び出し
        if config:
            response = client.models.generate_content(
                model=model,
                contents=request.prompt,
                config=config,
            )
        else:
            response = client.models.generate_content(
                model=model,
                contents=request.prompt,
            )
        
        # レスポンスから画像データを取得
        # 仕様によると、partsにinline_dataが含まれる
        # 複数のpartがある場合、画像データを含むpartを探す
        image_data = None
        mime_type = "image/png"
        
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        image_data = part.inline_data.data
                        if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
                        # 画像データが見つかったら続行（複数の画像が返される可能性があるため、最後のものを使用）
        elif hasattr(response, "parts"):
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data = part.inline_data.data
                    if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
        
        if image_data:
            # base64エンコードされた画像データをdata URLとして返す
            import base64
            # image_dataはbytes型なので、base64エンコードする
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            elif isinstance(image_data, str):
                # 既にbase64エンコードされている場合
                image_base64 = image_data
            else:
                raise ValueError(f"Unexpected image_data type: {type(image_data)}")
            
            image_url = f"data:{mime_type};base64,{image_base64}"
            
            logger.info(f"Image generated successfully: model={model}, size={len(image_data) if isinstance(image_data, bytes) else len(image_base64)} bytes")
            return ImageGenerateResponse(
                image_url=image_url,
                model=model,
                aspect_ratio=request.aspect_ratio,
                resolution=request.resolution
            )
        else:
            logger.warning(f"No image data found in response, returning placeholder")
            return ImageGenerateResponse(
                image_url="https://example.com/generated-image.png",
                model=model
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image generation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class ImageAnalyzeRequest(BaseModel):
    prompt: str
    model: Optional[str] = DEFAULT_ANALYSIS_MODEL


class ImageAnalyzeResponse(BaseModel):
    analysis: str
    model: str


@router.post("/analyze", response_model=ImageAnalyzeResponse)
async def analyze_image(
    request: ImageAnalyzeRequest, file: UploadFile = File(...)
):
    """画像の理解・分析"""
    try:
        # 画像を読み込む
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # Gemini APIで画像を分析
        response = client.models.generate_content(
            model=request.model,
            contents=[
                {
                    "parts": [
                        {"text": request.prompt},
                        {
                            "inline_data": {
                                "mime_type": file.content_type or "image/jpeg",
                                "data": image_base64,
                            }
                        },
                    ]
                }
            ],
        )

        return ImageAnalyzeResponse(analysis=response.text, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ImageEditResponse(BaseModel):
    image_url: str
    model: str
    aspect_ratio: Optional[str] = None
    resolution: Optional[str] = None


@router.post("/edit", response_model=ImageEditResponse)
async def edit_image(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    model: Optional[str] = Form(DEFAULT_IMAGE_MODEL),
    aspect_ratio: Optional[str] = Form(None),
    resolution: Optional[str] = Form(None)
):
    """画像編集（テキストと画像による画像変換）
    
    画像を提供し、テキストプロンプトで要素の追加、削除、変更、スタイルの変更を行います。
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Image edit request received: model={model}, prompt_length={len(prompt)}")
        
        # 画像を読み込む
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # デフォルトモデルをNano Bananaに設定
        model_name = model
        if model_name == "imagen-4.0" or not model_name.startswith("gemini"):
            model_name = "gemini-3-pro-image-preview"  # 編集にはProモデルを推奨
        
        # 画像編集設定
        config = None
        if aspect_ratio or resolution:
            image_config = types.ImageConfig()
            if aspect_ratio:
                image_config.aspect_ratio = aspect_ratio
            if resolution:
                image_config.image_size = resolution
            config = types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=image_config
            )
        
        # 画像編集APIを呼び出し
        contents = [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": file.content_type or "image/jpeg",
                            "data": image_base64,
                        }
                    },
                ]
            }
        ]
        
        if config:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
        else:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
        
        # レスポンスから画像データを取得
        image_data_result = None
        mime_type = "image/png"
        
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        image_data_result = part.inline_data.data
                        if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
        elif hasattr(response, "parts"):
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data_result = part.inline_data.data
                    if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
        
        if image_data_result:
            if isinstance(image_data_result, bytes):
                image_base64_result = base64.b64encode(image_data_result).decode('utf-8')
            elif isinstance(image_data_result, str):
                image_base64_result = image_data_result
            else:
                raise ValueError(f"Unexpected image_data type: {type(image_data_result)}")
            
            image_url = f"data:{mime_type};base64,{image_base64_result}"
            
            logger.info(f"Image edited successfully: model={model_name}")
            return ImageEditResponse(
                image_url=image_url,
                model=model_name,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
        else:
            raise HTTPException(status_code=500, detail="画像データが取得できませんでした")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image editing: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class ImageComposeResponse(BaseModel):
    image_url: str
    model: str
    aspect_ratio: Optional[str] = None
    resolution: Optional[str] = None


@router.post("/compose", response_model=ImageComposeResponse)
async def compose_images(
    files: List[UploadFile] = File(...),
    prompt: str = Form(...),
    model: Optional[str] = Form(DEFAULT_IMAGE_MODEL),
    aspect_ratio: Optional[str] = Form(None),
    resolution: Optional[str] = Form(None)
):
    """複数画像の合成
    
    複数の入力画像を使用して新しいシーンを構成し、スタイルを転送します。
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Image compose request received: model={model}, num_images={len(files)}")
        
        # デフォルトモデルをNano Bananaに設定
        model_name = model
        if model_name == "imagen-4.0" or not model_name.startswith("gemini"):
            model_name = "gemini-3-pro-image-preview"  # 合成にはProモデルを推奨
        
        # 複数の画像を読み込む
        parts = [{"text": prompt}]
        for file in files:
            image_data = await file.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": file.content_type or "image/jpeg",
                    "data": image_base64,
                }
            })
        
        # 画像合成設定
        config = None
        if aspect_ratio or resolution:
            image_config = types.ImageConfig()
            if aspect_ratio:
                image_config.aspect_ratio = aspect_ratio
            if resolution:
                image_config.image_size = resolution
            config = types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=image_config
            )
        
        # 画像合成APIを呼び出し
        contents = [{"parts": parts}]
        
        if config:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
        else:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
        
        # レスポンスから画像データを取得
        image_data_result = None
        mime_type = "image/png"
        
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        image_data_result = part.inline_data.data
                        if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
        elif hasattr(response, "parts"):
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data_result = part.inline_data.data
                    if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
        
        if image_data_result:
            if isinstance(image_data_result, bytes):
                image_base64_result = base64.b64encode(image_data_result).decode('utf-8')
            elif isinstance(image_data_result, str):
                image_base64_result = image_data_result
            else:
                raise ValueError(f"Unexpected image_data type: {type(image_data_result)}")
            
            image_url = f"data:{mime_type};base64,{image_base64_result}"
            
            logger.info(f"Images composed successfully: model={model_name}")
            return ImageComposeResponse(
                image_url=image_url,
                model=model_name,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
        else:
            raise HTTPException(status_code=500, detail="画像データが取得できませんでした")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image composition: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class MultiTurnImageChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gemini-3-pro-image-preview"
    aspect_ratio: Optional[Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]] = None
    resolution: Optional[Literal["1K", "2K", "4K"]] = None
    session_id: Optional[str] = None  # セッション管理用（簡易実装）


class MultiTurnImageChatResponse(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None
    model: str
    session_id: str


# 簡易的なセッション管理（本番環境ではRedis等を使用）
_chat_sessions: dict = {}


@router.post("/chat", response_model=MultiTurnImageChatResponse)
async def multi_turn_image_chat(request: MultiTurnImageChatRequest):
    """マルチターンの画像編集（チャット形式）
    
    会話形式で画像の生成と編集を続けます。
    """
    import logging
    import uuid
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Multi-turn image chat request received: model={request.model}, session_id={request.session_id}")
        
        # セッション管理
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in _chat_sessions:
            # 新しいチャットセッションを作成
            config = types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
            )
            if request.aspect_ratio or request.resolution:
                image_config = types.ImageConfig()
                if request.aspect_ratio:
                    image_config.aspect_ratio = request.aspect_ratio
                if request.resolution:
                    image_config.image_size = request.resolution
                config.image_config = image_config
            
            chat = client.chats.create(
                model=request.model or "gemini-3-pro-image-preview",
                config=config
            )
            _chat_sessions[session_id] = chat
        else:
            chat = _chat_sessions[session_id]
        
        # メッセージを送信
        config = None
        if request.aspect_ratio or request.resolution:
            image_config = types.ImageConfig()
            if request.aspect_ratio:
                image_config.aspect_ratio = request.aspect_ratio
            if request.resolution:
                image_config.image_size = request.resolution
            config = types.GenerateContentConfig(
                image_config=image_config
            )
        
        if config:
            response = chat.send_message(request.message, config=config)
        else:
            response = chat.send_message(request.message)
        
        # レスポンスからテキストと画像を取得
        text_result = None
        image_url_result = None
        mime_type = "image/png"
        
        if hasattr(response, "parts"):
            for part in response.parts:
                if hasattr(part, "text") and part.text:
                    text_result = part.text
                elif hasattr(part, "inline_data") and part.inline_data:
                    image_data = part.inline_data.data
                    if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    
                    if isinstance(image_data, bytes):
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                    elif isinstance(image_data, str):
                        image_base64 = image_data
                    else:
                        continue
                    
                    image_url_result = f"data:{mime_type};base64,{image_base64}"
        
        logger.info(f"Multi-turn chat response: session_id={session_id}, has_text={text_result is not None}, has_image={image_url_result is not None}")
        
        return MultiTurnImageChatResponse(
            text=text_result,
            image_url=image_url_result,
            model=request.model or "gemini-3-pro-image-preview",
            session_id=session_id
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multi-turn image chat: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

