# EJE CLOUD IA 🤖

Asistente de Inteligencia Artificial Generativa para **EJE CLOUD** del Gobierno de la Ciudad Autónoma de Buenos Aires.

## Funcionalidades

- **💬 Chatbot / Asistente**: Consultas en lenguaje natural sobre EJE CLOUD
- **🔍 Búsqueda semántica**: Búsqueda de expedientes y documentos por descripción
- **📊 Análisis de datos**: Extracción y análisis de tablas y reportes del sistema
- **📄 Generación de documentos**: Informes, notas, memos y resoluciones en formato oficial GCBA

## Requisitos

- Python 3.10+
- Cuenta de acceso a EJE CLOUD (GCBA)
- API Key de Anthropic (Claude)

## Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/tegralan/eje.git
cd eje

# 2. Instalar dependencias
bash scripts/install.sh

# 3. Configurar variables de entorno
cp .env.example .env
# Editá .env con tu ANTHROPIC_API_KEY y credenciales de EJE CLOUD

# 4. Iniciar la aplicación
bash scripts/start.sh
```

Abrí tu navegador en `http://localhost:8000`

## Configuración (.env)

```
ANTHROPIC_API_KEY=sk-ant-...         # API Key de Anthropic
EJE_CLOUD_URL=https://ejecloud...    # URL de EJE CLOUD GCBA
EJE_CLOUD_USER=usuario@...           # Usuario EJE CLOUD
EJE_CLOUD_PASSWORD=contraseña        # Contraseña EJE CLOUD
CLAUDE_MODEL=claude-sonnet-4-6       # Modelo de IA
BROWSER_HEADLESS=true                # Modo sin ventana del navegador
```

## Arquitectura

```
app/
├── main.py              # FastAPI entry point
├── api/
│   ├── chat.py          # API de chat con IA
│   ├── documents.py     # Generador de documentos
│   └── browser.py       # Control del navegador
├── core/
│   ├── claude_client.py # Cliente Claude + herramientas IA
│   └── eje_browser.py   # Automatización Chrome/Playwright
├── services/
│   ├── ai_service.py    # Orquestación IA
│   └── document_service.py  # Plantillas de documentos GCBA
frontend/
├── index.html           # Interfaz web
├── css/style.css        # Estilos GCBA
└── js/app.js            # Lógica frontend
```

## API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/chat` | Chat con el asistente IA |
| DELETE | `/api/chat/{id}` | Limpiar sesión |
| POST | `/api/documentos` | Generar documento |
| POST | `/api/documentos/preview` | Preview HTML del documento |
| POST | `/api/browser/login` | Conectar a EJE CLOUD |
| GET | `/api/browser/status` | Estado del navegador |

Documentación interactiva: `http://localhost:8000/docs`

## Tecnología

- **Backend**: Python + FastAPI
- **IA**: Claude (Anthropic) con Tool Use
- **Navegador**: Playwright (Chromium)
- **Documentos**: Jinja2 templates HTML
