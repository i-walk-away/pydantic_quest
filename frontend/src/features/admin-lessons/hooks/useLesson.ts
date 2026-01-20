import { useCallback, useEffect, useMemo, useState } from "react";

import { fetchLesson } from "@shared/api/lessonApi";
import { useLatestRequest } from "@shared/lib/useLatestRequest";
import { type Lesson } from "@shared/model/lesson";

interface LessonState {
  data: Lesson | null;
  isLoading: boolean;
  error: string | null;
}

interface UseLessonResult extends LessonState {
  reload: () => void;
}

export const useLesson = (lessonId: string | null): UseLessonResult => {
  const [state, setState] = useState<LessonState>({
    data: null,
    isLoading: Boolean(lessonId),
    error: null,
  });
  const { run } = useLatestRequest();

  const load = useCallback(() => {
    if (!lessonId) {
      setState({ data: null, isLoading: false, error: null });
      return;
    }

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    run((signal) => fetchLesson(lessonId, signal))
      .then((data) => {
        if (!data) {
          return;
        }
        setState({ data: data, isLoading: false, error: null });
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : "Failed to load lesson";
        setState((prev) => ({ ...prev, isLoading: false, error: message }));
      });
  }, [lessonId, run]);

  useEffect(() => {
    load();
  }, [load]);

  const reload = useCallback(() => {
    load();
  }, [load]);

  return useMemo(
    () => ({
      data: state.data,
      isLoading: state.isLoading,
      error: state.error,
      reload: reload,
    }),
    [state, reload]
  );
};
