import { useCallback, useRef, useState } from "react";

export type ToastVariant = "success" | "error" | "info";

export interface ToastPayload {
  message: string;
  variant?: ToastVariant;
}

interface UseToastOptions {
  durationMs?: number;
  maxVisible?: number;
}

interface ToastState {
  id: number;
  message: string;
  variant: ToastVariant;
}

interface UseToastResult {
  toasts: ToastState[];
  showToast: (payload: ToastPayload) => void;
  removeToast: (toastId: number) => void;
}

export const useToast = ({ durationMs = 1500, maxVisible = 3 }: UseToastOptions): UseToastResult => {
  const [toasts, setToasts] = useState<ToastState[]>([]);
  const idSeed = useRef(0);

  const removeToast = useCallback((toastId: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== toastId));
  }, []);

  const showToast = useCallback(
    (payload: ToastPayload) => {
      const variant = payload.variant ?? "success";
      idSeed.current += 1;
      const toastId = idSeed.current;
      setToasts((prev) => {
        if (prev.some((toast) => toast.message === payload.message && toast.variant === variant)) {
          return prev;
        }
        const next = [
          ...prev,
          {
            id: toastId,
            message: payload.message,
            variant: variant,
          },
        ];
        if (next.length > maxVisible) {
          return next.slice(-maxVisible);
        }
        return next;
      });
      window.setTimeout(() => {
        removeToast(toastId);
      }, durationMs);
    },
    [durationMs, maxVisible, removeToast]
  );

  return { toasts, showToast, removeToast };
};
