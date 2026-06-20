const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const resetButton = document.getElementById("resetButton");

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}

function addUserMessage(text) {
  messages.insertAdjacentHTML("beforeend", `<article class="message user-message"><div class="bubble"><p>${escapeHtml(text)}</p></div></article>`);
  scrollDown();
}

function addTyping() {
  const id = `typing-${Date.now()}`;
  messages.insertAdjacentHTML("beforeend", `<article id="${id}" class="message bot-message"><div class="avatar">C</div><div class="bubble"><p class="typing"><span></span><span></span><span></span></p></div></article>`);
  scrollDown();
  return id;
}

function addBotMessage(data) {
  const courses = (data.courses || []).map(course => `
    <div class="course-card">
      <h3>${escapeHtml(course.title)}</h3>
      <span class="tag">${escapeHtml(course.level)}</span><span class="tag">${escapeHtml(course.duration)}</span>
      <p>${escapeHtml(course.description)}</p>
    </div>`).join("");
  const confidence = Math.round((data.confidence || 0) * 100);
  messages.insertAdjacentHTML("beforeend", `
    <article class="message bot-message">
      <div class="avatar">C</div>
      <div class="bubble">
        <p>${escapeHtml(data.reply)}</p>
        ${courses ? `<div class="course-grid">${courses}</div>` : ""}
        <div class="meta">Intent: ${escapeHtml(data.intent)} · Confidence: ${confidence}% · Sentiment: ${escapeHtml(data.sentiment)}</div>
      </div>
    </article>`);
  scrollDown();
}

function scrollDown() { messages.scrollTop = messages.scrollHeight; }

async function sendMessage(text) {
  const clean = text.trim();
  if (!clean || sendButton.disabled) return;
  addUserMessage(clean);
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;
  const typingId = addTyping();
  try {
    const response = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: clean }) });
    const data = await response.json();
    document.getElementById(typingId)?.remove();
    if (!response.ok) throw new Error(data.error || "Something went wrong.");
    addBotMessage(data);
  } catch (error) {
    document.getElementById(typingId)?.remove();
    addBotMessage({ reply: error.message, intent: "Error", confidence: 0, sentiment: "Neutral", courses: [] });
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", event => { event.preventDefault(); sendMessage(input.value); });
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
});
input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = `${Math.min(input.scrollHeight, 120)}px`; });
document.querySelectorAll(".suggestions button").forEach(button => button.addEventListener("click", () => sendMessage(button.textContent)));
resetButton.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  messages.innerHTML = `<article class="message bot-message"><div class="avatar">C</div><div class="bubble"><p>Fresh start. Tell me what you would like to learn.</p></div></article>`;
  input.focus();
});

