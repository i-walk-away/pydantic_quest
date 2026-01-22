import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { useLesson } from "@features/admiin-lessons/hooks/useLesson";
import { useLessonForm } from "@features/admiin-lessons/hooks/useLessonForm";
import { MarkdownEditor } from "@features/admiin-lessons/ui/MarkdownEditor";
import { createLesson, deleteLesson, updateLesson } from "@shared/api/lessonApi";
import { loadHotkeys } from "@shared/lib/hotkeys";
import { type ToastVariant, useToast } from "@shared/lib/useToast";
import { Button } from "@shared/ui/Button";
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
  const { toasts, showToast } = useToast({ durationMs: 1000 });

  const hotkeys = useMemo(() => loadHotkeys(), []);

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

      <form id="lesson-form" className="lesson-form" onSubmit={handleSubmit}>
        <div className="field-grid">
          <label className="field">
            <span>Order</span>
            <Input
              type="number"
              min={1}
              value={values.order}
              onChange={(event) => updateField("order", Number(event.target.value))}
            />
          </label>
          <label className="field">
            <span>Slug</span>
            <Input
              value={values.slug}
              onChange={(event) => updateField("slug", event.target.value)}
            />
          </label>
          <label className="field field--wide">
            <span>Title</span>
            <Input
              value={values.title}
              onChange={(event) => updateField("title", event.target.value)}
            />
          </label>
        </div>

        <label className="field">
          <span>Expected output</span>
          <Textarea
            rows={3}
            value={values.expectedOutput}
            onChange={(event) => updateField("expectedOutput", event.target.value)}
          />
        </label>
        <label className="field">
          <span>Code editor default</span>
          <Textarea
            rows={6}
            value={values.codeEditorDefault}
            onChange={(event) => updateField("codeEditorDefault", event.target.value)}
          />
        </label>

        <MarkdownEditor
          value={values.bodyMarkdown}
          onChange={(next) => updateField("bodyMarkdown", next)}
          toolbarHidden={toolbarHidden}
          onToggleToolbar={() => setToolbarHidden((prev) => !prev)}
          hotkeys={hotkeys}
        />
      </form>
    </div>
  );
};
