/* EJE CLOUD IA — Frontend JS */

let sessionId = null;
let isProcessing = false;

// ---- Tabs ----
document.querySelectorAll('.nav-item[data-tab]').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const tab = item.dataset.tab;

        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

        item.classList.add('active');
        document.getElementById(`tab-${tab}`).classList.add('active');
    });
});

// ---- Chat ----
function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message || isProcessing) return;

    input.value = '';
    input.style.height = 'auto';
    appendMessage('user', message);
    await callChatAPI(message);
}

async function sendQuickQuery(text) {
    // Cambia al tab de chat
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="chat"]').classList.add('active');
    document.getElementById('tab-chat').classList.add('active');

    appendMessage('user', text);
    await callChatAPI(text);
}

async function callChatAPI(message) {
    isProcessing = true;
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;

    // Muestra el indicador de escritura
    const typingId = showTyping();
    const actionsArea = document.getElementById('actionsArea');
    const actionsList = document.getElementById('actionsList');
    const actionsText = document.getElementById('actionsText');
    actionsArea.style.display = 'block';
    actionsList.innerHTML = '';
    actionsText.textContent = 'Consultando EJE CLOUD...';

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                session_id: sessionId,
                history: [],
            }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error del servidor');
        }

        const data = await res.json();
        sessionId = data.session_id;

        document.getElementById('sessionInfo').textContent = `Sesión: ${sessionId.substring(0, 8)}...`;

        // Muestra las acciones tomadas
        if (data.actions_taken && data.actions_taken.length > 0) {
            data.actions_taken.forEach(action => {
                const div = document.createElement('div');
                div.className = 'action-item';
                div.textContent = action;
                actionsList.appendChild(div);
            });
            actionsText.textContent = `${data.actions_taken.length} acciones realizadas`;
        } else {
            actionsArea.style.display = 'none';
        }

        removeTyping(typingId);
        appendMessage('assistant', data.response);

        // Oculta el área de acciones después de un momento
        if (data.actions_taken && data.actions_taken.length > 0) {
            setTimeout(() => { actionsArea.style.display = 'none'; }, 4000);
        }

    } catch (err) {
        removeTyping(typingId);
        actionsArea.style.display = 'none';
        appendMessage('assistant', `❌ Error: ${err.message}`);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
    }
}

