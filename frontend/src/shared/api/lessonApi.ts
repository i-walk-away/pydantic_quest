import { apiRequest } from "@shared/api/apiClient";
import { mapLesson, mapLessonPayload, type Lesson, type LessonApiResponse, type LessonFormValues } from "@shared/model/lesson";

export const fetchLessons = async (signal?: AbortSignal): Promise<Lesson[]> => {
  const data = await apiRequest<LessonApiResponse[]>({
    path: "/api/v1/lessons/get_all",
    method: "GET",
    signal: signal,
  });
  return data.map(mapLesson).sort((a, b) => a.order - b.order);
};

export const fetchLesson = async (lessonId: string, signal?: AbortSignal): Promise<Lesson> => {
  const data = await apiRequest<LessonApiResponse>({
    path: `/api/v1/lessons/${lessonId}`,
    method: "GET",
    signal: signal,
  });
  return mapLesson(data);
};

export const createLesson = async (values: LessonFormValues): Promise<Lesson> => {
  const data = await apiRequest<LessonApiResponse>({
    path: "/api/v1/lessons/create",
    method: "POST",
    body: mapLessonPayload(values),
  });
  return mapLesson(data);
};

export const updateLesson = async (lessonId: string, values: LessonFormValues): Promise<Lesson> => {
  const data = await apiRequest<LessonApiResponse>({
    path: `/api/v1/lessons/${lessonId}`,
    method: "PUT",
    body: mapLessonPayload(values),
  });
  return mapLesson(data);
};

export const deleteLesson = async (lessonId: string): Promise<boolean> => {
  return apiRequest<boolean>({
    path: `/api/v1/lessons/${lessonId}`,
    method: "DELETE",
  });
};
