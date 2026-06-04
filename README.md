# EJE CLOUD IA 🤖

Asistente de Inteligencia Artificial Generativa para **EJE CLOUD** del **Consejo de la Magistratura de la Ciudad Autónoma de Buenos Aires**.

## Funcionalidades

- **💬 Chatbot / Asistente**: Consultas en lenguaje natural sobre EJE CLOUD
- **🔍 Búsqueda semántica**: Búsqueda de expedientes, legajos y concursos por descripción
- **📊 Análisis de datos**: Extracción y análisis de tablas y reportes del sistema
- **📄 Generación de documentos**: Informes, notas, memos, resoluciones CM y dictámenes

## Requisitos

- Python 3.10+
- Cuenta de acceso a EJE CLOUD del Consejo de la Magistratura (`@jusbaires.gob.ar`)
- API Key de Google Gemini (gratis en [aistudio.google.com](https://aistudio.google.com))

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
GEMINI_API_KEY=AIza...                              # API Key de Google Gemini
EJE_CLOUD_URL=https://ejecloud.jusbaires.gob.ar    # URL de EJE CLOUD
EJE_CLOUD_USER=usuario@jusbaires.gob.ar            # Usuario EJE CLOUD
EJE_CLOUD_PASSWORD=contraseña                       # Contraseña EJE CLOUD
GEMINI_MODEL=gemini-2.0-flash                       # Modelo de IA
BROWSER_HEADLESS=true                               # Modo sin ventana del navegador
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
│   └── document_service.py  # Plantillas del Consejo de la Magistratura
frontend/
├── index.html           # Interfaz web
├── css/style.css        # Estilos institucionales
└── js/app.js            # Lógica frontend
```

## Tipos de documentos soportados

| Tipo | Descripción |
|------|-------------|
| `informe` | Informe técnico o administrativo |
| `nota` | Nota oficial dirigida a un destinatario |
| `memo` | Memorando interno |
| `resolucion` | Resolución del Consejo de la Magistratura |
| `dictamen` | Dictamen de asesoría o área competente |

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
- **IA**: Gemini (Google) con Function Calling
- **Navegador**: Playwright (Chromium) — automatización de EJE CLOUD
- **Documentos**: Jinja2 + plantillas HTML institucionales
