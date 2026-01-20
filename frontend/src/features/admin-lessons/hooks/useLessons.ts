import { useCallback, useEffect, useMemo, useState } from "react";

import { fetchLessons } from "@shared/api/lessonApi";
import { useLatestRequest } from "@shared/lib/useLatestRequest";
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
  const { run } = useLatestRequest();

  const load = useCallback(() => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    run((signal) => fetchLessons(signal))
      .then((data) => {
        if (!data) {
          return;
        }
        setState({ data: data, isLoading: false, error: null });
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : "Failed to load lessons";
        setState((prev) => ({ ...prev, isLoading: false, error: message }));
      });
  }, [run]);

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