function appendMessage(role, content) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const time = new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
    const avatarText = role === 'assistant' ? 'IA' : 'VOS';

    div.innerHTML = `
        <div class="message-avatar">${avatarText}</div>
        <div class="message-body">
            <div class="message-bubble">${formatMessage(content)}</div>
            <span class="message-time">${time}</span>
        </div>
    `;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function formatMessage(text) {
    // Convierte markdown básico a HTML
    return text
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        .replace(/^### (.+)$/gm, '<strong>$1</strong>')
        .replace(/^## (.+)$/gm, '<strong>$1</strong>')
        .replace(/^# (.+)$/gm, '<strong>$1</strong>')
        .replace(/^[-•]\s(.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^(.+)$/, '<p>$1</p>');
}

function showTyping() {
    const id = 'typing-' + Date.now();
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = id;
    div.innerHTML = `
        <div class="message-avatar">IA</div>
        <div class="message-body">
            <div class="message-bubble">
                <div class="typing-dots"><span></span><span></span><span></span></div>
            </div>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function clearChat() {
    if (!confirm('¿Limpiás la conversación?')) return;
    document.getElementById('chatMessages').innerHTML = '';
    if (sessionId) {
        fetch(`/api/chat/${sessionId}`, { method: 'DELETE' }).catch(() => {});
        sessionId = null;
        document.getElementById('sessionInfo').textContent = '';
    }
    appendMessage('assistant', 'Conversación limpiada. ¿En qué te ayudo?');
}

// ---- Login Modal ----
function openLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

async function doLogin() {
    const user = document.getElementById('loginUser').value.trim();
    const pass = document.getElementById('loginPass').value;
    const btn = document.getElementById('loginBtn');
    const errDiv = document.getElementById('loginError');

    errDiv.style.display = 'none';
    btn.textContent = 'Conectando...';
    btn.disabled = true;

    const indicator = document.getElementById('statusIndicator');
    indicator.className = 'status-dot connecting';

    try {
        const params = new URLSearchParams();
        if (user) params.append('usuario', user);
        if (pass) params.append('password', pass);

        const res = await fetch(`/api/browser/login?${params}`, { method: 'POST' });
        const data = await res.json();

        if (data.autenticado) {
            indicator.className = 'status-dot online';
            closeLoginModal();
            appendMessage('assistant', `✅ Conectado a EJE CLOUD como **${data.usuario || user}**. ¿Qué necesitás consultar?`);

            // Cambia al tab de chat
            document.querySelector('[data-tab="chat"]').click();
        } else {
            indicator.className = 'status-dot offline';
            errDiv.textContent = 'No se pudo conectar a EJE CLOUD. Verificá las credenciales.';
            errDiv.style.display = 'block';
        }
    } catch (err) {
        indicator.className = 'status-dot offline';
        errDiv.textContent = `Error: ${err.message}`;
        errDiv.style.display = 'block';
    } finally {
        btn.textContent = 'Ingresar a EJE CLOUD';
        btn.disabled = false;
    }
}

// ---- Generador de Documentos ----
async function generateDocumentWithAI() {
    const tipo = document.getElementById('docTipo').value;
    const asunto = document.getElementById('docAsunto').value.trim();
    const descripcion = document.getElementById('docDescripcion').value.trim();
    const destinatario = document.getElementById('docDestinatario').value.trim();

    if (!asunto || !descripcion) {
        alert('Completá el asunto y la descripción del documento.');
        return;
    }

    // Construye el mensaje para la IA
    const prompt = `Generá un ${tipo} oficial del GCBA con los siguientes datos:
- Tipo: ${tipo}
- Asunto: ${asunto}
- Destinatario: ${destinatario || 'A quien corresponda'}
- Descripción/Contenido: ${descripcion}

Usá la herramienta generar_documento con un contenido profesional y formal apropiado para un documento oficial del Gobierno de la Ciudad de Buenos Aires.`;

    appendMessage('user', `Generá un ${tipo}: "${asunto}"`);

    // Cambia al tab de chat para ver el resultado
    document.querySelector('[data-tab="chat"]').click();

    await callChatAPI(prompt);
}

async function generateDocumentDirect() {
    const tipo = document.getElementById('docTipo').value;
    const asunto = document.getElementById('docAsunto').value.trim();
    const contenido = document.getElementById('docDescripcion').value.trim();
    const destinatario = document.getElementById('docDestinatario').value.trim();

    if (!asunto || !contenido) {
        alert('Completá el asunto y el contenido.');
        return;
    }

    try {
        const res = await fetch('/api/documentos/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo, asunto, contenido, destinatario }),
        });

        if (!res.ok) throw new Error('Error generando documento');

        const html = await res.text();
        const container = document.getElementById('docPreviewContainer');
        const frame = document.getElementById('docPreviewFrame');
        frame.innerHTML = html;
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

function printDocument() {
    const content = document.getElementById('docPreviewFrame').innerHTML;
    const win = window.open('', '_blank');
    win.document.write(content);
    win.document.close();
    win.print();
}

function copyDocumentHtml() {
    const html = document.getElementById('docPreviewFrame').innerHTML;
    navigator.clipboard.writeText(html).then(() => {
        alert('HTML copiado al portapapeles');
    });
}

// ---- Ayuda: ejemplos ----
function useExample(el) {
    const text = el.querySelector('code').textContent;
    document.querySelector('[data-tab="chat"]').click();
    document.getElementById('chatInput').value = text;
    document.getElementById('chatInput').focus();
}

// ---- Cerrar modal con Escape ----
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeLoginModal();
});
