import { useMemo, useState, type ReactElement } from "react";

import { defaultHotkeys, loadHotkeys, normalizeHotkey, saveHotkeys, type MarkdownHotkeys } from "@shared/lib/hotkeys";
import { Button } from "@shared/ui/Button";
import { Input } from "@shared/ui/Input";
import { useToast } from "@shared/lib/useToast";
import { Notice } from "@shared/ui/Notice";

const captureCombo = (event: React.KeyboardEvent<HTMLInputElement>): string => {
  event.preventDefault();
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

export const AdminSettingsPage = (): ReactElement => {
  const initial = useMemo(() => loadHotkeys(), []);
  const [values, setValues] = useState<MarkdownHotkeys>(initial);
  const { toasts, showToast } = useToast({ durationMs: 1000 });

  const updateField = (key: keyof MarkdownHotkeys, value: string) => {
    setValues((prev) => ({ ...prev, [key]: normalizeHotkey(value) }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    saveHotkeys(values);
    showToast({ message: "Hotkeys saved", variant: "success" });
  };

  const handleReset = () => {
    setValues(defaultHotkeys);
    saveHotkeys(defaultHotkeys);
    showToast({ message: "Hotkeys reset", variant: "success" });
  };

  return (
    <div className="admin-page">
      <div className="panel__header">
        <div>
          <p className="eyebrow">preferences</p>
          <h1>Markdown editor hotkeys</h1>
        </div>
      </div>

      <div className="settings-body">
        <div className="settings-card">
          <p className="muted">Click a field and press the shortcut you want to use.</p>
          {toasts.length > 0 && (
            <div className="toast-stack">
              {toasts.map((toast) => (
                <Notice key={toast.id} message={toast.message} variant={toast.variant} />
              ))}
            </div>
          )}
          <form className="settings-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Bold</span>
              <Input
                value={values.bold}
                onKeyDown={(event) => updateField("bold", captureCombo(event))}
                onChange={(event) => updateField("bold", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Italic</span>
              <Input
                value={values.italic}
                onKeyDown={(event) => updateField("italic", captureCombo(event))}
                onChange={(event) => updateField("italic", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Code block</span>
              <Input
                value={values.codeBlock}
                onKeyDown={(event) => updateField("codeBlock", captureCombo(event))}
                onChange={(event) => updateField("codeBlock", event.target.value)}
              />
            </label>
            <div className="form-actions">
              <Button variant="ghost" type="button" onClick={handleReset}>
                reset defaults
              </Button>
              <Button variant="accent" type="submit">
                save hotkeys
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
