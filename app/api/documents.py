from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import logging

from app.models.schemas import DocumentRequest, DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/documentos", tags=["documentos"])
logger = logging.getLogger(__name__)
doc_service = DocumentService()


@router.post("", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest):
    """Genera un documento oficial del GCBA."""
    try:
        html = await doc_service.generate(
            tipo=request.tipo.value,
            asunto=request.asunto,
            contenido=request.contenido,
            destinatario=request.destinatario,
            datos_adicionales=request.datos_adicionales,
        )
        return DocumentResponse(
            documento=html,
            tipo=request.tipo,
            formato="html",
        )
    except Exception as e:
        logger.error(f"Error generando documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview", response_class=HTMLResponse)
async def preview_document(request: DocumentRequest):
    """Genera y retorna el HTML del documento para previsualización."""
    try:
        html = await doc_service.generate(
            tipo=request.tipo.value,
            asunto=request.asunto,
            contenido=request.contenido,
            destinatario=request.destinatario,
            datos_adicionales=request.datos_adicionales,
        )
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
