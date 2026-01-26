import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { useLesson } from "@features/admin-lessons/hooks/useLesson";
import { useLessonForm } from "@features/admin-lessons/hooks/useLessonForm";
import { MarkdownEditor } from "@features/admin-lessons/ui/MarkdownEditor";
import { SampleCasesEditor } from "@features/admin-lessons/ui/SampleCasesEditor";
import { createLesson, deleteLesson, updateLesson } from "@shared/api/lessonApi";
import { loadHotkeys } from "@shared/lib/hotkeys";
import { type ToastVariant, useToast } from "@shared/lib/useToast";
import { Button } from "@shared/ui/Button";
import { CodeEditor } from "@shared/ui/CodeEditor";
import { Input } from "@shared/ui/Input";
import { Notice } from "@shared/ui/Notice";
import { Textarea } from "@shared/ui/Textarea";

interface LocationState {
  toast?: {
    message: string;
    variant: ToastVariant;
  };
}

export const AdminLessonEditorPage = (): ReactElement => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { data, isLoading, error } = useLesson(lessonId ?? null);
  const { values, updateField, reset } = useLessonForm(data);
  const [saving, setSaving] = useState(false);
  const [toolbarHidden, setToolbarHidden] = useState(false);
  const [activeSection, setActiveSection] = useState<"content" | "execution">("content");
  const { toasts, showToast } = useToast({ durationMs: 1000 });

  const hotkeys = useMemo(() => loadHotkeys(), []);
  const evalScriptTemplate = useMemo(
    () =>
      [
        "import json",
        "",
        "{{USER_CODE}}",
        "",
        "class Case:",
        "  \"\"\"",
        "  wrapper that turns a case function into a uniform result",
        "  \"\"\"",
        "  def __init__(self, name, fn):",
        "    # name must match the sample case name in admin UI",
        "    # the UI uses this name to map results to labels",
        "    self.name = name",
        "    self.fn = fn",
        "",
        "  def run(self):",
        "    # execute the case and return a normalized result",
        "    # each case must return: (ok: bool, reason: str | None)",
        "    # ok = passed/failed, reason = short failure hint or None",
        "    ok, reason = self.fn()",
        "    return {\"name\": self.name, \"ok\": ok, \"reason\": reason}",
        "",
        "def case_one():",
        "  \"\"\"",
        "  first test case",
        "  \"\"\"",
        "  # return (ok, reason); reason is shown to the user",
        "  # use ValidationError or assertions to fail the case",
        "  return True, None",
        "",
        "def case_two():",
        "  \"\"\"",
        "  second test case",
        "  \"\"\"",
        "  # you can raise exceptions here to fail the case",
        "  # keep the message concise for better UX",
        "  return True, None",
        "",
        "# register all cases here; order matters for display",
        "# this list can be any length and is easy to extend",
        "CASES = [",
        "  Case(\"case_one\", case_one),",
        "  Case(\"case_two\", case_two),",
        "]",
        "",
        "def run():",
        "  # run all cases and build the final payload",
        "  # the engine expects JSON with { ok: bool, cases: [] }",
        "  results = [case.run() for case in CASES]",
        "  ok = all(item.get(\"ok\") is True for item in results)",
        "  print(json.dumps({\"ok\": ok, \"cases\": results}))",
        "",
        "# entrypoint",
        "run()",
      ].join("\n"),
    []
  );

  useEffect(() => {
    const state = location.state as LocationState | null;
    if (state?.toast) {
      showToast({ message: state.toast.message, variant: state.toast.variant });
      navigate(
        location.pathname,
        {
          replace: true,
          state: null
        }
      );
    }
  }, [location.pathname, location.state, navigate, showToast]);

  useEffect(() => {
    if (error) {
      showToast({ message: error, variant: "error" });
    }
  }, [error, showToast]);

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      if (lessonId) {
        await updateLesson(lessonId, values);
        showToast({ message: "Lesson saved", variant: "success" });
      } else {
        const created = await createLesson(values);
        navigate(
          `/admiin/lessons/${created.id}`,
          {
            replace: true,
            state: { toast: { message: "Lesson created", variant: "success" } }
          }
        );
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to save lesson";
      showToast({ message: message, variant: "error" });
    } finally {
      setSaving(false);
    }
  }, [lessonId, navigate, showToast, values]);

  const handleDelete = useCallback(async () => {
    if (!lessonId) {
      return;
    }
    const shouldDelete = window.confirm("Delete this lesson?");
    if (!shouldDelete) {
      return;
    }
    try {
      await deleteLesson(lessonId);
      navigate(
        "/admiin/lessons",
        {
          replace: true,
          state: { toast: { message: "Lesson deleted", variant: "success" } }
        }
      );
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to delete lesson";
      showToast({ message: message, variant: "error" });
    }
  }, [lessonId, navigate, showToast]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    handleSave();
  };

  return (
    <div className="admin-page">
      {toasts.length > 0 && (
        <div className="toast-stack">
          {toasts.map((toast) => (
            <Notice key={toast.id} message={toast.message} variant={toast.variant} />
          ))}
        </div>
      )}
      <div className="panel__header">
        <div>
          <p className="eyebrow">editor</p>
          <h1>{lessonId ? "Edit lesson" : "Create lesson"}</h1>
        </div>
        <div className="actions">
          <div className="actions__group">
            <Button variant="ghost" type="button" onClick={() => reset()}>
              reset
            </Button>
            <Button variant="ghost" type="button" onClick={handleDelete} disabled={!lessonId}>
              delete
            </Button>
            <Button variant="accent" type="submit" form="lesson-form" disabled={saving}>
              {saving ? "saving..." : "save lesson"}
            </Button>
          </div>
        </div>
      </div>

      {isLoading && <div className="status muted">Loading lesson...</div>}

      <div className="admin-tabs">
        <button
          type="button"
          className={activeSection === "content" ? "admin-tab is-active" : "admin-tab"}
          onClick={() => setActiveSection("content")}
        >
          lesson content
        </button>
        <button
          type="button"
          className={activeSection === "execution" ? "admin-tab is-active" : "admin-tab"}
          onClick={() => setActiveSection("execution")}
        >
          code execution
        </button>
      </div>

      <form id="lesson-form" className="lesson-form" onSubmit={handleSubmit}>
        {activeSection === "content" ? (
          <>
            <div className="field-grid">
              <label className="field">
                <span className="field__label">Order</span>
                <Input
                  type="number"
                  min={1}
                  value={values.order}
                  onChange={(event) => updateField("order", Number(event.target.value))}
                />
              </label>
              <label className="field">
                <span className="field__label">Slug</span>
                <Input
                  value={values.slug}
                  onChange={(event) => updateField("slug", event.target.value)}
                />
              </label>
              <label className="field field--wide">
                <span className="field__label">Title</span>
                <Input
                  value={values.title}
                  onChange={(event) => updateField("title", event.target.value)}
                />
              </label>
            </div>

            <MarkdownEditor
              value={values.bodyMarkdown}
              onChange={(next) => updateField("bodyMarkdown", next)}
              toolbarHidden={toolbarHidden}
              onToggleToolbar={() => setToolbarHidden((prev) => !prev)}
              hotkeys={hotkeys}
            />
          </>
        ) : (
          <>
            <div className="inline-help">
              <p>Eval script quick guide</p>
              <ul>
                <li>
                  Paste user code with <code>{"{{USER_CODE}}"}</code> placeholder.
                </li>
                <li>Each case must return (ok: bool, reason: str | None).</li>
                <li>Case names must match Sample Cases below.</li>
                <li>Print JSON: {"{ ok, cases }"} exactly once.</li>
              </ul>
            </div>
            <div className="field">
              <div className="field__header">
                <span className="field__label">Eval script</span>
                <Button
                  type="button"
                  variant="ghost"
                  className="btn--tiny"
                  onClick={() => {
                    updateField("evalScript", evalScriptTemplate);
                    updateField(
                      "sampleCases",
                      [
                        { name: "case_one", label: "Case one" },
                        { name: "case_two", label: "Case two" },
                      ]
                    );
                  }}
                >
                  insert template (2 cases)
                </Button>
              </div>
              <div className="code-field code-field--eval">
                <CodeEditor
                  value={values.evalScript}
                  onChange={(next) => updateField("evalScript", next)}
                  className="code-editor code-field__surface"
                />
              </div>
            </div>
            <div className="field">
              <span className="field__label">Code editor default</span>
              <div className="code-field">
                <CodeEditor
                  value={values.codeEditorDefault}
                  onChange={(next) => updateField("codeEditorDefault", next)}
                  className="code-editor code-field__surface"
                />
              </div>
            </div>

            <SampleCasesEditor
              cases={values.sampleCases}
              onChange={(next) => updateField("sampleCases", next)}
            />
          </>
        )}
      </form>
    </div>
  );
};
