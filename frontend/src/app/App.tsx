import { Suspense, lazy, type ReactElement } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthTokenHandler } from "@app/AuthTokenHandler";
import { ErrorBoundary } from "@shared/ui/ErrorBoundary";

const QuestPage = lazy(async () => {
  const module = await import("@pages/quest/QuestPage");
  return { default: module.QuestPage };
});
const AdminLayout = lazy(async () => {
  const module = await import("@pages/admin/AdminLayout");
  return { default: module.AdminLayout };
});
const AdminLessonsPage = lazy(async () => {
  const module = await import("@pages/admin/AdminLessonsPage");
  return { default: module.AdminLessonsPage };
});
const AdminLessonEditorPage = lazy(async () => {
  const module = await import("@pages/admin/AdminLessonEditorPage");
  return { default: module.AdminLessonEditorPage };
});
const AdminSettingsPage = lazy(async () => {
  const module = await import("@pages/admin/AdminSettingsPage");
  return { default: module.AdminSettingsPage };
});

export const App = (): ReactElement => {
  return (
    <ErrorBoundary>
      <Suspense fallback={null}>
        <BrowserRouter>
          <AuthTokenHandler />
          <Routes>
            <Route path="/" element={<QuestPage />} />
            <Route path="/admiin" element={<AdminLayout />}>
              <Route path="lessons" element={<AdminLessonsPage />} />
              <Route path="lessons/new" element={<AdminLessonEditorPage />} />
              <Route path="lessons/:lessonId" element={<AdminLessonEditorPage />} />
              <Route path="settings" element={<AdminSettingsPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace={true} />} />
          </Routes>
        </BrowserRouter>
      </Suspense>
    </ErrorBoundary>
  );
};
