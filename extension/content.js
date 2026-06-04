/**
 * Content Script — EJE CLOUD IA
 * Se inyecta en las páginas de EJE CLOUD y ejecuta las acciones solicitadas por la IA.
 */

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type !== "TOOL") return;

  handleTool(msg.tool, msg.args)
    .then((result) => sendResponse({ result }))
    .catch((err) => sendResponse({ result: `Error: ${err.message}` }));

  return true; // asíncrono
});

async function handleTool(tool, args) {
  switch (tool) {
    case "obtener_pagina_actual":
      return getPageContent();
    case "extraer_tablas":
      return extractTables();
    case "hacer_click":
      return clickElement(args.texto);
    case "completar_campo":
      return fillField(args.selector, args.valor);
    case "buscar_en_pagina":
      return searchInPage(args.termino);
    case "navegar_url":
      return navigateTo(args.path);
    default:
      return `Herramienta desconocida: ${tool}`;
  }
}

function getPageContent() {
  const skip = ["script", "style", "noscript", "svg", "path", "meta", "link"];
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const tag = node.parentElement?.tagName?.toLowerCase();
        if (skip.includes(tag)) return NodeFilter.FILTER_REJECT;
        const text = node.textContent.trim();
        return text.length > 1 ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
      },
    }
  );

  const lines = [];
  let node;
  while ((node = walker.nextNode())) {
    lines.push(node.textContent.trim());
  }

  return lines.join("\n").replace(/\n{3,}/g, "\n\n").substring(0, 8000);
}

function extractTables() {
  const tables = document.querySelectorAll("table");
  if (!tables.length) return "No se encontraron tablas en la página actual.";

  const result = [];
  tables.forEach((table, i) => {
    const headers = [...table.querySelectorAll("th")].map((th) => th.innerText.trim());
    const rows = [...table.querySelectorAll("tbody tr")].map((tr) => {
      const cells = [...tr.querySelectorAll("td")].map((td) => td.innerText.trim());
      if (headers.length) {
        const obj = {};
        headers.forEach((h, idx) => { obj[h] = cells[idx] ?? ""; });
        return obj;
      }
      return cells;
    });
    if (rows.length) result.push({ tabla: i + 1, headers, filas: rows });
  });

  return result.length
    ? JSON.stringify(result, null, 2)
    : "No se encontraron datos en las tablas.";
}

async function clickElement(texto) {
  // Busca por texto exacto primero, luego parcial
  const candidates = [
    ...document.querySelectorAll("button, a, [role='button'], [role='menuitem'], td, th, label, span"),
  ];

  const exact = candidates.find(
    (el) => el.innerText?.trim().toLowerCase() === texto.toLowerCase()
  );
  const match =
    exact ||
    candidates.find((el) =>
      el.innerText?.trim().toLowerCase().includes(texto.toLowerCase())
    );

  if (!match) return `No se encontró el elemento con texto: "${texto}"`;

  match.click();
  await wait(800);
  return `Click realizado en: "${match.innerText.trim()}"`;
}

async function fillField(selectorText, valor) {
  const inputs = [
    ...document.querySelectorAll("input, textarea, select"),
  ];

  const match = inputs.find((el) => {
    const label = document.querySelector(`label[for="${el.id}"]`);
    return (
      el.placeholder?.toLowerCase().includes(selectorText.toLowerCase()) ||
      el.name?.toLowerCase().includes(selectorText.toLowerCase()) ||
      el.id?.toLowerCase().includes(selectorText.toLowerCase()) ||
      label?.innerText?.toLowerCase().includes(selectorText.toLowerCase())
    );
  });

  if (!match) return `No se encontró el campo: "${selectorText}"`;

  match.focus();
  if (match.tagName === "SELECT") {
    const option = [...match.options].find(
      (o) => o.text.toLowerCase().includes(valor.toLowerCase())
    );
    if (option) match.value = option.value;
    else return `Opción "${valor}" no encontrada en el select`;
  } else {
    match.value = valor;
    match.dispatchEvent(new Event("input", { bubbles: true }));
    match.dispatchEvent(new Event("change", { bubbles: true }));
  }

  await wait(300);
  return `Campo "${selectorText}" completado con: "${valor}"`;
}

async function searchInPage(termino) {
  const searchInputs = document.querySelectorAll(
    "input[type='search'], input[type='text'][placeholder*='buscar'], input[type='text'][placeholder*='Buscar'], input[name*='search'], input[id*='search'], input[id*='buscar']"
  );

  const input = searchInputs[0];
  if (!input) {
    // intenta el primer input de texto visible
    const fallback = document.querySelector("input[type='text']:not([type='hidden'])");
    if (!fallback) return "No se encontró campo de búsqueda en la página";
    fallback.value = termino;
    fallback.dispatchEvent(new Event("input", { bubbles: true }));
    fallback.dispatchEvent(new KeyboardEvent("keypress", { key: "Enter", bubbles: true }));
    await wait(1000);
    return `Búsqueda ejecutada: "${termino}"`;
  }

  input.focus();
  input.value = termino;
  input.dispatchEvent(new Event("input", { bubbles: true }));
  input.dispatchEvent(new KeyboardEvent("keypress", { key: "Enter", keyCode: 13, bubbles: true }));
  await wait(1000);
  return `Búsqueda realizada: "${termino}"`;
}

function navigateTo(path) {
  const base = window.location.origin;
  const url = base + (path.startsWith("/") ? path : "/" + path);
  window.location.href = url;
  return `Navegando a: ${url}`;
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
