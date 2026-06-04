#!/bin/bash
# Script de inicio de EJE CLOUD IA

set -e

echo "=================================================="
echo "   EJE CLOUD IA — Gobierno de la Ciudad de BA    "
echo "=================================================="

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    exit 1
fi

# Verifica el archivo .env
if [ ! -f ".env" ]; then
    echo "⚠ Archivo .env no encontrado. Copiando desde .env.example..."
    cp .env.example .env
    echo "→ Editá el archivo .env con tu ANTHROPIC_API_KEY y credenciales de EJE CLOUD"
    echo ""
fi

# Instala dependencias si no están
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual Python..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Instalando dependencias..."
pip install -q -r requirements.txt

echo "Instalando navegadores Playwright (Chromium)..."
playwright install chromium

echo ""
echo "Iniciando servidor EJE CLOUD IA en http://localhost:8000"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
