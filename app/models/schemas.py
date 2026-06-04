from pydantic import BaseModel
from typing import Optional, List, Any
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    actions_taken: List[str] = []


class DocumentType(str, Enum):
    informe = "informe"
    nota = "nota"
    resolucion = "resolucion"
    memo = "memo"
    dictamen = "dictamen"


class DocumentRequest(BaseModel):
    tipo: DocumentType
    asunto: str
    destinatario: str
    contenido: str
    datos_adicionales: Optional[dict] = None


class DocumentResponse(BaseModel):
    documento: str
    tipo: DocumentType
    formato: str = "html"


class SearchRequest(BaseModel):
    query: str
    filtros: Optional[dict] = None
    limite: int = 10


class SearchResult(BaseModel):
    titulo: str
    descripcion: str
    url: Optional[str] = None
    datos: Optional[dict] = None
    relevancia: float = 0.0


class SearchResponse(BaseModel):
    resultados: List[SearchResult]
    total: int
    query: str


class AnalysisRequest(BaseModel):
    consulta: str
    contexto: Optional[str] = None


class AnalysisResponse(BaseModel):
    analisis: str
    datos: Optional[Any] = None
    graficos: Optional[List[dict]] = None


class BrowserAction(BaseModel):
    accion: str
    parametros: dict = {}
    resultado: Optional[str] = None
    exitoso: bool = False


class SessionInfo(BaseModel):
    session_id: str
    autenticado: bool
    usuario: Optional[str] = None
    modulo_activo: Optional[str] = None
