export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

export interface ApiRequestOptions {
  path: string;
  method: HttpMethod;
  body?: unknown;
  signal?: AbortSignal;
}

export interface ApiErrorPayload {
  message: string;
  status: number;
}

export class ApiError extends Error {
  status: number;

  constructor(payload: ApiErrorPayload) {
    super(payload.message);
    this.status = payload.status;
  }
}

const buildUrl = (path: string): string => {
  const trimmed = path.startsWith("/") ? path : `/${path}`;
  const base = import.meta.env.VITE_API_BASE_URL || "";
  return `${base}${trimmed}`;
};

import { getAuthToken } from "@shared/lib/auth";

export const apiRequest = async <T>({ path, method, body, signal }: ApiRequestOptions): Promise<T> => {
  const token = getAuthToken();
  const response = await fetch(buildUrl(path), {
    method: method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
    signal: signal,
  });

  if (!response.ok) {
    let message: string = response.statusText;
    try {
      const payload = (await response.json()) as {
        detail?: unknown;
        message?: unknown;
      };
      const detail = payload.detail ?? payload.message;
      if (typeof detail === "string") {
        message = detail;
      } else if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0] as { msg?: unknown };
        if (typeof first?.msg === "string") {
          message = first.msg;
        } else {
          message = JSON.stringify(detail);
        }
      } else if (detail) {
        try {
          message = JSON.stringify(detail);
        } catch {
          message = response.statusText;
        }
      }
    } catch {
      message = response.statusText;
    }
    throw new ApiError({ message: message, status: response.status });
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
};
