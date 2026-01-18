(() => {
  const storageKey = "pq_admin_hotkeys";
  const form = document.querySelector("[data-role='settings-form']");
  const resetButton = document.querySelector("[data-action='reset']");
  const inputs = {
    bold: form.querySelector("[name='bold']"),
    italic: form.querySelector("[name='italic']"),
    code_block: form.querySelector("[name='code_block']"),
  };

  const defaults = {
    bold: "CTRL+B",
    italic: "CTRL+I",
    code_block: "CTRL+ALT+L",
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

  const loadSettings = () => {
    const raw = window.localStorage.getItem(storageKey);
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

  const applySettings = (settings) => {
    inputs.bold.value = settings.bold;
    inputs.italic.value = settings.italic;
    inputs.code_block.value = settings.code_block;
  };

  const saveSettings = () => {
    const payload = {
      bold: normalizeCombo(inputs.bold.value || defaults.bold),
      italic: normalizeCombo(inputs.italic.value || defaults.italic),
      code_block: normalizeCombo(inputs.code_block.value || defaults.code_block),
    };
    window.localStorage.setItem(storageKey, JSON.stringify(payload));
    applySettings(payload);
  };

  Object.values(inputs).forEach((input) => {
    input.addEventListener("keydown", (event) => {
      event.preventDefault();
      if (["Control", "Shift", "Alt", "Meta"].includes(event.key)) {
        return;
      }
      const combo = eventCombo(event);
      if (!combo) {
        return;
      }
      input.value = combo;
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    saveSettings();
  });

  resetButton.addEventListener("click", () => {
    window.localStorage.setItem(storageKey, JSON.stringify(defaults));
    applySettings(defaults);
  });

  applySettings(loadSettings());
})();
