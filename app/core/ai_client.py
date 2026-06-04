"""
Cliente de Gemini (Google) con soporte para function calling.
Permite a la IA interactuar con EJE CLOUD a través del navegador.
"""
import json
import logging
from typing import List, Any

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.gemini_api_key)

# Herramientas disponibles para Gemini (function calling)
EJE_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "navegar_a_seccion",
                "description": "Navega a una sección o módulo específico de EJE CLOUD. Usar para acceder a expedientes, RRHH, presupuesto, contrataciones, concursos, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seccion": {
                            "type": "string",
                            "description": "Nombre o ruta de la sección (ej: 'expedientes', 'rrhh/legajos', 'concursos')",
                        }
                    },
                    "required": ["seccion"],
                },
            },
            {
                "name": "buscar_informacion",
                "description": "Busca información en la página actual de EJE CLOUD usando un campo de búsqueda.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campo": {
                            "type": "string",
                            "description": "Nombre del campo de búsqueda (ej: 'expediente', 'agente', 'numero')",
                        },
                        "valor": {
                            "type": "string",
                            "description": "Valor a buscar",
                        },
                    },
                    "required": ["campo", "valor"],
                },
            },
            {
                "name": "obtener_contenido_pagina",
                "description": "Obtiene el contenido de texto de la página actual de EJE CLOUD.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "extraer_tabla",
                "description": "Extrae los datos de tablas en la página actual de EJE CLOUD en formato estructurado.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "hacer_click",
                "description": "Hace click en un elemento de la página por su texto visible (botón, enlace, menú).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "texto": {
                            "type": "string",
                            "description": "Texto visible del elemento en el que hacer click",
                        }
                    },
                    "required": ["texto"],
                },
            },
            {
                "name": "completar_formulario",
                "description": "Completa un formulario en EJE CLOUD con los datos proporcionados.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campos": {
                            "type": "object",
                            "description": "Diccionario con nombre_campo: valor para cada campo del formulario",
                        }
                    },
                    "required": ["campos"],
                },
            },
            {
                "name": "generar_documento",
                "description": "Genera un documento oficial del Consejo de la Magistratura (informe, nota, resolución, memo, dictamen).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tipo": {
                            "type": "string",
                            "description": "Tipo: informe, nota, resolucion, memo, dictamen",
                        },
                        "asunto": {
                            "type": "string",
                            "description": "Asunto o título del documento",
                        },
                        "destinatario": {
                            "type": "string",
                            "description": "Destinatario del documento",
                        },
                        "contenido": {
                            "type": "string",
                            "description": "Contenido principal del documento",
                        },
                    },
                    "required": ["tipo", "asunto", "contenido"],
                },
            },
        ]
    }
]

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

SYSTEM_PROMPT = """Sos un asistente de Inteligencia Artificial especializado en EJE CLOUD, la plataforma de gestión del Consejo de la Magistratura de la Ciudad Autónoma de Buenos Aires (CMCABA).

Tu rol es ayudar a los funcionarios, magistrados y empleados del Consejo de la Magistratura a:
1. Navegar y consultar información en EJE CLOUD de forma eficiente
2. Buscar expedientes, legajos y datos usando lenguaje natural
3. Analizar información y generar reportes claros
4. Redactar documentos oficiales según las normas del Consejo de la Magistratura

Podés navegar EJE CLOUD automáticamente a través del navegador, extraer datos de tablas y formularios, y generar documentos oficiales (informe, nota, memo, resolución CM, dictamen).

Comportamiento:
- Respondé siempre en español rioplatense
- Sé conciso y directo
- Explicá brevemente qué herramienta estás usando y por qué
- Protegé la información sensible de magistrados y funcionarios judiciales"""


def _build_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(
        model_name=settings.gemini_model,
        tools=EJE_TOOLS,
        system_instruction=SYSTEM_PROMPT,
        safety_settings=SAFETY_SETTINGS,
    )


def _history_to_gemini(history: List[dict]) -> List[dict]:
    """Convierte el historial interno al formato de Gemini (role: user/model)."""
    contents = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents


async def chat_with_gemini(
    message: str,
    history: List[dict] = None,
    browser=None,
    document_service=None,
) -> tuple[str, List[str]]:
    """
    Envía un mensaje a Gemini con soporte para function calling de EJE CLOUD.
    Retorna (respuesta_texto, lista_de_acciones).
    """
    model = _build_model()
    actions_taken = []

    # Construye el historial en formato Gemini
    contents = _history_to_gemini(history or [])
    contents.append({"role": "user", "parts": [{"text": message}]})

    # Loop de function calling
    while True:
        response = await model.generate_content_async(contents=contents)

        candidate = response.candidates[0]
        parts = candidate.content.parts

        # Busca function calls en las partes de la respuesta
        fn_calls = [p for p in parts if p.function_call.name if hasattr(p, "function_call") and p.function_call.name]

        if not fn_calls:
            # Sin function calls: retorna el texto
            text = "".join(p.text for p in parts if hasattr(p, "text") and p.text)
            return text or "No pude procesar la solicitud.", actions_taken

        # Agrega la respuesta del modelo al historial
        contents.append({"role": "model", "parts": parts})

        # Procesa cada function call y acumula los resultados
        fn_results = []
        for part in fn_calls:
            fn = part.function_call
            fn_name = fn.name
            fn_args = {k: v for k, v in fn.args.items()}

            logger.info(f"Gemini usa herramienta: {fn_name} con {fn_args}")
            actions_taken.append(f"🔧 {fn_name}: {json.dumps(fn_args, ensure_ascii=False)[:80]}")

            result = await _execute_tool(fn_name, fn_args, browser, document_service)

            fn_results.append({
                "function_response": {
                    "name": fn_name,
                    "response": {"result": str(result)},
                }
            })

        # Envía los resultados de las herramientas al modelo
        contents.append({"role": "user", "parts": fn_results})


async def _execute_tool(tool_name: str, tool_input: dict, browser, document_service) -> Any:
    """Ejecuta la herramienta solicitada por Gemini."""
    try:
        if tool_name == "navegar_a_seccion":
            if not browser:
                return "Error: navegador no disponible"
            return await browser.navigate_to(tool_input.get("seccion", ""))

        elif tool_name == "buscar_informacion":
            if not browser:
                return "Error: navegador no disponible"
            return await browser.search_in_page(
                tool_input.get("campo", ""),
                tool_input.get("valor", ""),
            )

        elif tool_name == "obtener_contenido_pagina":
            if not browser:
                return "Error: navegador no disponible"
            return await browser.get_page_content()

        elif tool_name == "extraer_tabla":
            if not browser:
                return "Error: navegador no disponible"
            data = await browser.extract_table_data()
            return json.dumps(data, ensure_ascii=False, indent=2)

        elif tool_name == "hacer_click":
            if not browser:
                return "Error: navegador no disponible"
            return await browser.click_element(tool_input.get("texto", ""))

        elif tool_name == "completar_formulario":
            if not browser:
                return "Error: navegador no disponible"
            return await browser.fill_form(tool_input.get("campos", {}))

        elif tool_name == "generar_documento":
            if not document_service:
                return "Error: servicio de documentos no disponible"
            return await document_service.generate(
                tipo=tool_input.get("tipo", "informe"),
                asunto=tool_input.get("asunto", ""),
                destinatario=tool_input.get("destinatario", ""),
                contenido=tool_input.get("contenido", ""),
            )

        else:
            return f"Herramienta desconocida: {tool_name}"

    except Exception as e:
        logger.error(f"Error ejecutando herramienta {tool_name}: {e}")
        return f"Error al ejecutar {tool_name}: {str(e)}"
