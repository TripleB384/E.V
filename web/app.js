const log = document.getElementById("log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");

const STORAGE_KEY = "ev.conversation_id";
let conversationId = sessionStorage.getItem(STORAGE_KEY) || null;

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `msg msg-${role}`;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  input.disabled = true;
  addMessage("user", message);
  const pending = addMessage("assistant pending", "…");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });

    if (!res.ok) {
      const detail = await res.text();
      throw new Error(`${res.status}: ${detail}`);
    }

    const data = await res.json();
    conversationId = data.conversation_id;
    sessionStorage.setItem(STORAGE_KEY, conversationId);
    pending.textContent = data.reply;
    pending.className = "msg msg-assistant";
  } catch (err) {
    pending.textContent = `Error talking to E.V: ${err.message}`;
    pending.className = "msg msg-error";
  } finally {
    input.disabled = false;
    input.focus();
  }
});
