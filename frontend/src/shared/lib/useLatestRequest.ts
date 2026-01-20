import { useCallback, useEffect, useRef } from "react";

export type RequestExecutor<TResult> = (signal: AbortSignal) => Promise<TResult>;

interface UseLatestRequestResult {
  run: <TResult>(executor: RequestExecutor<TResult>) => Promise<TResult | null>;
  abort: () => void;
}

export const useLatestRequest = (): UseLatestRequestResult => {
  const requestIdRef = useRef(0);
  const controllerRef = useRef<AbortController | null>(null);

  const abort = useCallback(() => {
    controllerRef.current?.abort();
  }, []);

  const run = useCallback(async <TResult,>(executor: RequestExecutor<TResult>) => {
    abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;

    try {
      const result = await executor(controller.signal);
      if (requestIdRef.current !== requestId) {
        return null;
      }
      return result;
    } catch (error: unknown) {
      if (controller.signal.aborted) {
        return null;
      }
      if (error instanceof DOMException && error.name === "AbortError") {
        return null;
      }
      if (requestIdRef.current !== requestId) {
        return null;
      }
      throw error;
    }
  }, [abort]);

  useEffect(() => {
    return () => {
      abort();
    };
  }, [abort]);

  return { run, abort };
};
