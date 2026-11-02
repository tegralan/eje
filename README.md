# EJE CLOUD IA — Extensión de Chrome

Extensión de Chrome con Inteligencia Artificial Generativa para **EJE CLOUD** del **Consejo de la Magistratura de la Ciudad Autónoma de Buenos Aires**.

## Funcionalidades

- **💬 Asistente IA**: Panel lateral que responde preguntas sobre lo que está en pantalla
- **🔍 Lectura de página**: Lee y analiza el contenido de EJE CLOUD automáticamente
- **📊 Extracción de datos**: Extrae tablas y datos estructurados de cualquier pantalla
- **🖱 Automatización**: Hace clicks, completa formularios y navega dentro de EJE CLOUD
- **📄 Generador de documentos**: Crea informes, notas, memos, resoluciones CM y dictámenes

## Instalación

### 1. Obtener API Key de Gemini (gratuita)

1. Entrá a **[aistudio.google.com](https://aistudio.google.com)**
2. "Get API key" → "Create API key"
3. Copiá la clave (empieza con `AIza...`)

### 2. Instalar la extensión en Chrome

1. Abrí Chrome → `chrome://extensions`
2. Activá **"Modo desarrollador"** (switch arriba a la derecha)
3. Click en **"Cargar descomprimida"**
4. Seleccioná la carpeta `extension/` de este repositorio
5. La extensión aparece en la barra de Chrome

### 3. Configurar la API Key

1. Click derecho en el ícono de la extensión → **"Opciones"**
2. Pegá tu API Key de Gemini
3. Guardá

### 4. Usar la extensión

1. Abrí **EJE CLOUD** (`ejecloud.jusbaires.gob.ar`) en Chrome
2. Click en el ícono de la extensión → se abre el panel lateral
3. Escribile al asistente lo que necesitás

## Estructura

```
extension/
├── manifest.json       # Configuración de la extensión (Manifest V3)
├── background.js       # Service worker — llama a la API de Gemini
├── content.js          # Script inyectado en EJE CLOUD — lee y controla el DOM
├── sidepanel.html/js/css  # Panel lateral con el chat
├── options.html/js/css    # Página de configuración (API Key)
└── icons/              # Íconos de la extensión
```

## Ejemplos de uso

```
"Leé la página actual y decime qué expedientes aparecen"
"Buscá el expediente CM-2024-12345"
"Extraé los datos de la tabla y generá un informe"
"Redactá un dictamen sobre la solicitud de licencia del agente"
"Hacé click en el botón Guardar"
```

## Alcance y privacidad

La extensión solo se inyecta en `https://ejecloud.jusbaires.gob.ar/*`. El texto que se envía al asistente se transmite a Google Gemini mediante la API Key configurada. No envíes expedientes, datos personales ni información reservada sin autorización institucional y una política de uso aprobada.

La extensión puede leer la página y extraer tablas. Antes de hacer clic o completar un campo, solicita confirmación porque esas acciones podrían guardar o enviar datos.

## Aplicación Python (experimental)

El repositorio también contiene una aplicación separada en `app/`, con interfaz web, API FastAPI y navegador Playwright. No forma parte del flujo de instalación de la extensión ni está conectada a ella. Se conserva como prototipo experimental; no la expongas en una red ni la uses con credenciales o datos reales sin una revisión de seguridad.

Para iniciarla localmente, completá `GEMINI_API_KEY` en `.env` y ejecutá `scripts/start.sh`. El servidor escucha solo en `127.0.0.1:8000`. El archivo `.env` contiene secretos y no debe subirse al repositorio.

## Tecnología

- **Extensión**: Chrome Extension Manifest V3
- **IA de la extensión**: Google Gemini con Function Calling (API directa desde el navegador)
- **Aplicación experimental**: Python, FastAPI y Playwright
