import { apiRequest } from "@shared/api/apiClient";
import { type ExecutionResult } from "@shared/model/execution";

interface ExecutionRequest {
  lesson_id: string;
  code: string;
}

export const runLessonCode = async (lessonId: string, code: string): Promise<ExecutionResult> => {
  return apiRequest<ExecutionResult>({
    path: "/api/v1/execute/run",
    method: "POST",
    body: {
      lesson_id: lessonId,
      code: code,
    } satisfies ExecutionRequest,
  });
};
