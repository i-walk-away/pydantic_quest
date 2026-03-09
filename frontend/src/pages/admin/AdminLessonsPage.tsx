import { useCallback, useEffect, type ReactElement } from "react";

import { useLessons } from "@features/admin-lessons/hooks/useLessons";
import { LessonTable } from "@features/admin-lessons/ui/LessonTable";
import { syncLessonsFromFiles } from "@shared/api/lessonApi";
import { useToast } from "@shared/lib/useToast";
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

  const handleSync = useCallback(async () => {
    try {
      const result = await syncLessonsFromFiles();
      showToast(
        {
          message: `Synced lessons: +${result.created} ~${result.updated} -${result.deleted}.`,
          variant: "success",
        },
      );
      reload();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to sync lessons";
      showToast({ message: message, variant: "error" });
    }
  }, [reload, showToast]);

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
          <Button variant="ghost" type="button" onClick={handleSync}>sync from files</Button>
        </div>
      </div>

      {isLoading && <div className="status muted">Loading lessons...</div>}

      {!isLoading && !error && <LessonTable lessons={data} />}

      <div className="panel__footer">
        <div className="status muted">{data.length} lessons</div>
      </div>
    </div>
  );
};
