"""
Cliente de Claude con soporte para uso de herramientas (tool use).
Permite a la IA interactuar con EJE CLOUD a través del navegador.
"""
import json
import logging
from typing import List, Optional, Any
import anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

# Herramientas disponibles para Claude
EJE_TOOLS = [
    {
        "name": "navegar_a_seccion",
        "description": "Navega a una sección o módulo específico de EJE CLOUD. Usar para acceder a expedientes, RRHH, presupuesto, contrataciones, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "seccion": {
                    "type": "string",
                    "description": "Nombre o ruta de la sección a navegar (ej: 'expedientes', 'rrhh/agentes', 'presupuesto')",
                }
            },
            "required": ["seccion"],
        },
    },
    {
        "name": "buscar_informacion",
        "description": "Busca información en la página actual de EJE CLOUD usando un campo de búsqueda.",
        "input_schema": {
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
        "description": "Obtiene el contenido de texto de la página actual de EJE CLOUD para analizar la información disponible.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "extraer_tabla",
        "description": "Extrae los datos de tablas en la página actual de EJE CLOUD en formato estructurado.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "hacer_click",
        "description": "Hace click en un elemento de la página por su texto visible (botón, enlace, menú).",
        "input_schema": {
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
        "input_schema": {
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
        "description": "Genera un documento oficial (informe, nota, resolución, memo) basado en plantillas del GCBA.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tipo": {
                    "type": "string",
                    "enum": ["informe", "nota", "resolucion", "memo"],
                    "description": "Tipo de documento a generar",
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


SYSTEM_PROMPT = """Sos un asistente de Inteligencia Artificial especializado en EJE CLOUD, la plataforma de gestión de la Ciudad de Buenos Aires (GCBA).

Tu rol es ayudar a los agentes y empleados del gobierno de la Ciudad a:
1. **Navegar y consultar** información en EJE CLOUD de forma eficiente
2. **Buscar** expedientes, documentos y datos usando lenguaje natural
3. **Analizar** información y generar reportes claros
4. **Redactar** documentos oficiales según las normas del GCBA

## Capacidades:
- Podés navegar EJE CLOUD automáticamente a través del navegador
- Podés extraer y analizar datos de tablas y formularios
- Podés generar documentos en formato oficial del GCBA
- Conocés la estructura y módulos de EJE CLOUD: Expedientes, RRHH, Presupuesto, Contrataciones, etc.

## Comportamiento:
- Respondé siempre en español rioplatense (vos, che, etc.)
- Sé conciso y directo
- Cuando uses herramientas, explicá brevemente qué estás haciendo
- Si encontrás errores en EJE CLOUD, informá al usuario claramente
- Protegé la información sensible de los agentes del gobierno

## Contexto:
- Trabajás para el Gobierno de la Ciudad de Buenos Aires
- Los usuarios son agentes del GCBA que necesitan gestionar tareas administrativas
- EJE CLOUD es el sistema ERP del GCBA para gestión de recursos humanos, presupuesto y expedientes"""


async def chat_with_claude(
    message: str,
    history: List[dict] = None,
    browser=None,
    document_service=None,
) -> tuple[str, List[str]]:
    """
    Envía un mensaje a Claude con soporte para herramientas de EJE CLOUD.
    Retorna (respuesta_texto, lista_de_acciones).
    """
    messages = list(history or [])
    messages.append({"role": "user", "content": message})

    actions_taken = []

    while True:
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=EJE_TOOLS,
            messages=messages,
        )

        # Si no hay uso de herramientas, retorna la respuesta
        if response.stop_reason == "end_turn":
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            return text, actions_taken

        # Procesa las herramientas solicitadas
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    logger.info(f"Claude usa herramienta: {tool_name} con {tool_input}")
                    actions_taken.append(f"🔧 {tool_name}: {json.dumps(tool_input, ensure_ascii=False)[:80]}")

                    result = await _execute_tool(tool_name, tool_input, browser, document_service)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

            # Agrega la respuesta del asistente con las herramientas al historial
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        else:
            # Cualquier otro stop_reason
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            return text or "No pude procesar la solicitud.", actions_taken


async def _execute_tool(tool_name: str, tool_input: dict, browser, document_service) -> Any:
    """Ejecuta la herramienta solicitada por Claude."""
    try:
        if tool_name == "navegar_a_seccion":
            if not browser:
                return "Error: navegador no disponible"
            seccion = tool_input.get("seccion", "")
            return await browser.navigate_to(seccion)

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
