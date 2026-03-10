import { apiRequest } from "@shared/api/apiClient";
import { mapLesson, mapLessonPayload, type Lesson, type LessonApiResponse, type LessonFormValues } from "@shared/model/lesson";

const lessonOrderKey = (order: string): number[] => {
  return order.split(".").map((part) => Number(part));
};

export const fetchLessons = async (signal?: AbortSignal): Promise<Lesson[]> => {
  const data = await apiRequest<LessonApiResponse[]>({
    path: "/api/v1/lessons/get_all",
    method: "GET",
    signal: signal,
  });
  return data.map(mapLesson).sort((a, b) => {
    const left = lessonOrderKey(a.order);
    const right = lessonOrderKey(b.order);
    const maxLength = Math.max(left.length, right.length);

    for (let index = 0; index < maxLength; index += 1) {
      const leftPart = left[index] ?? -1;
      const rightPart = right[index] ?? -1;

      if (leftPart !== rightPart) {
        return leftPart - rightPart;
      }
    }

    return 0;
  });
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

export const syncLessonsFromFiles = async (): Promise<{ created: number; updated: number; deleted: number; total: number }> => {
  return apiRequest<{ created: number; updated: number; deleted: number; total: number }>({
    path: "/api/v1/lessons/sync_from_files",
    method: "POST",
  });
};
