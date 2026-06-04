/**
 * Service Worker — EJE CLOUD IA
 * Maneja las llamadas a la API de Gemini y la comunicación con el content script.
 */

const GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models";

const SYSTEM_PROMPT = `Sos un asistente de Inteligencia Artificial especializado en EJE CLOUD,
la plataforma de gestión del Consejo de la Magistratura de la Ciudad Autónoma de Buenos Aires (CMCABA).

Ayudás a funcionarios, magistrados y empleados del Consejo a:
1. Consultar y analizar la información visible en EJE CLOUD
2. Buscar expedientes, legajos y datos usando lenguaje natural
3. Generar documentos oficiales (informes, notas, resoluciones CM, dictámenes, memos)
4. Navegar y operar la plataforma EJE CLOUD

Tenés acceso a herramientas para leer la página actual, hacer click en elementos,
completar formularios y extraer datos de tablas de EJE CLOUD.

Comportamiento:
- Respondé siempre en español rioplatense
- Sé conciso y directo
- Explicá brevemente qué acción estás tomando cuando usás herramientas
- Protegé la información sensible de magistrados y funcionarios judiciales`;

const EJE_TOOLS = [
  {
    functionDeclarations: [
      {
        name: "obtener_pagina_actual",
        description: "Obtiene el contenido de texto completo de la página actual de EJE CLOUD, incluyendo formularios y datos visibles.",
        parameters: { type: "object", properties: {} },
      },
      {
        name: "extraer_tablas",
        description: "Extrae los datos de todas las tablas visibles en la página actual de EJE CLOUD en formato estructurado.",
        parameters: { type: "object", properties: {} },
      },
      {
        name: "hacer_click",
        description: "Hace click en un elemento de la página por su texto visible (botón, enlace, ítem de menú).",
        parameters: {
          type: "object",
          properties: {
            texto: {
              type: "string",
              description: "Texto visible del elemento en el que hacer click",
            },
          },
          required: ["texto"],
        },
      },
      {
        name: "completar_campo",
        description: "Completa un campo de formulario en EJE CLOUD con un valor específico.",
        parameters: {
          type: "object",
          properties: {
            selector: {
              type: "string",
              description: "Texto del label, placeholder o name del campo",
            },
            valor: {
              type: "string",
              description: "Valor a ingresar en el campo",
            },
          },
          required: ["selector", "valor"],
        },
      },
      {
        name: "buscar_en_pagina",
        description: "Ejecuta una búsqueda en el campo de búsqueda principal de la página actual.",
        parameters: {
          type: "object",
          properties: {
            termino: {
              type: "string",
              description: "Término o número a buscar (expediente, legajo, nombre, etc.)",
            },
          },
          required: ["termino"],
        },
      },
      {
        name: "navegar_url",
        description: "Navega a una sección de EJE CLOUD cambiando la URL del tab actual.",
        parameters: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "Ruta relativa dentro de EJE CLOUD (ej: '/expedientes', '/rrhh/legajos')",
            },
          },
          required: ["path"],
        },
      },
      {
        name: "generar_documento",
        description: "Genera un documento oficial del Consejo de la Magistratura de la CABA (informe, nota, resolución, memo o dictamen) con los datos proporcionados.",
        parameters: {
          type: "object",
          properties: {
            tipo: {
              type: "string",
              description: "Tipo de documento: informe, nota, resolucion, memo, dictamen",
            },
            asunto: {
              type: "string",
              description: "Asunto o título del documento",
            },
            destinatario: {
              type: "string",
              description: "Destinatario del documento",
            },
            contenido: {
              type: "string",
              description: "Contenido completo y desarrollado del documento en formato profesional",
            },
          },
          required: ["tipo", "asunto", "contenido"],
        },
      },
    ],
  },
];

// Abre el panel lateral al hacer click en el ícono de la extensión
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ tabId: tab.id });
});

// Listener principal de mensajes desde el sidepanel
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "CHAT") {
    handleChat(msg.message, msg.history, msg.tabId)
      .then((result) => sendResponse({ ok: true, ...result }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true; // mantiene el canal abierto para respuesta asíncrona
  }
});

async function handleChat(userMessage, history, tabId) {
  const { gemini_api_key, gemini_model } = await chrome.storage.local.get([
    "gemini_api_key",
    "gemini_model",
  ]);

  if (!gemini_api_key) {
    throw new Error("API Key de Gemini no configurada. Abrí las opciones de la extensión (click derecho → Opciones).");
  }

  const model = gemini_model || "gemini-2.0-flash";

  // Convierte historial al formato de Gemini
  const contents = historyToGemini(history);
  contents.push({ role: "user", parts: [{ text: userMessage }] });

  const actions = [];
  let generatedDoc = null;

  // Loop de function calling
  while (true) {
    const response = await callGemini(gemini_api_key, model, contents);

    const candidate = response.candidates?.[0];
    if (!candidate) throw new Error("Gemini no devolvió respuesta.");

    const parts = candidate.content?.parts || [];
    const fnCalls = parts.filter((p) => p.functionCall);

    if (fnCalls.length === 0) {
      const text = parts.map((p) => p.text || "").join("");
      return { text, actions, generatedDoc };
    }

    // Agrega respuesta del modelo al historial
    contents.push({ role: "model", parts });

    // Procesa cada function call
    const fnResults = [];
    for (const part of fnCalls) {
      const { name, args } = part.functionCall;
      actions.push({ name, args });

      let result;
      if (name === "generar_documento") {
        result = args; // el sidepanel lo renderiza
        generatedDoc = args;
      } else {
        result = await executePageTool(tabId, name, args);
      }

      fnResults.push({
        functionResponse: {
          name,
          response: { result: typeof result === "string" ? result : JSON.stringify(result) },
        },
      });
    }

    contents.push({ role: "user", parts: fnResults });
  }
}

async function callGemini(apiKey, model, contents) {
  const url = `${GEMINI_BASE}/${model}:generateContent?key=${apiKey}`;
  const body = {
    contents,
    tools: EJE_TOOLS,
    systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
    generationConfig: { temperature: 0.3, maxOutputTokens: 4096 },
  };

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `Error Gemini ${res.status}`);
  }

  return res.json();
}

async function executePageTool(tabId, toolName, args) {
  return new Promise((resolve) => {
    chrome.tabs.sendMessage(
      tabId,
      { type: "TOOL", tool: toolName, args },
      (response) => {
        if (chrome.runtime.lastError) {
          resolve(`Error: ${chrome.runtime.lastError.message}`);
        } else {
          resolve(response?.result || "Sin resultado");
        }
      }
    );
  });
}

function historyToGemini(history) {
  return history.map((msg) => ({
    role: msg.role === "assistant" ? "model" : "user",
    parts: [{ text: msg.content }],
  }));
}
