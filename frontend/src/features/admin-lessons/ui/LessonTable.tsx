import { Link } from "react-router-dom";

import { Button } from "@shared/ui/Button";
import { type Lesson } from "@shared/model/lesson";

interface LessonTableProps {
  lessons: Lesson[];
  onDelete: (lessonId: string) => void;
}

export const LessonTable = ({ lessons, onDelete }: LessonTableProps): JSX.Element => {
  if (lessons.length === 0) {
    return <div className="empty">No lessons yet.</div>;
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Order</th>
            <th>Slug</th>
            <th>Title</th>
            <th>Updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {lessons.map((lesson) => (
            <tr key={lesson.id}>
              <td>{lesson.order}</td>
              <td>{lesson.slug}</td>
              <td>{lesson.title}</td>
              <td>{lesson.updatedAt ? lesson.updatedAt.toLocaleString() : "-"}</td>
              <td>
                <div className="actions">
                  <Link className="btn btn--ghost" to={`/admin/lessons/${lesson.id}`}>
                    edit
                  </Link>
                  <Button variant="ghost" type="button" onClick={() => onDelete(lesson.id)}>
                    delete
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
