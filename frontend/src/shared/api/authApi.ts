import { apiRequest } from "./apiClient";

export interface LoginRequest {
  username: string;
  plain_password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface SignupRequest {
  username: string;
  plain_password: string;
}

export interface UserResponse {
  id: string;
  username: string;
  role: "admin" | "user";
  email?: string | null;
}

export const loginUser = async (payload: LoginRequest): Promise<LoginResponse> => {
  return apiRequest<LoginResponse>({
    path: "/api/v1/auth/login",
    method: "POST",
    body: payload,
  });
};

export const signupUser = async (payload: SignupRequest): Promise<UserResponse> => {
  return apiRequest<UserResponse>({
    path: "/api/v1/users/create",
    method: "POST",
    body: payload,
  });
};

export const buildGithubLoginUrl = (): string => {
  const base = import.meta.env.VITE_API_BASE_URL || "";
  return `${base}/api/v1/auth/github`;
};
