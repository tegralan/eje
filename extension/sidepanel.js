/* EJE CLOUD IA — Side Panel Logic */

let history = [];
let currentTabId = null;
let lastGeneratedDoc = null;

// ---- Inicialización ----
document.addEventListener("DOMContentLoaded", async () => {
  // Obtiene el tab activo
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTabId = tab?.id;

  // Muestra el modelo configurado
  const { gemini_model } = await chrome.storage.local.get("gemini_model");
  document.getElementById("modelLabel").textContent = gemini_model || "gemini-2.0-flash";

  // Mensaje de bienvenida
  appendMsg("assistant", `¡Hola! Soy el asistente IA de **EJE CLOUD** del Consejo de la Magistratura.

Puedo leer la página que tenés abierta, buscar datos, completar formularios y generar documentos oficiales.

¿En qué te ayudo?`);
});

// ---- Envío de mensajes ----
function onKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 100) + "px";
}

async function sendMessage() {
  const input = document.getElementById("msgInput");
  const text = input.value.trim();
  if (!text || document.getElementById("sendBtn").disabled) return;

  input.value = "";
  input.style.height = "auto";
  appendMsg("user", text);
  await callAI(text);
}

async function quickQuery(text) {
  appendMsg("user", text);
  await callAI(text);
}

async function callAI(message) {
  const sendBtn = document.getElementById("sendBtn");
  sendBtn.disabled = true;

  const typingId = showTyping();

  try {
    const response = await chrome.runtime.sendMessage({
      type: "CHAT",
      message,
      history,
      tabId: currentTabId,
    });

    removeTyping(typingId);

    if (!response.ok) {
      appendMsg("assistant", `❌ ${response.error}`);
      return;
    }

    // Muestra acciones tomadas
    if (response.actions?.length) {
      showActions(response.actions);
    }

    // Guarda documento generado si hay
    if (response.generatedDoc) {
      lastGeneratedDoc = response.generatedDoc;
      const docHtml = buildDocumentHtml(response.generatedDoc);
      document.getElementById("docContent").innerHTML = docHtml;

      const msgWithBadge = (response.text || "") +
        `\n\n<span class="doc-badge" onclick="toggleDocPanel()">📄 Ver documento generado →</span>`;
      appendMsg("assistant", msgWithBadge, true);
    } else {
      appendMsg("assistant", response.text || "Sin respuesta.");
    }

    // Actualiza historial
    history.push({ role: "user", content: message });
    history.push({ role: "assistant", content: response.text || "" });

    // Limita historial a 30 turnos
    if (history.length > 60) history = history.slice(-60);

  } catch (err) {
    removeTyping(typingId);
    appendMsg("assistant", `❌ Error de comunicación: ${err.message}`);
  } finally {
    sendBtn.disabled = false;
  }
}

