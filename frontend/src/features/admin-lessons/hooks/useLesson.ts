import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchLesson } from "@shared/api/lessonApi";
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
  const requestIdRef = useRef(0);

  const load = useCallback(() => {
    if (!lessonId) {
      setState({ data: null, isLoading: false, error: null });
      return () => undefined;
    }

    const controller = new AbortController();
    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    fetchLesson(lessonId, controller.signal)
      .then((data) => {
        if (requestIdRef.current !== requestId) {
          return;
        }
        setState({ data: data, isLoading: false, error: null });
      })
      .catch((error: unknown) => {
        if (requestIdRef.current !== requestId) {
          return;
        }
        const message = error instanceof Error ? error.message : "Failed to load lesson";
        setState((prev) => ({ ...prev, isLoading: false, error: message }));
      });

    return () => controller.abort();
  }, [lessonId]);

  useEffect(() => {
    const abort = load();
    return () => {
      abort?.();
    };
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
