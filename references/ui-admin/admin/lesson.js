(() => {
  const apiBase = "/api/v1/lessons";
  const form = document.querySelector("[data-role='lesson-form']");
  const editorTitle = document.querySelector("[data-role='editor-title']");
  const editorStatus = document.querySelector("[data-role='editor-status']");
  const message = document.querySelector("[data-role='message']");
  const messageText = document.querySelector("[data-role='message-text']");
  const preview = document.querySelector("[data-role='preview']");
  const deleteButton = document.querySelector("[data-action='delete']");
  const resetButton = document.querySelector("[data-action='reset']");
  const toolbarButtons = document.querySelectorAll(".toolbar__btn");
  const toolbarToggle = document.querySelector("[data-action='toggle-toolbar']");
  const markdownEditor = document.querySelector(".markdown-editor");

  let activeId = null;
  const hotkeyStorageKey = "pq_admin_hotkeys";
  const toolbarStorageKey = "pq_admin_toolbar_hidden";
  const defaultMarkdown = `# Lesson title

Plain text paragraph to show base typography.

## Formatting examples

**Bold text** and *italic text* in the same line.

Inline code looks like \`user_id\`.

> Block quote to highlight a tip or warning.

- Bullet item one
- Bullet item two
- Bullet item three

\`\`\`python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
\`\`\`
`;

  const fields = {
    order: form.querySelector("[name='order']"),
    slug: form.querySelector("[name='slug']"),
    name: form.querySelector("[name='name']"),
    body_markdown: form.querySelector("[name='body_markdown']"),
    expected_output: form.querySelector("[name='expected_output']"),
  };

  const setMessage = (text, tone = "muted") => {
    if (!message || !messageText) {
      return;
    }
    message.classList.toggle("muted", tone === "muted");
    messageText.textContent = text;
  };

  const setEditorStatus = (text) => {
    if (!editorStatus) {
      return;
    }
    editorStatus.textContent = text;
  };

  const escapeHtml = (value) => {
    return value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  };

  const highlightPython = (code) => {
    const keywords = new Set([
      "False", "None", "True", "and", "as", "assert", "async", "await", "break",
      "class", "continue", "def", "del", "elif", "else", "except", "finally",
      "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
      "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
    ]);

    const highlightCodeSegment = (value) => {
      let result = "";
      let lastIndex = 0;
      let expectTitle = false;
      const tokenRegex = /([A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?)/g;
      let match = tokenRegex.exec(value);

      while (match) {
        const token = match[0];
        const start = match.index;
        const end = start + token.length;
        result += escapeHtml(value.slice(lastIndex, start));
        if (/^\d/.test(token)) {
          result += `<span class="hljs-number">${token}</span>`;
        } else if (expectTitle) {
          result += `<span class="hljs-title">${token}</span>`;
          expectTitle = false;
        } else if (keywords.has(token)) {
          result += `<span class="hljs-keyword">${token}</span>`;
          if (token === "class" || token === "def") {
            expectTitle = true;
          }
        } else {
          result += token;
        }
        lastIndex = end;
        match = tokenRegex.exec(value);
      }
      result += escapeHtml(value.slice(lastIndex));
      return result;
    };

    const tokens = [];
    let index = 0;

    while (index < code.length) {
      const char = code[index];

      if (char === "#" ) {
        let end = code.indexOf("\n", index);
        if (end === -1) {
          end = code.length;
        }
        tokens.push({ type: "comment", text: code.slice(index, end) });
        index = end;
        continue;
      }

      if (char === "\"" || char === "'") {
        const quote = char;
        const triple = code.slice(index, index + 3) === quote.repeat(3);
        let end = index + (triple ? 3 : 1);
        while (end < code.length) {
          if (code[end] === "\\" && !triple) {
            end += 2;
            continue;
          }
          if (triple && code.slice(end, end + 3) === quote.repeat(3)) {
            end += 3;
            break;
          }
          if (!triple && code[end] === quote) {
            end += 1;
            break;
          }
          end += 1;
        }
        tokens.push({ type: "string", text: code.slice(index, end) });
        index = end;
        continue;
      }

      tokens.push({ type: "code", text: char });
      index += 1;
    }

    const merged = [];
    for (const token of tokens) {
      if (token.type === "code" && merged.length && merged[merged.length - 1].type === "code") {
        merged[merged.length - 1].text += token.text;
      } else {
        merged.push(token);
      }
    }

    const highlighted = merged.map((token) => {
      if (token.type === "comment") {
        return `<span class="hljs-comment">${escapeHtml(token.text)}</span>`;
      }
      if (token.type === "string") {
        return `<span class="hljs-string">${escapeHtml(token.text)}</span>`;
      }

      return highlightCodeSegment(token.text);
    });

    return highlighted.join("");
  };

  const updatePreview = () => {
    if (!window.marked) {
      preview.textContent = fields.body_markdown.value || "";
      return;
    }
    preview.innerHTML = window.marked.parse(fields.body_markdown.value || "");
    preview.querySelectorAll("pre code").forEach((block) => {
      block.classList.add("language-python", "hljs");
      block.innerHTML = highlightPython(block.textContent || "");
    });
  };

  const resetForm = () => {
    form.reset();
    activeId = null;
    editorTitle.textContent = "Create lesson";
    setEditorStatus("idle");
    fields.body_markdown.value = defaultMarkdown;
    updatePreview();
  };

  const populateForm = (lesson) => {
    fields.order.value = lesson.order ?? "";
    fields.slug.value = lesson.slug ?? "";
    fields.name.value = lesson.name ?? "";
    fields.body_markdown.value = lesson.body_markdown ?? "";
    fields.expected_output.value = lesson.expected_output ?? "";
    activeId = lesson.id;
    editorTitle.textContent = "Edit lesson";
    setEditorStatus(`editing ${lesson.slug}`);
    updatePreview();
  };

  const loadLesson = async (lessonId) => {
    if (!lessonId) {
      return;
    }
    setMessage("loading lesson...", "muted");
    try {
      const response = await fetch(`${apiBase}/${lessonId}`);
      if (!response.ok) {
        throw new Error("failed to load lesson");
      }
      const data = await response.json();
      populateForm(data);
      setMessage("lesson loaded", "muted");
    } catch (error) {
      setMessage("failed to load lesson", "muted");
    }
  };

  const saveLesson = async () => {
    const payload = {
      order: Number(fields.order.value),
      slug: fields.slug.value.trim(),
      name: fields.name.value.trim(),
      body_markdown: fields.body_markdown.value,
      expected_output: fields.expected_output.value,
    };

    const hasRequired = payload.order && payload.slug && payload.name;
    if (!hasRequired) {
      setMessage("order, slug, and title are required", "muted");
      return;
    }

    setEditorStatus("saving...");
    const isUpdate = Boolean(activeId);
    const url = isUpdate ? `${apiBase}/${activeId}` : `${apiBase}/create`;
    const method = isUpdate ? "PUT" : "POST";

    try {
      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("save failed");
      }

      const saved = await response.json();
      setMessage("lesson saved", "muted");
      populateForm(saved);
    } catch (error) {
      setMessage("save failed", "muted");
      setEditorStatus("error");
    }
  };

  const deleteLesson = async () => {
    if (!activeId) {
      return;
    }
    if (!window.confirm("Delete this lesson?")) {
      return;
    }

    setMessage("deleting...", "muted");
    try {
      const response = await fetch(`${apiBase}/${activeId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("delete failed");
      }

      setMessage("lesson deleted", "muted");
      window.location.href = "./index.html";
    } catch (error) {
      setMessage("delete failed", "muted");
    }
  };

  const insertAtCursor = (textarea, text) => {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const before = textarea.value.substring(0, start);
    const after = textarea.value.substring(end);
    textarea.value = `${before}${text}${after}`;
    textarea.selectionStart = start + text.length;
    textarea.selectionEnd = start + text.length;
    textarea.focus();
    updatePreview();
  };

  const wrapSelection = (textarea, left, right, placeholder) => {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = textarea.value.substring(start, end);
    const value = selected || placeholder;
    const before = textarea.value.substring(0, start);
    const after = textarea.value.substring(end);
    textarea.value = `${before}${left}${value}${right}${after}`;
    textarea.selectionStart = start + left.length;
    textarea.selectionEnd = textarea.selectionStart + value.length;
    textarea.focus();
    updatePreview();
  };

  const applyFormat = (action, textarea) => {
    if (action === "bold") {
      wrapSelection(textarea, "**", "**", "bold");
      return;
    }
    if (action === "italic") {
      wrapSelection(textarea, "*", "*", "italic");
      return;
    }
    if (action === "code") {
      wrapSelection(textarea, "`", "`", "code");
      return;
    }
    if (action === "code_block") {
      wrapSelection(textarea, "```\n", "\n```", "code");
      return;
    }
    if (action === "link") {
      wrapSelection(textarea, "[", "](https://)", "label");
      return;
    }
    const map = {
      h2: "\n## Heading\n",
      quote: "\n> quote\n",
      ul: "\n- item\n- item\n"
    };
    insertAtCursor(textarea, map[action] || "");
  };

  const normalizeCombo = (combo) => {
    return combo
      .replace(/\s+/g, "")
      .replace(/Cmd/i, "Meta")
      .replace(/Command/i, "Meta")
      .replace(/Control/i, "Ctrl")
      .toUpperCase();
  };

  const eventCombo = (event) => {
    const parts = [];
    if (event.ctrlKey) {
      parts.push("CTRL");
    }
    if (event.altKey) {
      parts.push("ALT");
    }
    if (event.shiftKey) {
      parts.push("SHIFT");
    }
    if (event.metaKey) {
      parts.push("META");
    }
    const key = event.key.toUpperCase();
    if (!["CONTROL", "SHIFT", "ALT", "META"].includes(key)) {
      parts.push(key);
    }
    return parts.join("+");
  };

  const getHotkeys = () => {
    const defaults = {
      bold: "CTRL+B",
      italic: "CTRL+I",
      code_block: "CTRL+ALT+L",
    };
    const raw = window.localStorage.getItem(hotkeyStorageKey);
    if (!raw) {
      return defaults;
    }
    try {
      const parsed = JSON.parse(raw);
      return {
        bold: normalizeCombo(parsed.bold || defaults.bold),
        italic: normalizeCombo(parsed.italic || defaults.italic),
        code_block: normalizeCombo(parsed.code_block || defaults.code_block),
      };
    } catch (error) {
      return defaults;
    }
  };

  const hotkeys = getHotkeys();

  const handleToolbar = (event) => {
    const action = event.currentTarget.dataset.md;
    const textarea = fields.body_markdown;
    applyFormat(action, textarea);
  };

  const setToolbarHidden = (hidden) => {
    if (!markdownEditor || !toolbarToggle) {
      return;
    }
    markdownEditor.classList.toggle("markdown-editor--compact", hidden);
    toolbarToggle.textContent = hidden ? "show tools" : "hide tools";
    window.localStorage.setItem(toolbarStorageKey, String(hidden));
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    saveLesson();
  });

  deleteButton.addEventListener("click", () => {
    deleteLesson();
  });

  resetButton.addEventListener("click", () => {
    resetForm();
  });

  fields.body_markdown.addEventListener("input", () => {
    updatePreview();
  });

  fields.body_markdown.addEventListener("keydown", (event) => {
    const combo = eventCombo(event);
    if (combo === hotkeys.bold) {
      event.preventDefault();
      applyFormat("bold", fields.body_markdown);
    }
    if (combo === hotkeys.italic) {
      event.preventDefault();
      applyFormat("italic", fields.body_markdown);
    }
    if (combo === hotkeys.code_block) {
      event.preventDefault();
      applyFormat("code_block", fields.body_markdown);
    }
  });

  toolbarButtons.forEach((button) => {
    if (button.dataset.action === "toggle-toolbar") {
      return;
    }
    button.addEventListener("click", handleToolbar);
  });

  if (toolbarToggle) {
    toolbarToggle.addEventListener("click", () => {
      const hidden = markdownEditor?.classList.contains("markdown-editor--compact");
      setToolbarHidden(!hidden);
    });
  }

  const params = new URLSearchParams(window.location.search);
  const lessonId = params.get("id");
  const toolbarHidden = window.localStorage.getItem(toolbarStorageKey) === "true";
  setToolbarHidden(toolbarHidden);
  if (lessonId) {
    loadLesson(lessonId);
  } else {
    resetForm();
  }
})();
