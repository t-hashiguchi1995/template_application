"""
エージェント・ツールルーター
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.client import client
from backend.config import DEFAULT_TEXT_MODEL, DEFAULT_ANALYSIS_MODEL

router = APIRouter()


class AgentRequest(BaseModel):
    prompt: str
    tools: Optional[List[str]] = None  # 使用するツールのリスト
    model: Optional[str] = DEFAULT_ANALYSIS_MODEL


class AgentResponse(BaseModel):
    response: str
    tools_used: List[str]
    model: str


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):
    """エージェントチャット（ツール使用可能）"""
    import logging
    from google.genai import types
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Agent chat request received: model={request.model}, tools={request.tools}")
        
        # 利用可能なツールを設定
        # 仕様: https://ai.google.dev/gemini-api/docs/gemini-3
        # 組み込みツールは {"google_search": {}} の形式で指定
        tools = []
        if request.tools:
            for tool_name in request.tools:
                if tool_name == "google_search":
                    tools.append({"google_search": {}})
                elif tool_name == "google_maps":
                    # 注意: Gemini 3ではGoogle Mapsはまだサポートされていない
                    logger.warning("Google Maps tool is not yet supported in Gemini 3")
                elif tool_name == "url_context":
                    tools.append({"url_context": {}})
                elif tool_name == "code_execution":
                    tools.append({"code_execution": {}})
                elif tool_name == "file_search":
                    tools.append({"file_search": {}})

        config = types.GenerateContentConfig(tools=tools) if tools else None
        
        response = client.models.generate_content(
            model=request.model,
            contents=request.prompt,
            config=config,
        )

        # 使用されたツールを抽出
        tools_used = []
        response_text = None
        
        # まず、candidatesからpartsを確認（組み込みツールはここに含まれる可能性がある）
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                text_parts = []
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        text_parts.append(part.text)
                    elif hasattr(part, "function_call") and part.function_call:
                        # 関数呼び出し部分はツール使用として記録
                        fc = part.function_call
                        if hasattr(fc, "name") and fc.name:
                            tools_used.append(fc.name)
                if text_parts:
                    response_text = " ".join(text_parts)
        
        # function_callsからも確認
        if hasattr(response, "function_calls") and response.function_calls:
            for func_call in response.function_calls:
                # func_callはFunctionCallオブジェクト（name属性を持つ）
                if hasattr(func_call, "name") and func_call.name:
                    if func_call.name not in tools_used:
                        tools_used.append(func_call.name)
        
        # 組み込みツールが自動実行された場合、function_callsが空になる可能性がある
        # この場合、リクエストで指定されたツールが実際に使用されたと判断
        # （レスポンスに検索結果が含まれている場合など）
        if not tools_used and request.tools:
            # レスポンステキストに検索結果が含まれているか確認
            # 組み込みツールが自動実行された場合、テキストに結果が含まれる
            if hasattr(response, "text") and response.text:
                response_text = response.text
                # リクエストで指定されたツールを記録
                # 注意: これは推測であり、実際にツールが使用されたかは保証されない
                # ただし、組み込みツールが自動実行された場合、function_callsが空になることがある
                tools_used = request.tools.copy()
        
        # テキストレスポンスを取得（まだ取得できていない場合）
        if not response_text:
            if hasattr(response, "text") and response.text:
                response_text = response.text
        
        # テキストが取得できない場合のデフォルト
        if not response_text:
            if tools_used:
                response_text = f"ツールを使用しました: {', '.join(tools_used)}"
            else:
                response_text = "レスポンスを生成しました。"

        logger.info(f"Agent chat completed: tools_used={tools_used}, model={request.model}")
        
        return AgentResponse(
            response=response_text, tools_used=tools_used, model=request.model
        )
    except Exception as e:
        logger.error(f"Error in agent chat: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

