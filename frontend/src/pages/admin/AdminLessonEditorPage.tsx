import { useCallback, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useLesson } from "@features/admin-lessons/hooks/useLesson";
import { useLessonForm } from "@features/admin-lessons/hooks/useLessonForm";
import { MarkdownEditor } from "@features/admin-lessons/ui/MarkdownEditor";
import { createLesson, deleteLesson, updateLesson } from "@shared/api/lessonApi";
import { loadHotkeys } from "@shared/lib/hotkeys";
import { Button } from "@shared/ui/Button";
import { Input } from "@shared/ui/Input";
import { Textarea } from "@shared/ui/Textarea";

export const AdminLessonEditorPage = (): JSX.Element => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const { data, isLoading, error } = useLesson(lessonId ?? null);
  const { values, updateField, reset } = useLessonForm(data);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [toolbarHidden, setToolbarHidden] = useState(false);

  const hotkeys = useMemo(() => loadHotkeys(), []);

  const handleSave = useCallback(async () => {
    setSaving(true);
    setActionError(null);
    try {
      if (lessonId) {
        await updateLesson(lessonId, values);
      } else {
        const created = await createLesson(values);
        navigate(`/admin/lessons/${created.id}`, { replace: true });
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to save lesson";
      setActionError(message);
    } finally {
      setSaving(false);
    }
  }, [lessonId, navigate, values]);

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
      navigate("/admin/lessons", { replace: true });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to delete lesson";
      setActionError(message);
    }
  }, [lessonId, navigate]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    handleSave();
  };

  return (
    <div className="admin-page">
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
      {error && <div className="status error">{error}</div>}
      {actionError && <div className="status error">{actionError}</div>}

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
