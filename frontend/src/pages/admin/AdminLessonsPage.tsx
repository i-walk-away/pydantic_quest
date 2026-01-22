import { useCallback, useEffect, type ReactElement } from "react";

import { useLessons } from "@features/admiin-lessons/hooks/useLessons";
import { LessonTable } from "@features/admiin-lessons/ui/LessonTable";
import { deleteLesson } from "@shared/api/lessonApi";
import { useToast } from "@shared/lib/useToast";
import { LinkButton } from "@shared/ui/LinkButton";
import { Button } from "@shared/ui/Button";
import { Notice } from "@shared/ui/Notice";

export const AdminLessonsPage = (): ReactElement => {
  const { data, isLoading, error, reload } = useLessons();
  const { toasts, showToast } = useToast({ durationMs: 1000 });

  useEffect(() => {
    if (error) {
      showToast({ message: error, variant: "error" });
    }
  }, [error, showToast]);

  const handleDelete = useCallback(
    async (lessonId: string) => {
      const shouldDelete = window.confirm("Delete this lesson?");
      if (!shouldDelete) {
        return;
      }
      try {
        await deleteLesson(lessonId);
        showToast({ message: "Lesson deleted", variant: "success" });
        reload();
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Failed to delete lesson";
        showToast({ message: message, variant: "error" });
      }
    },
    [reload, showToast]
  );

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
          <p className="eyebrow">library</p>
          <h1>Lessons</h1>
        </div>
        <div className="actions">
          <Button variant="ghost" type="button" onClick={reload}>refresh</Button>
          <LinkButton to="/admiin/lessons/new" variant="accent">new lesson</LinkButton>
        </div>
      </div>

      {isLoading && <div className="status muted">Loading lessons...</div>}

      {!isLoading && !error && (
        <LessonTable lessons={data} onDelete={handleDelete} />
      )}

      <div className="panel__footer">
        <div className="status muted">{data.length} lessons</div>
      </div>
    </div>
  );
};
