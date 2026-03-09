const tokenKey = "pq:token";
const tokenSubjectKey = "sub";
const tokenRoleKey = "role";

export const getAuthToken = (): string | null => {
  if (typeof window === "undefined") {
    return null;
  }

  const token = window.localStorage.getItem(tokenKey);
  if (!token) {
    return null;
  }

  const payload = decodeJwtPayload(token);
  if (isTokenExpired(payload)) {
    window.localStorage.removeItem(tokenKey);
    return null;
  }

  return token;
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

export const getAuthRole = (): string | null => {
  const token = getAuthToken();
  if (!token) {
    return null;
  }

  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload[tokenRoleKey] !== "string") {
    return null;
  }

  return payload[tokenRoleKey];
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

const isTokenExpired = (payload: Record<string, unknown> | null): boolean => {
  if (!payload) {
    return true;
  }
  const exp = payload["exp"];
  if (typeof exp !== "number") {
    return false;
  }
  return exp <= Math.floor(Date.now() / 1000);
};

const normalizeBase64 = (value: string): string => {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padding = normalized.length % 4;
  if (padding === 0) {
    return normalized;
  }
  return `${normalized}${"=".repeat(4 - padding)}`;
};
