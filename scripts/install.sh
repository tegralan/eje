#!/bin/bash
# Script de instalación de dependencias

set -e

echo "Instalando EJE CLOUD IA..."

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

playwright install chromium
playwright install-deps chromium

echo ""
echo "✓ Instalación completada"
echo ""
echo "Próximos pasos:"
echo "  1. Copiá .env.example a .env"
echo "  2. Editá .env con tu ANTHROPIC_API_KEY y las credenciales de EJE CLOUD"
echo "  3. Ejecutá: bash scripts/start.sh"
