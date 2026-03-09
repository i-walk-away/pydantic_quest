import type { ReactElement } from "react";

import { type Lesson } from "@shared/model/lesson";

interface LessonTableProps {
  lessons: Lesson[];
}

export const LessonTable = ({ lessons }: LessonTableProps): ReactElement => {
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
          </tr>
        </thead>
        <tbody>
          {lessons.map((lesson) => (
            <tr key={lesson.id}>
              <td>{lesson.order}</td>
              <td>{lesson.slug}</td>
              <td>{lesson.title}</td>
              <td>{lesson.updatedAt ? lesson.updatedAt.toLocaleString() : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
