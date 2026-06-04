from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_service import process_chat, clear_session

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint principal de chat con EJE CLOUD IA."""
    try:
        response = await process_chat(
            message=request.message,
            session_id=request.session_id,
            use_browser=True,
        )
        return response
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def clear_chat_session(session_id: str):
    """Limpia el historial de una sesión de chat."""
    clear_session(session_id)
    return {"message": "Sesión limpiada correctamente", "session_id": session_id}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "EJE CLOUD IA"}
