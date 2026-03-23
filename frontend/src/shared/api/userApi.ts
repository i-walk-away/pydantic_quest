import { apiRequest } from "@shared/api/apiClient";

export interface UserProfileResponse {
  id: string;
  username: string;
  email: string | null;
  role: string;
}

export interface UserProfileUpdatePayload {
  username?: string;
  email?: string;
  current_password?: string;
  new_password?: string;
}

export const fetchCurrentUser = async (): Promise<UserProfileResponse> => {
  return apiRequest<UserProfileResponse>({
    path: "/api/v1/users/me",
    method: "GET",
  });
};

export const updateCurrentUser = async (
  payload: UserProfileUpdatePayload,
): Promise<UserProfileResponse> => {
  return apiRequest<UserProfileResponse>({
    path: "/api/v1/users/me",
    method: "PUT",
    body: payload,
  });
};

export const fetchUserProgress = async (): Promise<string[]> => {
  return apiRequest<string[]>({
    path: "/api/v1/users/me/progress",
    method: "GET",
  });
};

export const markLessonCompleted = async (lessonId: string): Promise<{ ok: boolean }> => {
  return apiRequest<{ ok: boolean }>({
    path: `/api/v1/users/me/progress/${lessonId}`,
    method: "POST",
  });
};

export const resetUserProgress = async (): Promise<{ deleted: number }> => {
  return apiRequest<{ deleted: number }>({
    path: "/api/v1/users/me/progress/reset",
    method: "POST",
  });
};
