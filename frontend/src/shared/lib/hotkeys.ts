export interface MarkdownHotkeys {
  bold: string;
  italic: string;
  codeBlock: string;
}

const storageKey = "pq_admin_hotkeys";

const normalizeCombo = (combo: string): string => {
  return combo
    .replace(/\s+/g, "")
    .replace(/Cmd/i, "Meta")
    .replace(/Command/i, "Meta")
    .replace(/Control/i, "Ctrl")
    .toUpperCase();
};

export const defaultHotkeys: MarkdownHotkeys = {
  bold: "CTRL+B",
  italic: "CTRL+I",
  codeBlock: "CTRL+ALT+L",
};

export const loadHotkeys = (): MarkdownHotkeys => {
  const raw = window.localStorage.getItem(storageKey);
  if (!raw) {
    return defaultHotkeys;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<MarkdownHotkeys>;
    return {
      bold: normalizeCombo(parsed.bold || defaultHotkeys.bold),
      italic: normalizeCombo(parsed.italic || defaultHotkeys.italic),
      codeBlock: normalizeCombo(parsed.codeBlock || defaultHotkeys.codeBlock),
    };
  } catch {
    return defaultHotkeys;
  }
};

export const saveHotkeys = (hotkeys: MarkdownHotkeys): void => {
  window.localStorage.setItem(storageKey, JSON.stringify(hotkeys));
};

export const normalizeHotkey = (combo: string): string => {
  return normalizeCombo(combo);
};

export const eventToCombo = (event: KeyboardEvent): string => {
  const parts: string[] = [];
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
