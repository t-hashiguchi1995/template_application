"""
構造化出力ルーター
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from google.genai import types
from backend.client import client
from backend.config import DEFAULT_TEXT_MODEL

router = APIRouter()


class StructuredOutputRequest(BaseModel):
    prompt: str
    schema: Dict[str, Any]  # JSON Schema
    model: Optional[str] = "gemini-2.5-flash"  # 構造化出力に対応したモデル


class StructuredOutputResponse(BaseModel):
    data: Dict[str, Any]
    model: str


@router.post("/generate", response_model=StructuredOutputResponse)
async def generate_structured_output(request: StructuredOutputRequest):
    """構造化出力（JSON形式）"""
    import logging
    import json
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Structured output request received: model={request.model}, prompt_length={len(request.prompt)}")
        
        # 構造化出力の設定
        # 仕様: https://ai.google.dev/gemini-api/docs/gemini-3
        # response_mime_typeとresponse_json_schemaを使用
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=request.schema,  # JSON Schemaを直接渡す
        )
        
        response = client.models.generate_content(
            model=request.model,
            contents=request.prompt,
            config=config,
        )

        # response.textまたはresponse.parsedを使用
        if hasattr(response, "parsed") and response.parsed:
            data = response.parsed
        elif hasattr(response, "text") and response.text:
            data = json.loads(response.text)
        else:
            raise ValueError("No valid response data found")
        
        logger.info(f"Structured output generated: model={request.model}")
        
        return StructuredOutputResponse(data=data, model=request.model)
    except Exception as e:
        logger.error(f"Error in structured output generation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

