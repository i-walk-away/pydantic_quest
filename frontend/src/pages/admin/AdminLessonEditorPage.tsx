import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { useLesson } from "@features/admin-lessons/hooks/useLesson";
import { useLessons } from "@features/admin-lessons/hooks/useLessons";
import { useLessonForm } from "@features/admin-lessons/hooks/useLessonForm";
import { MarkdownEditor } from "@features/admin-lessons/ui/MarkdownEditor";
import { createLesson, deleteLesson, updateLesson } from "@shared/api/lessonApi";
import { loadHotkeys } from "@shared/lib/hotkeys";
import { type ToastVariant, useToast } from "@shared/lib/useToast";
import { Button } from "@shared/ui/Button";
import { LazyCodeEditor } from "@shared/ui/LazyCodeEditor";
import { Input } from "@shared/ui/Input";
import { Notice } from "@shared/ui/Notice";

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
  const { data: lessons } = useLessons();
  const { values, updateField, reset } = useLessonForm(data);
  const [saving, setSaving] = useState(false);
  const [toolbarHidden, setToolbarHidden] = useState(false);
  const { toasts, showToast } = useToast({ durationMs: 1000 });

  const hotkeys = useMemo(() => loadHotkeys(), []);
  const slugError = useMemo(() => {
    const trimmed = values.slug.trim();
    if (!trimmed) {
      return null;
    }
    const conflict = lessons.find((lesson) => lesson.slug === trimmed && lesson.id !== lessonId);
    if (conflict) {
      return "Slug already exists.";
    }
    return null;
  }, [lessons, lessonId, values.slug]);

  const orderError = useMemo(() => {
    const order = values.order;
    if (!Number.isFinite(order) || order < 1) {
      return "Order must be at least 1.";
    }
    const otherOrders = lessons
      .filter((lesson) => lesson.id !== lessonId)
      .map((lesson) => lesson.order);
    const maxOrder = otherOrders.length ? Math.max(...otherOrders) : 0;
    if (order > maxOrder + 1) {
      return `Order must be between 1 and ${maxOrder + 1}.`;
    }
    if (otherOrders.includes(order)) {
      return "Order already in use.";
    }
    return null;
  }, [lessons, lessonId, values.order]);

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
    if (slugError || orderError) {
      showToast({ message: "Fix validation errors before saving.", variant: "error" });
      return;
    }
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
  }, [lessonId, navigate, orderError, showToast, slugError, values]);

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

      <div className="inline-help">
        <p>lesson execution cases</p>
        <ul>
          <li>Cases are now managed from the repository `lessons/` directory.</li>
          <li>Use the sync action on the lessons page after editing files.</li>
          <li>This editor only updates metadata, markdown and default code.</li>
        </ul>
      </div>

      <form id="lesson-form" className="lesson-form" onSubmit={handleSubmit}>
        <div className="field-grid">
          <label className="field">
            <span className="field__label">Order</span>
            <Input
              type="number"
              min={1}
              value={values.order}
              onChange={(event) => updateField("order", Number(event.target.value))}
            />
            {orderError ? <div className="field__error">{orderError}</div> : null}
          </label>
          <label className="field">
            <span className="field__label">Slug</span>
            <Input
              value={values.slug}
              onChange={(event) => updateField("slug", event.target.value)}
            />
            {slugError ? <div className="field__error">{slugError}</div> : null}
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

        <div className="field">
          <span className="field__label">Code editor default</span>
          <div className="code-field">
            <LazyCodeEditor
              value={values.codeEditorDefault}
              onChange={(next) => updateField("codeEditorDefault", next)}
              className="code-editor code-field__surface"
            />
          </div>
        </div>
      </form>
    </div>
  );
};
