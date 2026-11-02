import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import chat, documents, browser
from app.core.eje_browser import shutdown_browser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 EJE CLOUD IA iniciando...")
    yield
    logger.info("Cerrando EJE CLOUD IA...")
    await shutdown_browser()


app = FastAPI(
    title="EJE CLOUD IA",
    description="Asistente de Inteligencia Artificial para EJE CLOUD — Gobierno de la Ciudad de Buenos Aires",
    version="1.0.0",
    lifespan=lifespan,
)

# La aplicación se sirve localmente; no habilitar CORS para sitios arbitrarios.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(browser.router)

# Archivos estáticos del frontend
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "app": "EJE CLOUD IA",
            "version": "1.0.0",
            "docs": "/docs",
            "descripcion": "Asistente IA para EJE CLOUD — GCBA",
        }
