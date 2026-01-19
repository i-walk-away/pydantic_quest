import { useCallback, useState } from "react";

import { useLessons } from "@features/admin-lessons/hooks/useLessons";
import { LessonTable } from "@features/admin-lessons/ui/LessonTable";
import { deleteLesson } from "@shared/api/lessonApi";
import { LinkButton } from "@shared/ui/LinkButton";
import { Button } from "@shared/ui/Button";

export const AdminLessonsPage = (): JSX.Element => {
  const { data, isLoading, error, reload } = useLessons();
  const [actionError, setActionError] = useState<string | null>(null);

  const handleDelete = useCallback(
    async (lessonId: string) => {
      const shouldDelete = window.confirm("Delete this lesson?");
      if (!shouldDelete) {
        return;
      }
      try {
        await deleteLesson(lessonId);
        setActionError(null);
        reload();
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Failed to delete lesson";
        setActionError(message);
      }
    },
    [reload]
  );

  return (
    <div className="admin-page">
      <div className="panel__header">
        <div>
          <p className="eyebrow">library</p>
          <h1>Lessons</h1>
        </div>
        <div className="actions">
          <Button variant="ghost" type="button" onClick={reload}>refresh</Button>
          <LinkButton to="/admin/lessons/new" variant="accent">new lesson</LinkButton>
        </div>
      </div>

      {isLoading && <div className="status muted">Loading lessons...</div>}
      {error && <div className="status error">{error}</div>}
      {actionError && <div className="status error">{actionError}</div>}

      {!isLoading && !error && (
        <LessonTable lessons={data} onDelete={handleDelete} />
      )}

      <div className="panel__footer">
        <div className="status muted">{data.length} lessons</div>
      </div>
    </div>
  );
};
