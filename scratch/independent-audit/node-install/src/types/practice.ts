export type ExerciseType = "multiple_choice" | "short_answer" | "python_code" | "python_debug";

export interface PythonTest {
  name: string;
  args?: unknown[];
  kwargs?: Record<string, unknown>;
  expected?: unknown;
  expected_typed?: TypedValue;
  expected_exception?: string | null;
  stdin?: string;
  expected_stdout?: string;
  secret?: boolean;
}

export interface TypedValue {
  type: string;
  display: string;
  value: unknown;
}

export interface ExecutionTestResult {
  test_index: number;
  name: string;
  passed: boolean;
  input_display: string;
  expected_value: TypedValue | null;
  expected_type: string;
  actual_value: TypedValue | null;
  actual_type: string;
  stdout: string;
  stderr: string;
  exception_type: string | null;
  exception_message: string | null;
  line_number: number | null;
  duration_ms: number;
  message: string;
}

export interface Exercise {
  id: number;
  topic_id: number;
  exercise_type: ExerciseType;
  title: string;
  prompt_markdown: string;
  difficulty: string;
  hints_available: number;
  validation_status: "valid" | "pending" | "invalid";
  content: {
    choices?: string[];
    starter_code?: string;
    function_name?: string;
    sample_tests?: PythonTest[];
    time_limit_ms?: number;
  };
}

export interface PracticePack {
  session_id: number;
  exercises: Exercise[];
}

export interface ExecutionResult {
  status: "passed" | "failed" | "runtime_error" | "timeout";
  stdout: string;
  stderr: string;
  tests: ExecutionTestResult[];
  duration_ms: number;
}

export interface Attempt {
  attempt_id: number;
  session_id: number;
  exercise_id: number;
  exercise_title: string;
  exercise_type: string;
  score: number | null;
  passed: boolean | null;
  hints_used_count: number;
  grading_source: string;
  evaluation_status: string;
  feedback: string;
  created_at: string;
}

export interface PracticeHistory {
  attempts: Attempt[];
  attempt_count: number;
  recent_average: number | null;
  last_practiced_at: string | null;
}
