(function () {
  var root = document.getElementById("fits-sitewide-chatbot-root");
  if (!root || window.__fitsSitewideChatbotMounted) {
    return;
  }
  window.__fitsSitewideChatbotMounted = true;

  var storageKey = "fits_sitewide_chatbot_history_v1";
  var apiUrl = root.dataset.apiUrl;
  var quickPrompts = [
    "Where can I view the organization hierarchy?",
    "Where do I manage payslips?",
    "How do I open the recruitment pipeline?",
    "Where can I find succession planning?"
  ];

  function loadHistory() {
    try {
      var parsed = JSON.parse(localStorage.getItem(storageKey) || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  }

  function saveHistory(messages) {
    localStorage.setItem(storageKey, JSON.stringify(messages.slice(-12)));
  }

  function createEl(tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (typeof text === "string") el.textContent = text;
    return el;
  }

  function renderLinks(container, links) {
  if (!links || !links.length) return;

  var wrap = createEl("div", "fits-chatbot__links");

  links.slice(0, 4).forEach(function (link) {
    var a = createEl("a", "fits-chatbot__link");
    a.href = link.url;
    a.target = "_blank";

    var title = createEl("div", "fits-chatbot__link-title", link.title);
    var meta = createEl("div", "fits-chatbot__link-meta", new URL(link.url).pathname);

    a.appendChild(title);
    a.appendChild(meta);

    wrap.appendChild(a);
  });

  container.appendChild(wrap);
}

  function renderMessage(messagesEl, item) {
    var message = createEl("div", "fits-chatbot__message fits-chatbot__message--" + item.role);
    var bubble = createEl("div", "fits-chatbot__bubble");
    bubble.innerHTML = formatMessage(item.content);
    message.appendChild(bubble);

    if (item.role === "assistant" && item.links) {
      renderLinks(message, item.links);
    }

    messagesEl.appendChild(message);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function mount() {
    var state = {
      open: false,
      busy: false,
      history: loadHistory()
    };

    var shell = createEl("section", "fits-chatbot");
    shell.innerHTML = [
      '<button type="button" class="fits-chatbot__launcher" aria-label="Open FITS assistant">AI</button>',
      '<div class="fits-chatbot__panel" role="dialog" aria-label="FITS HCMS assistant">',
      '  <div class="fits-chatbot__header">',
      '    <div class="fits-chatbot__title">Hi I am Ahmed, your AI assistant!</div>',
      '    <div class="fits-chatbot__subtitle">Ask about product features and page links.</div>',
      "  </div>",
      '  <div class="fits-chatbot__messages"></div>',
      '  <div class="fits-chatbot__composer">',
      '    <div class="fits-chatbot__quick-actions"></div>',
      '    <div class="fits-chatbot__input-row">',
      '      <textarea class="fits-chatbot__textarea" placeholder="Ask where to find a feature, page, or workflow."></textarea>',
      '      <button type="button" class="fits-chatbot__send">Send</button>',
      "    </div>",
      '    <div class="fits-chatbot__status">Powered by local product knowledge and OpenRouter when configured.</div>',
      "  </div>",
      "</div>"
    ].join("");

    var launcher = shell.querySelector(".fits-chatbot__launcher");
    var messagesEl = shell.querySelector(".fits-chatbot__messages");
    var quickActionsEl = shell.querySelector(".fits-chatbot__quick-actions");
    var textarea = shell.querySelector(".fits-chatbot__textarea");
    var sendButton = shell.querySelector(".fits-chatbot__send");
    var statusEl = shell.querySelector(".fits-chatbot__status");

    function setBusy(busy, statusText) {
      state.busy = busy;
      sendButton.disabled = busy;
      textarea.disabled = busy;
      statusEl.textContent = statusText || "Powered by local product knowledge and OpenRouter when configured.";
    }
       


    function formatMessage(text) {
  if (!text) return "";

  // Convert URLs into clickable links
  text = text.replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" target="_blank" style="color:#1e88e5;">$1</a>'
  );

  // Add spacing for readability
  text = text.replace(/\n/g, "<br>");

  return text;
}

   function appendMessage(role, content, links) {
  // REMOVE raw URLs from content (since we show them separately)
  if (role === "assistant") {
    content = content.replace(/https?:\/\/[^\s]+/g, "").trim();
  }

  var item = { role, content, links: links || [] };
  state.history.push(item);
  saveHistory(state.history);
  renderMessage(item);
}

    function bootstrapMessages() {
      if (!state.history.length) {
        appendMessage(
          "assistant",
          "I can answer product questions about FITS HCMS and point you to the right page. Try asking where to find org charts, payslips, recruitment pipeline, EOSB, WPS, learning, or succession planning."
        );
        return;
      }

      state.history.forEach(function (item) {
        renderMessage(messagesEl, item);
      });
    }

    function toggle() {
      state.open = !state.open;
      shell.classList.toggle("fits-chatbot--open", state.open);
      if (state.open) {
        textarea.focus();
      }
    }

    function sendMessage(promptText) {
      var message = (promptText || textarea.value || "").trim();
      if (!message || state.busy) return;

      if (!promptText) {
        textarea.value = "";
      }

      appendMessage("user", message);
      setBusy(true, "Thinking...");

      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: message,
          current_path: window.location.pathname,
          current_title: document.title,
          history: state.history.slice(-8).map(function (item) {
            return { role: item.role, content: item.content };
          })
        })
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Chat request failed with status " + response.status);
          }
          return response.json();
        })
        .then(function (payload) {
          appendMessage("assistant", payload.answer || "I could not generate a response.", payload.links || []);
          var suffix = payload.model ? " via " + payload.model : "";
          statusEl.textContent = payload.mode === "openrouter"
            ? "Answered with OpenRouter" + suffix + "."
            : "Answered from the local FITS HCMS product map.";
        })
        .catch(function (error) {
          appendMessage(
            "assistant",
            "I ran into a problem while answering that. Please try again."
          );
          statusEl.textContent = error.message;
        })
        .finally(function () {
          setBusy(false);
          textarea.focus();
        });
    }

    quickPrompts.forEach(function (prompt) {
      var button = createEl("button", "fits-chatbot__quick-action", prompt);
      button.type = "button";
      button.addEventListener("click", function () {
        sendMessage(prompt);
      });
      quickActionsEl.appendChild(button);
    });

    launcher.addEventListener("click", toggle);
    sendButton.addEventListener("click", function () {
      sendMessage();
    });
    textarea.addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });

    bootstrapMessages();
    document.body.appendChild(shell);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
