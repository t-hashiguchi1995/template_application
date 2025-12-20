"""
エンベディングルーター
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.client import client
from backend.config import DEFAULT_EMBEDDING_MODEL

router = APIRouter()


class EmbeddingRequest(BaseModel):
    text: str
    model: Optional[str] = DEFAULT_EMBEDDING_MODEL


class EmbeddingResponse(BaseModel):
    embedding: List[float]
    model: str
    dimensions: int


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """テキストエンベディング生成"""
    import logging
    from google.genai import types
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Embedding request received: model={request.model}, text_length={len(request.text)}")
        
        # エンベディングAPIの実装
        response = client.models.embed_content(
            model=request.model,
            contents=[request.text],
            config=types.EmbedContentConfig(),
        )
        
        # レスポンスの構造: response.embeddings[0].values
        if hasattr(response, "embeddings") and len(response.embeddings) > 0:
            embedding = response.embeddings[0].values
        elif hasattr(response, "embedding"):
            embedding = response.embedding.values if hasattr(response.embedding, "values") else response.embedding
        elif hasattr(response, "values"):
            embedding = response.values
        else:
            embedding = []
        
        if not embedding:
            raise ValueError("Embedding values not found in response")
        
        logger.info(f"Embedding generated: dimensions={len(embedding)}")
        
        return EmbeddingResponse(
            embedding=embedding,
            model=request.model,
            dimensions=len(embedding),
        )
    except Exception as e:
        logger.error(f"Error in embedding generation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class BatchEmbeddingRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = DEFAULT_EMBEDDING_MODEL


class BatchEmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    dimensions: int


@router.post("/batch", response_model=BatchEmbeddingResponse)
async def generate_batch_embeddings(request: BatchEmbeddingRequest):
    """バッチエンベディング生成"""
    import logging
    from google.genai import types
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Batch embedding request received: model={request.model}, text_count={len(request.texts)}")
        
        # バッチエンベディングは複数のテキストを一度に処理
        response = client.models.embed_content(
            model=request.model,
            contents=request.texts,
            config=types.EmbedContentConfig(),
        )
        
        embeddings = []
        # レスポンスの構造: response.embeddings は ContentEmbedding のリスト
        if hasattr(response, "embeddings"):
            for content_embedding in response.embeddings:
                if hasattr(content_embedding, "values"):
                    embeddings.append(content_embedding.values)
                else:
                    embeddings.append([])
        elif isinstance(response, list):
            for item in response:
                if hasattr(item, "values"):
                    embeddings.append(item.values)
                else:
                    embeddings.append([])
        else:
            # 単一のレスポンスの場合
            if hasattr(response, "values"):
                embeddings.append(response.values)
            else:
                embeddings.append([])

        dimensions = len(embeddings[0]) if embeddings else 0
        logger.info(f"Batch embeddings generated: count={len(embeddings)}, dimensions={dimensions}")
        
        return BatchEmbeddingResponse(
            embeddings=embeddings,
            model=request.model,
            dimensions=dimensions,
        )
    except Exception as e:
        logger.error(f"Error in batch embedding generation: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

