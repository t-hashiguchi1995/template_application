"""
関数呼び出しルーター
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.client import client
from backend.config import DEFAULT_TEXT_MODEL

router = APIRouter()


class FunctionParameter(BaseModel):
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class FunctionCallingRequest(BaseModel):
    prompt: str
    functions: List[FunctionDefinition]
    model: Optional[str] = DEFAULT_TEXT_MODEL


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class FunctionCallingResponse(BaseModel):
    function_calls: List[FunctionCall]
    text: Optional[str] = None
    model: str


@router.post("/call", response_model=FunctionCallingResponse)
async def call_functions(request: FunctionCallingRequest):
    """関数呼び出し"""
    import logging
    from google.genai import types
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Function calling request received: model={request.model}, function_count={len(request.functions)}")
        
        # 関数定義をGemini形式に変換
        function_declarations = []
        for func in request.functions:
            # JSON Schemaをそのまま使用（parameters_json_schemaとして）
            function_declaration = types.FunctionDeclaration(
                name=func.name,
                description=func.description,
                parameters_json_schema=func.parameters,
            )
            function_declarations.append(function_declaration)
        
        tool = types.Tool(function_declarations=function_declarations)
        
        response = client.models.generate_content(
            model=request.model,
            contents=request.prompt,
            config=types.GenerateContentConfig(tools=[tool]),
        )

        # 関数呼び出しを抽出
        function_calls = []
        if hasattr(response, "function_calls") and response.function_calls:
            for func_call in response.function_calls:
                # func_callはFunctionCallオブジェクト（nameとargs属性を持つ）
                if hasattr(func_call, "name"):
                    # argsはdictまたはFunctionCallArgsオブジェクトの可能性がある
                    args_dict = {}
                    if hasattr(func_call, "args"):
                        if isinstance(func_call.args, dict):
                            args_dict = func_call.args
                        elif hasattr(func_call.args, "model_dump"):
                            args_dict = func_call.args.model_dump()
                        elif hasattr(func_call.args, "__dict__"):
                            args_dict = func_call.args.__dict__
                    
                    function_calls.append(
                        FunctionCall(
                            name=func_call.name,
                            arguments=args_dict,
                        )
                    )
        elif response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call"):
                    fc = part.function_call
                    args_dict = {}
                    if hasattr(fc, "args"):
                        if isinstance(fc.args, dict):
                            args_dict = fc.args
                        elif hasattr(fc.args, "model_dump"):
                            args_dict = fc.args.model_dump()
                        elif hasattr(fc.args, "__dict__"):
                            args_dict = fc.args.__dict__
                    
                    function_calls.append(
                        FunctionCall(
                            name=fc.name if hasattr(fc, "name") else str(fc),
                            arguments=args_dict,
                        )
                    )

        logger.info(f"Function calling completed: function_calls_count={len(function_calls)}")
        
        return FunctionCallingResponse(
            function_calls=function_calls,
            text=response.text if not function_calls else None,
            model=request.model,
        )
    except Exception as e:
        logger.error(f"Error in function calling: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

