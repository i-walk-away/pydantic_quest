import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AdminLayout } from "@pages/admin/AdminLayout";
import { AdminLessonsPage } from "@pages/admin/AdminLessonsPage";
import { AdminLessonEditorPage } from "@pages/admin/AdminLessonEditorPage";
import { AdminSettingsPage } from "@pages/admin/AdminSettingsPage";

export const App = (): JSX.Element => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/admin/lessons" replace={true} />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="lessons" element={<AdminLessonsPage />} />
          <Route path="lessons/new" element={<AdminLessonEditorPage />} />
          <Route path="lessons/:lessonId" element={<AdminLessonEditorPage />} />
          <Route path="settings" element={<AdminSettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/admin/lessons" replace={true} />} />
      </Routes>
    </BrowserRouter>
  );
};
