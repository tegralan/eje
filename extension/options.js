document.addEventListener("DOMContentLoaded", async () => {
  const { gemini_api_key, gemini_model } = await chrome.storage.local.get([
    "gemini_api_key",
    "gemini_model",
  ]);
  if (gemini_api_key) document.getElementById("apiKey").value = gemini_api_key;
  if (gemini_model) document.getElementById("model").value = gemini_model;
});

async function save() {
  const key = document.getElementById("apiKey").value.trim();
  const model = document.getElementById("model").value;
  const msg = document.getElementById("msg");

  if (!key) {
    showMsg("Ingresá la API Key de Gemini.", "error");
    return;
  }

  await chrome.storage.local.set({ gemini_api_key: key, gemini_model: model });
  showMsg("✓ Configuración guardada correctamente.", "ok");
}

function showMsg(text, type) {
  const el = document.getElementById("msg");
  el.textContent = text;
  el.className = "msg " + type;
  el.style.display = "block";
  setTimeout(() => { el.style.display = "none"; }, 3000);
}
