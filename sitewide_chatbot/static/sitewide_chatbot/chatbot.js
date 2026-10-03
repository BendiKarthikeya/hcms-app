(function () {
  var shell = document.getElementById("fits-sitewide-chatbot");
  if (!shell || window.__fitsSitewideChatbotMounted) return;
  window.__fitsSitewideChatbotMounted = true;

  var storageKey = "fits_sitewide_chatbot_history_v2";
  var panelStateKey = "fits_chatbot_panel_open";
  var apiUrl = new URL(shell.dataset.apiUrl, window.location.origin).toString();

  var launcher = shell.querySelector(".fits-chatbot__launcher");
  var panel = shell.querySelector(".fits-chatbot__panel");
  var header = shell.querySelector(".fits-chatbot__header");
  var messagesEl = shell.querySelector(".fits-chatbot__messages");
  var quickActions = shell.querySelectorAll(".fits-chatbot__quick-action");
  var textarea = shell.querySelector(".fits-chatbot__textarea");
  var sendButton = shell.querySelector(".fits-chatbot__send");
  var resetButton = shell.querySelector(".fits-chatbot__reset");

  var state = {
    open: false,
    busy: false,
    history: loadHistory()
  };

  function loadHistory() {
    try {
      var parsed = JSON.parse(localStorage.getItem(storageKey) || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch { return []; }
  }

  function saveHistory(messages) {
    localStorage.setItem(storageKey, JSON.stringify(messages.slice(-12)));
  }

  function createEl(tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }

  // ── Thinking indicator ──────────────────────────────────────────
  function showThinking() {
    var msg = createEl("div", "fits-chatbot__message fits-chatbot__message--assistant");
    var bubble = createEl("div", "fits-chatbot__bubble fits-chatbot__thinking-bubble");

    var dots = createEl("div", "fits-chatbot__dots");
    dots.appendChild(createEl("span", "fits-chatbot__dot"));
    dots.appendChild(createEl("span", "fits-chatbot__dot"));
    dots.appendChild(createEl("span", "fits-chatbot__dot"));
    bubble.appendChild(dots);

    var label = createEl("span", "fits-chatbot__thinking-label", "Thinking…");
    bubble.appendChild(label);

    msg.appendChild(bubble);
    messagesEl.appendChild(msg);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return msg;
  }

  // ── Word-by-word typewriter ─────────────────────────────────────
  function typeText(container, text, onDone) {
    // Split on whitespace but keep the whitespace tokens so spacing is preserved
    var tokens = text.split(/(\s+)/);
    var wordCount = tokens.filter(function(t) { return t.trim(); }).length;
    // Faster for long answers so it doesn't drag
    var speed = wordCount > 80 ? 18 : wordCount > 40 ? 28 : 38;
    var idx = 0;

    function next() {
      if (idx >= tokens.length) {
        if (onDone) onDone();
        return;
      }
      var token = tokens[idx++];
      var span = document.createElement("span");
      if (token.trim()) {
        span.className = "fits-chatbot__word";
      }
      span.textContent = token;
      container.appendChild(span);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      // Whitespace tokens get tiny delay, word tokens get full delay
      setTimeout(next, token.trim() ? speed : 4);
    }
    next();
  }

  // ── Render pills ────────────────────────────────────────────────
  function renderPills(container, links) {
    if (!links || !links.length) return;
    var wrap = createEl("div", "fits-chatbot__nav-pills");

    links.slice(0, 5).forEach(function (link) {
      var btn = createEl("button", "fits-chatbot__nav-pill");
      btn.type = "button";
      btn.title = link.description || link.title;
      btn.textContent = link.title;
      btn.addEventListener("click", function () {
        var dest = link.path || link.url;
        if (dest) {
          localStorage.setItem(panelStateKey, "1");
          window.location.href = dest;
        }
      });
      wrap.appendChild(btn);
    });

    // Fade the pills in after a brief pause
    wrap.style.opacity = "0";
    container.appendChild(wrap);
    setTimeout(function() {
      wrap.style.transition = "opacity 0.35s ease";
      wrap.style.opacity = "1";
    }, 60);
  }

  // ── Render (instant, used for history replay) ───────────────────
  function renderMessage(item) {
    var msg = createEl("div", "fits-chatbot__message fits-chatbot__message--" + item.role);
    var bubble = createEl("div", "fits-chatbot__bubble", item.content);
    msg.appendChild(bubble);
    if (item.role === "assistant") renderPills(msg, item.links);
    messagesEl.appendChild(msg);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // ── Animated assistant message ──────────────────────────────────
  function appendAnimatedAssistant(text, links) {
    var item = { role: "assistant", content: text, links: links || [] };
    state.history.push(item);
    saveHistory(state.history);

    var msg = createEl("div", "fits-chatbot__message fits-chatbot__message--assistant");
    var bubble = createEl("div", "fits-chatbot__bubble");
    msg.appendChild(bubble);
    messagesEl.appendChild(msg);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    typeText(bubble, text, function () {
      renderPills(msg, links);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    });
  }

  function appendMessage(role, content, links) {
    var item = { role: role, content: content, links: links || [] };
    state.history.push(item);
    saveHistory(state.history);
    renderMessage(item);
  }

  function setBusy(busy) {
    state.busy = busy;
    sendButton.disabled = busy;
    textarea.disabled = busy;
  }

  function resetChat() {
    state.history = [];
    saveHistory(state.history);
    messagesEl.innerHTML = "";
    textarea.value = "";
    bootstrapMessages();
  }

  function bootstrapMessages() {
    if (!state.history.length) {
      appendMessage("assistant", "Hi, I am Ahmed, your AI assistant. How may I help you today?");
    } else {
      state.history.forEach(renderMessage);
    }
  }

  function toggle() {
    state.open = !state.open;
    shell.classList.toggle("fits-chatbot--open", state.open);
    localStorage.setItem(panelStateKey, state.open ? "1" : "0");
    if (state.open) textarea.focus();
  }

  // ── Send ────────────────────────────────────────────────────────
  function sendMessage(promptText) {
    var message = (promptText || textarea.value).trim();
    if (!message || state.busy) return;

    textarea.value = "";
    appendMessage("user", message);
    setBusy(true);

    var thinkingEl = showThinking();

    fetch(apiUrl, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
      },
      body: JSON.stringify({
        message: message,
        current_path: window.location.pathname,
        current_title: document.title,
        history: state.history.slice(-8).map(function(item) {
          return { role: item.role, content: item.content };
        })
      })
    })
      .then(function(res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function(data) {
        thinkingEl.remove();
        appendAnimatedAssistant(
          data.answer || data.response || "No response",
          data.links || []
        );
      })
      .catch(function(err) {
        thinkingEl.remove();
        console.error("CHATBOT ERROR:", err);
        appendMessage("assistant", "Sorry, something went wrong. Please try again.");
      })
      .finally(function() {
        setBusy(false);
        textarea.focus();
      });
  }

  // ── Events ──────────────────────────────────────────────────────
  launcher.addEventListener("click", toggle);
  var closeBtn = shell.querySelector(".fits-chatbot__close");
  if (closeBtn) closeBtn.addEventListener("click", toggle);
  sendButton.addEventListener("click", function() { sendMessage(); });

  textarea.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  quickActions.forEach(function(btn) {
    if (btn.classList.contains("fits-chatbot__reset")) return;
    btn.addEventListener("click", function() {
      sendMessage((btn.dataset.prompt || btn.textContent).trim());
    });
  });

  if (resetButton) {
    resetButton.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      resetChat();
    });
  }

  shell.addEventListener("click", function(e) {
    if (e.target.classList.contains("fits-chatbot__reset") || e.target.closest(".fits-chatbot__reset")) {
      e.preventDefault();
      e.stopPropagation();
      resetChat();
    }
  });

  // ── Draggable ───────────────────────────────────────────────────
  var isDragging = false, offsetX = 0, offsetY = 0;

  header.addEventListener("mousedown", function(e) {
    isDragging = true;
    offsetX = e.clientX - panel.getBoundingClientRect().left;
    offsetY = e.clientY - panel.getBoundingClientRect().top;
  });

  document.addEventListener("mousemove", function(e) {
    if (!isDragging) return;
    panel.style.position = "fixed";
    panel.style.left = (e.clientX - offsetX) + "px";
    panel.style.top = (e.clientY - offsetY) + "px";
  });

  document.addEventListener("mouseup", function() { isDragging = false; });

  // ── Init ────────────────────────────────────────────────────────
  if (localStorage.getItem(panelStateKey) === "1") {
    state.open = true;
    shell.classList.add("fits-chatbot--open");
    textarea.focus();
  }

  bootstrapMessages();
})();
