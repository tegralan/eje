"""
Servicio principal de IA que orquesta las conversaciones y acciones.
"""
import uuid
import logging
from typing import Optional

from app.core.ai_client import chat_with_gemini
from app.core.eje_browser import get_browser
from app.services.document_service import DocumentService
from app.models.schemas import ChatResponse

logger = logging.getLogger(__name__)

document_service = DocumentService()

# Almacenamiento de sesiones en memoria (en producción usar Redis)
_sessions: dict = {}


def get_or_create_session(session_id: Optional[str] = None) -> str:
    sid = session_id or str(uuid.uuid4())
    if sid not in _sessions:
        _sessions[sid] = {"history": [], "browser_connected": False}
    return sid


async def process_chat(
    message: str,
    session_id: Optional[str] = None,
    use_browser: bool = True,
) -> ChatResponse:
    """Procesa un mensaje de chat con soporte opcional de navegador."""
    sid = get_or_create_session(session_id)
    session = _sessions[sid]
    history = session.get("history", [])

    browser = None
    if use_browser:
        try:
            browser = await get_browser()
        except Exception as e:
            logger.warning(f"No se pudo iniciar el navegador: {e}")

    response_text, actions = await chat_with_gemini(
        message=message,
        history=history,
        browser=browser,
        document_service=document_service,
    )

    # Actualiza el historial de la sesión
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response_text})

    # Limita el historial a las últimas 20 interacciones para no sobrecargar el contexto
    if len(history) > 40:
        history = history[-40:]
    session["history"] = history

    return ChatResponse(
        response=response_text,
        session_id=sid,
        actions_taken=actions,
    )


def clear_session(session_id: str):
    """Limpia el historial de una sesión."""
    if session_id in _sessions:
        _sessions[session_id]["history"] = []
