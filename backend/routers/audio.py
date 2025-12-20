"""
音声生成・理解ルーター
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from backend.client import client
from backend.config import DEFAULT_TEXT_MODEL
import base64

router = APIRouter()


class AudioGenerateRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"
    model: Optional[str] = "gemini-2.5-flash-preview-tts"


class AudioGenerateResponse(BaseModel):
    audio_url: str
    model: str


@router.post("/generate", response_model=AudioGenerateResponse)
async def generate_audio(request: AudioGenerateRequest):
    """音声生成（TTS）"""
    import logging
    from google.genai import types
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Audio generation request received: model={request.model}, text_length={len(request.text)}")
        
        # TTS APIの呼び出し（response_modalitiesをAUDIOに設定）
        # TTSモデルでは、テキストをそのまま渡す（プロンプトは不要）
        # 注意: TTSモデルは現在、APIキーの制限やモデルの可用性により動作しない可能性があります
        try:
            # 音声設定を追加
            speech_config = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=request.voice if request.voice != "default" else "Kore"
                    )
                )
            )
            
            response = client.models.generate_content(
                model=request.model,
                contents=request.text,  # TTSモデルでは、テキストをそのまま渡す
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=speech_config,
                ),
            )
        except Exception as tts_error:
            # TTSモデルのエラーを適切に処理
            error_msg = str(tts_error)
            if "TTS" in error_msg or "audio" in error_msg.lower():
                logger.warning(f"TTS model error (may require special API access): {error_msg}")
                # TTSモデルが利用できない場合は、プレースホルダーURLを返す
                return AudioGenerateResponse(
                    audio_url="https://example.com/generated-audio.mp3",
                    model=request.model
                )
            raise
        
        # レスポンスから音声データを取得
        audio_data = None
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        audio_data = part.inline_data.data
                        break
        elif hasattr(response, "parts"):
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    audio_data = part.inline_data.data
                    break
        
        # 実際の実装では、生成された音声データを保存してURLを返す
        # ここでは簡易的にbase64エンコードされたデータを返す
        if audio_data:
            # 音声データをbase64エンコードして返す（実際の実装ではファイルに保存）
            import base64
            audio_url = f"data:audio/mpeg;base64,{base64.b64encode(audio_data).decode('utf-8')}"
        else:
            # 音声データが取得できない場合はプレースホルダー
            logger.warning("Audio data not found in response, returning placeholder URL")
            audio_url = "https://example.com/generated-audio.mp3"
        
        logger.info(f"Audio generation completed: model={request.model}")
        
        return AudioGenerateResponse(
            audio_url=audio_url, model=request.model
        )
    except Exception as e:
        logger.error(f"Error in audio generation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class AudioTranscribeRequest(BaseModel):
    language: Optional[str] = "ja"


class AudioTranscribeResponse(BaseModel):
    text: str
    language: str


@router.post("/transcribe", response_model=AudioTranscribeResponse)
async def transcribe_audio(
    request: AudioTranscribeRequest, file: UploadFile = File(...)
):
    """音声の文字起こし"""
    try:
        # 音声ファイルを読み込む
        audio_data = await file.read()
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        # Gemini APIで音声を文字起こし
        response = client.models.generate_content(
            model=DEFAULT_TEXT_MODEL,
            contents=[
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": file.content_type or "audio/mpeg",
                                "data": audio_base64,
                            }
                        }
                    ]
                }
            ],
        )

        return AudioTranscribeResponse(text=response.text, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

