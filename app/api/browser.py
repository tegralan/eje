from fastapi import APIRouter, HTTPException
import logging

from app.core.eje_browser import get_browser, shutdown_browser
from app.core.config import settings
from app.models.schemas import SessionInfo

router = APIRouter(prefix="/api/browser", tags=["browser"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=SessionInfo)
async def login(usuario: str = None, password: str = None):
    """Autentica en EJE CLOUD con las credenciales configuradas o las proporcionadas."""
    try:
        browser = await get_browser()
        success = await browser.login(usuario, password)
        return SessionInfo(
            session_id="browser-session",
            autenticado=success,
            usuario=usuario or settings.eje_cloud_user,
            modulo_activo="inicio",
        )
    except Exception as e:
        logger.error(f"Error de login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=SessionInfo)
async def browser_status():
    """Obtiene el estado actual del navegador."""
    try:
        browser = await get_browser()
        return SessionInfo(
            session_id="browser-session",
            autenticado=browser.is_authenticated,
            modulo_activo=browser.current_url,
        )
    except Exception as e:
        return SessionInfo(
            session_id="browser-session",
            autenticado=False,
        )


@router.post("/stop")
async def stop_browser():
    """Cierra el navegador."""
    await shutdown_browser()
    return {"message": "Navegador cerrado correctamente"}


@router.post("/screenshot")
async def take_screenshot():
    """Captura la pantalla actual del navegador."""
    try:
        browser = await get_browser()
        path = await browser.take_screenshot()
        return {"screenshot_path": path, "message": "Captura realizada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