// ---- UI helpers ----
function appendMsg(role, content, rawHtml = false) {
  const container = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = `msg ${role}`;

  const avatarText = role === "assistant" ? "IA" : "Vos";
  const bubbleContent = rawHtml ? content : formatText(content);

  div.innerHTML = `
    <div class="avatar">${avatarText}</div>
    <div class="bubble">${bubbleContent}</div>
  `;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function showTyping() {
  const id = "typing-" + Date.now();
  const container = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = "msg assistant";
  div.id = id;
  div.innerHTML = `
    <div class="avatar">IA</div>
    <div class="bubble">
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTyping(id) {
  document.getElementById(id)?.remove();
}

function showActions(actions) {
  const container = document.getElementById("messages");
  const bar = document.createElement("div");
  bar.className = "actions-bar";
  bar.innerHTML = actions
    .map((a) => `<div class="action-item">${a.name}(${JSON.stringify(a.args).substring(0, 60)})</div>`)
    .join("");
  container.appendChild(bar);
}

function formatText(text) {
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/^#{1,3} (.+)$/gm, "<strong>$1</strong>")
    .replace(/^[-•]\s(.+)$/gm, "<li>$1</li>")
    .replace(/(<li>[\s\S]+?<\/li>)/g, "<ul>$1</ul>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>")
    .replace(/^(?!<)(.+)/gm, "<p>$1</p>");
}

function clearChat() {
  history = [];
  document.getElementById("messages").innerHTML = "";
  appendMsg("assistant", "Conversación limpiada. ¿En qué te ayudo?");
}

function openOptions() {
  chrome.runtime.openOptionsPage();
}

function toggleDocPanel() {
  const chat = document.getElementById("chatPanel");
  const doc = document.getElementById("docPanel");
  if (doc.classList.contains("active")) {
    doc.classList.remove("active");
    chat.classList.add("active");
  } else {
    chat.classList.remove("active");
    doc.classList.add("active");
  }
}

function printDoc() {
  const content = document.getElementById("docContent").innerHTML;
  const win = window.open("", "_blank");
  win.document.write(`<!DOCTYPE html><html><body>${content}</body></html>`);
  win.document.close();
  win.print();
}

function copyDocHtml() {
  const html = document.getElementById("docContent").innerHTML;
  navigator.clipboard.writeText(html).then(() => alert("HTML copiado al portapapeles"));
}

// ---- Generador de documentos (HTML) ----
function buildDocumentHtml({ tipo, asunto, contenido, destinatario }) {
  const fecha = new Date().toLocaleDateString("es-AR", {
    day: "numeric", month: "long", year: "numeric",
  });
  const anio = new Date().getFullYear();
  const dest = destinatario || "A quien corresponda";
  const body = (contenido || "").replace(/\n/g, "<br>");

  const header = `
    <div style="border-bottom:3px solid #C9A84C;padding-bottom:14px;margin-bottom:22px;display:flex;justify-content:space-between;align-items:flex-end;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:50px;height:50px;background:#1A1A3E;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid #C9A84C;color:#C9A84C;font-weight:800;font-size:14px;">CM</div>
        <div>
          <div style="font-size:13px;font-weight:800;color:#1A1A3E;">CONSEJO DE LA MAGISTRATURA</div>
          <div style="font-size:11px;color:#2C3E7A;font-weight:600;">CIUDAD AUTÓNOMA DE BUENOS AIRES</div>
          <div style="font-size:10px;color:#888;">EJE CLOUD — Sistema de Gestión Judicial</div>
        </div>
      </div>
      <div style="font-size:12px;color:#555;text-align:right;">Buenos Aires, ${fecha}</div>
    </div>`;

  const base = `font-family:Arial,sans-serif;margin:30px;color:#222;`;

  const templates = {
    informe: `<div style="${base}">
      ${header}
      <div style="display:inline-block;background:#1A1A3E;color:white;padding:3px 12px;border-radius:3px;font-size:11px;letter-spacing:1px;">INFORME</div>
      <h1 style="color:#1A1A3E;font-size:16px;text-align:center;margin:16px 0;text-transform:uppercase;">${asunto}</h1>
      <div style="background:#f8f8f0;padding:12px 16px;border-left:4px solid #C9A84C;margin-bottom:18px;font-size:13px;">
        <p><strong>Para:</strong> ${dest}</p>
        <p><strong>Asunto:</strong> ${asunto}</p>
        <p><strong>Fecha:</strong> ${fecha}</p>
      </div>
      <div style="line-height:1.75;font-size:13px;text-align:justify;">${body}</div>
      <div style="margin-top:55px;text-align:right;font-size:12px;"><p>________________________</p><p>Firma y Sello<br>Consejo de la Magistratura — CABA</p></div>
      <div style="margin-top:35px;border-top:1px solid #ddd;padding-top:8px;font-size:10px;color:#999;text-align:center;">Documento generado por EJE CLOUD IA — Consejo de la Magistratura de la CABA — ${fecha}</div>
    </div>`,

    nota: `<div style="${base}">
      ${header}
      <div style="text-align:right;font-size:12px;color:#555;margin-bottom:16px;">Nota N°: ____/${anio}</div>
      <div style="font-size:13px;margin-bottom:14px;"><strong>Al/A la Señor/a:</strong><br>${dest}</div>
      <div style="font-weight:700;color:#1A1A3E;font-size:13px;margin-bottom:16px;">REF.: ${asunto}</div>
      <div style="line-height:1.8;font-size:13px;border-top:1px solid #eee;padding-top:14px;text-align:justify;">
        <p>Me dirijo a usted a efectos de comunicarle lo siguiente:</p><p>${body}</p>
      </div>
      <p style="margin-top:28px;font-size:13px;">Sin otro particular, saludo a usted muy atentamente.</p>
      <div style="margin-top:55px;font-size:12px;"><p>________________________</p><p>Firma y Sello<br>Consejo de la Magistratura — CABA</p></div>
    </div>`,

    memo: `<div style="${base}">
      ${header}
      <div style="background:#1A1A3E;color:white;padding:10px 16px;margin-bottom:20px;letter-spacing:2px;font-size:13px;font-weight:700;">MEMORANDO INTERNO</div>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:13px;">
        <tr><td style="padding:7px 10px;border-bottom:1px solid #eee;font-weight:700;color:#1A1A3E;width:90px;">PARA:</td><td style="padding:7px 10px;border-bottom:1px solid #eee;">${dest}</td></tr>
        <tr><td style="padding:7px 10px;border-bottom:1px solid #eee;font-weight:700;color:#1A1A3E;">ASUNTO:</td><td style="padding:7px 10px;border-bottom:1px solid #eee;">${asunto}</td></tr>
        <tr><td style="padding:7px 10px;border-bottom:1px solid #eee;font-weight:700;color:#1A1A3E;">FECHA:</td><td style="padding:7px 10px;border-bottom:1px solid #eee;">${fecha}</td></tr>
      </table>
      <div style="line-height:1.75;font-size:13px;padding:14px 16px;background:#fafaf5;border-left:3px solid #C9A84C;">${body}</div>
    </div>`,

    resolucion: `<div style="font-family:'Times New Roman',serif;margin:40px;color:#000;">
      ${header}
      <div style="text-align:center;margin-bottom:22px;">
        <div style="font-size:15px;font-weight:bold;letter-spacing:3px;">CONSEJO DE LA MAGISTRATURA</div>
        <div style="font-size:11px;color:#555;">Ciudad Autónoma de Buenos Aires</div>
        <div style="font-size:22px;font-weight:bold;margin:12px 0 4px;">RESOLUCIÓN CM N°: ____/${anio}</div>
      </div>
      <div style="margin:18px 0;font-size:13px;"><strong>VISTO:</strong> <p>${asunto}, y</p></div>
      <div style="margin:18px 0;font-size:13px;"><strong>CONSIDERANDO:</strong> <p>${body}</p></div>
      <p style="text-align:center;font-weight:bold;letter-spacing:2px;margin:20px 0;">EL CONSEJO DE LA MAGISTRATURA RESUELVE</p>
      <p style="font-size:13px;line-height:1.8;text-align:justify;margin-bottom:12px;"><strong>ARTÍCULO 1°.-</strong> ${asunto}.</p>
      <p style="font-size:13px;line-height:1.8;text-align:justify;"><strong>ARTÍCULO 2°.-</strong> Regístrese. Comuníquese a ${dest}. Archívese.</p>
      <div style="margin-top:65px;text-align:center;font-size:12px;">
        <div style="border-top:1px solid #000;padding-top:5px;width:250px;margin:0 auto;">Presidente del Consejo de la Magistratura<br>Ciudad Autónoma de Buenos Aires</div>
      </div>
    </div>`,

    dictamen: `<div style="font-family:'Times New Roman',serif;margin:40px;color:#000;">
      ${header}
      <div style="display:inline-block;border:2px solid #1A1A3E;padding:3px 14px;font-size:12px;font-weight:bold;letter-spacing:2px;margin-bottom:16px;">DICTAMEN</div>
      <h1 style="font-size:15px;text-align:center;margin:10px 0 20px;text-transform:uppercase;">${asunto}</h1>
      <div style="margin:16px 0;font-size:13px;line-height:1.75;"><strong>Antecedentes y Análisis:</strong><p>${body}</p></div>
      <div style="margin-top:24px;padding:14px 18px;border:1px solid #1A1A3E;background:#f9f9f5;font-size:13px;line-height:1.75;">
        <strong>OPINIÓN:</strong> En virtud de lo expuesto, esta asesoría entiende que corresponde proceder conforme lo indicado, dejando a criterio del Consejo de la Magistratura de la CABA la adopción de las medidas pertinentes.
      </div>
      <div style="margin-top:55px;font-size:12px;"><p>________________________</p><p>Firma y Sello<br>Asesoría — Consejo de la Magistratura CABA</p></div>
    </div>`,
  };

  return templates[tipo] || templates.informe;
}
