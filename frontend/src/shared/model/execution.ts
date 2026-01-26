export type ExecutionStatus =
  | "accepted"
  | "wrong_answer"
  | "compile_error"
  | "runtime_error"
  | "timeout";

export interface ExecutionCase {
  name: string;
  label: string;
  ok: boolean;
  reason?: string | null;
}

export interface ExecutionResult {
  status: ExecutionStatus;
  cases: ExecutionCase[];
  stderr?: string | null;
  stdout?: string | null;
  duration_ms?: number | null;
}
