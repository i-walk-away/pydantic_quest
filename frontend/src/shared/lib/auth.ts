const tokenKey = "pq:token";
const tokenSubjectKey = "sub";

export const getAuthToken = (): string | null => {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(tokenKey);
};

export const setAuthToken = (token: string): void => {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(tokenKey, token);
};

export const clearAuthToken = (): void => {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(tokenKey);
};

export const getAuthUsername = (): string | null => {
  const token = getAuthToken();
  if (!token) {
    return null;
  }

  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload[tokenSubjectKey] !== "string") {
    return null;
  }

  return payload[tokenSubjectKey];
};

const decodeJwtPayload = (token: string): Record<string, unknown> | null => {
  const parts = token.split(".");
  if (parts.length < 2) {
    return null;
  }

  const payloadPart = parts[1];
  try {
    const json = atob(normalizeBase64(payloadPart));
    const parsed = JSON.parse(json);
    if (parsed && typeof parsed === "object") {
      return parsed as Record<string, unknown>;
    }
    return null;
  } catch {
    return null;
  }
};

const normalizeBase64 = (value: string): string => {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padding = normalized.length % 4;
  if (padding === 0) {
    return normalized;
  }
  return `${normalized}${"=".repeat(4 - padding)}`;
};
