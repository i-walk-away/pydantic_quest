import { apiRequest } from "@shared/api/apiClient";
import {
  type CodeAnalysisResult,
  type ExecutionResult,
} from "@shared/model/execution";

interface ExecutionRequest {
  lesson_id: string;
  code: string;
}

interface CodeAnalysisRequest {
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

export const analyzeLessonCode = async (
  code: string,
  signal?: AbortSignal
): Promise<CodeAnalysisResult> => {
  return apiRequest<CodeAnalysisResult>({
    path: "/api/v1/execute/analyze",
    method: "POST",
    signal: signal,
    body: {
      code: code,
    } satisfies CodeAnalysisRequest,
  });
};
