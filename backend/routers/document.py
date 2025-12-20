"""
ドキュメント理解ルーター
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from backend.client import client
from backend.config import DEFAULT_TEXT_MODEL, DEFAULT_ANALYSIS_MODEL
import base64

router = APIRouter()


class DocumentAnalyzeRequest(BaseModel):
    prompt: str
    model: Optional[str] = DEFAULT_ANALYSIS_MODEL


class DocumentAnalyzeResponse(BaseModel):
    analysis: str
    model: str
    page_count: Optional[int] = None


@router.post("/analyze", response_model=DocumentAnalyzeResponse)
async def analyze_document(
    request: DocumentAnalyzeRequest, file: UploadFile = File(...)
):
    """ドキュメント（PDF等）の理解・分析"""
    try:
        # ドキュメントを読み込む
        document_data = await file.read()
        document_base64 = base64.b64encode(document_data).decode("utf-8")

        # MIMEタイプの判定
        mime_type = file.content_type or "application/pdf"
        if file.filename:
            if file.filename.endswith(".pdf"):
                mime_type = "application/pdf"
            elif file.filename.endswith(".docx"):
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif file.filename.endswith(".txt"):
                mime_type = "text/plain"

        # Gemini APIでドキュメントを分析
        response = client.models.generate_content(
            model=request.model,
            contents=[
                {
                    "parts": [
                        {"text": request.prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": document_base64,
                            }
                        },
                    ]
                }
            ],
        )

        return DocumentAnalyzeResponse(
            analysis=response.text, model=request.model, page_count=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

