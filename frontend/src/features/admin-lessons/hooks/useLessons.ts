import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchLessons } from "@shared/api/lessonApi";
import { type Lesson } from "@shared/model/lesson";

interface LessonsState {
  data: Lesson[];
  isLoading: boolean;
  error: string | null;
}

interface UseLessonsResult extends LessonsState {
  reload: () => void;
}

export const useLessons = (): UseLessonsResult => {
  const [state, setState] = useState<LessonsState>({
    data: [],
    isLoading: true,
    error: null,
  });
  const requestIdRef = useRef(0);

  const load = useCallback(() => {
    const controller = new AbortController();
    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    fetchLessons(controller.signal)
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
        const message = error instanceof Error ? error.message : "Failed to load lessons";
        setState((prev) => ({ ...prev, isLoading: false, error: message }));
      });

    return () => controller.abort();
  }, []);

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
