import type { AIStatus, Curriculum, CurriculumProposal, CurriculumSummary, Dashboard, Topic, TutorTurn } from "../types/api";
import type { Attempt, Exercise, PracticeHistory, PracticePack, PythonTest, ExecutionResult } from "../types/practice";
import type { AdaptiveAttempt, AdaptiveSubmission, MasteryBreakdown, PlannerSettings, ReviewQueueItem, ReviewSessionItem, TodayPlan, TransferSession } from "../types/adaptive";
import type { InterviewCodingSubmission, InterviewHistory, InterviewMode, InterviewReport, InterviewSession } from "../types/interview";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<Dashboard>("/api/dashboard"),
  curricula: () => request<CurriculumSummary[]>("/api/curricula"),
  activeCurriculum: () => request<Curriculum>("/api/curricula/active"),
  curriculum: (id: number) => request<Curriculum>(`/api/curricula/${id}`),
  proposal: (id: number) => request<CurriculumProposal>(`/api/curricula/${id}/proposal`),
  topic: (id: number) => request<Topic>(`/api/topics/${id}`),
  aiStatus: () => request<AIStatus>("/api/ai/status"),
  generateCurriculum: (body: { requirements: string; name?: string; goal?: string }) => request<CurriculumProposal>("/api/curricula/generate-preview", { method: "POST", body: JSON.stringify(body) }),
  createDraft: (proposal: CurriculumProposal, sourceRequirements: string) => request<Curriculum>("/api/curricula/drafts", { method: "POST", body: JSON.stringify({ proposal, source_requirements: sourceRequirements }) }),
  updateDraft: (id: number, proposal: CurriculumProposal, sourceRequirements = "") => request<Curriculum>(`/api/curricula/${id}/draft`, { method: "PUT", body: JSON.stringify({ proposal, source_requirements: sourceRequirements }) }),
  confirmCurriculum: (id: number) => request<Curriculum>(`/api/curricula/${id}/confirm`, { method: "POST" }),
  activateCurriculum: (id: number) => request<Curriculum>(`/api/curricula/${id}/activate`, { method: "POST" }),
  startTutor: (topicId: number) => request<{ session_id: number; turn: TutorTurn }>(`/api/tutor/topics/${topicId}/start`, { method: "POST" }),
  tutorMessage: (sessionId: number, message: string) => request<TutorTurn>(`/api/tutor/sessions/${sessionId}/message`, { method: "POST", body: JSON.stringify({ message }) }),
  doubtMessage: (body: { session_id: number | null; topic_id: number | null; message: string }) => request<{ session_id: number; reply: string }>("/api/doubt/message", { method: "POST", body: JSON.stringify(body) }),
  startPractice: (topicId: number) => request<PracticePack>(`/api/practice/topics/${topicId}/start`, { method: "POST" }),
  practiceSession: (id: number) => request<PracticePack>(`/api/practice/sessions/${id}`),
  practiceHistory: (topicId: number) => request<PracticeHistory>(`/api/practice/topics/${topicId}/history`),
  exercise: (id: number) => request<Exercise>(`/api/practice/exercises/${id}`),
  revealHint: (id: number, sessionId: number) => request<{ index: number; text: string; hints_used_count: number }>(`/api/practice/exercises/${id}/hint`, { method: "POST", body: JSON.stringify({ session_id: sessionId }) }),
  submissionTests: (id: number) => request<{ function_name: string; tests: PythonTest[]; time_limit_ms: number }>(`/api/practice/exercises/${id}/submission-tests`),
  referenceValidation: (id: number) => request<{ reference_solution: string; function_name: string; tests: PythonTest[]; time_limit_ms: number }>(`/api/practice/exercises/${id}/reference-validation`),
  reportReferenceValidation: (id: number, passed: boolean) => request<{ validation_status: string }>(`/api/practice/exercises/${id}/reference-validation`, { method: "POST", body: JSON.stringify({ passed }) }),
  submitMcq: (id: number, sessionId: number, selectedIndex: number) => request<Attempt>(`/api/practice/exercises/${id}/submit/mcq`, { method: "POST", body: JSON.stringify({ session_id: sessionId, selected_index: selectedIndex }) }),
  submitShortAnswer: (id: number, sessionId: number, answer: string) => request<Attempt>(`/api/practice/exercises/${id}/submit/short-answer`, { method: "POST", body: JSON.stringify({ session_id: sessionId, answer }) }),
  submitCode: (id: number, sessionId: number, source: string, execution: ExecutionResult) => request<Attempt>(`/api/practice/exercises/${id}/submit/code`, { method: "POST", body: JSON.stringify({ session_id: sessionId, source, execution }) }),
  mastery: (topicId: number) => request<MasteryBreakdown>(`/api/topics/${topicId}/mastery`),
  startTransfer: (topicId: number) => request<TransferSession>(`/api/mastery/topics/${topicId}/transfer/start`, { method: "POST" }),
  transferSession: (sessionId: number) => request<TransferSession>(`/api/mastery/transfer/${sessionId}`),
  submitTransfer: (sessionId: number, submission: AdaptiveSubmission) => request<AdaptiveAttempt>(`/api/mastery/transfer/${sessionId}/submit`, { method: "POST", body: JSON.stringify(submission) }),
  reviewsDue: () => request<ReviewQueueItem[]>("/api/reviews/due"),
  reviewsUpcoming: () => request<{ tomorrow: number; next_7_days: number; items: ReviewQueueItem[]; recently_reviewed: { topic_id: number; topic_name: string; score: number; at: string }[] }>("/api/reviews/upcoming"),
  startReviews: () => request<{ items: ReviewSessionItem[] }>("/api/reviews/session/start", { method: "POST" }),
  submitReview: (sessionId: number, submission: AdaptiveSubmission) => request<AdaptiveAttempt>(`/api/reviews/session/${sessionId}/submit`, { method: "POST", body: JSON.stringify(submission) }),
  todayPlan: () => request<TodayPlan>("/api/planner/today"),
  skipPlanItem: (id: number) => request<{ status: string }>(`/api/planner/items/${id}/skip`, { method: "POST" }),
  completePlanItem: (id: number) => request<{ status: string }>(`/api/planner/items/${id}/complete`, { method: "POST" }),
  plannerSettings: () => request<PlannerSettings>("/api/planner/settings"),
  updatePlannerSettings: (values: Partial<PlannerSettings>) => request<PlannerSettings>("/api/planner/settings", { method: "PUT", body: JSON.stringify(values) }),
  aiSettings: () => request<{ monthly_gemini_budget: number; pause_nonessential_ai: boolean }>("/api/ai/settings"),
  updateAiSettings: (values: { monthly_gemini_budget: number; pause_nonessential_ai: boolean }) => request<{ monthly_gemini_budget: number; pause_nonessential_ai: boolean }>("/api/ai/settings", { method: "PUT", body: JSON.stringify(values) }),
  interviewModes: () => request<InterviewMode[]>("/api/interviews/modes"),
  interviewHistory: () => request<InterviewHistory[]>("/api/interviews/history"),
  startInterview: (mode: string) => request<InterviewSession>("/api/interviews/start", { method: "POST", body: JSON.stringify({ mode }) }),
  interview: (id: number) => request<InterviewSession>(`/api/interviews/${id}`),
  answerInterview: (id: number, answer: string, durationSeconds?: number) => request<InterviewSession>(`/api/interviews/${id}/answer`, { method: "POST", body: JSON.stringify({ answer, duration_seconds: durationSeconds }) }),
  submitInterviewCode: (id: number, submission: InterviewCodingSubmission) => request<InterviewSession>(`/api/interviews/${id}/coding-submit`, { method: "POST", body: JSON.stringify(submission) }),
  completeInterview: (id: number) => request<InterviewReport>(`/api/interviews/${id}/complete`, { method: "POST" }),
  prepareNextInterviewQuestion: (id: number) => request<InterviewSession>(`/api/interviews/${id}/next`, { method: "POST" }),
  interviewReport: (id: number) => request<InterviewReport>(`/api/interviews/${id}/report`),
  saveInterview: (id: number) => request<{ status: string }>(`/api/interviews/${id}/save`, { method: "POST" }),
  resumeInterview: (id: number) => request<InterviewSession>(`/api/interviews/${id}/resume`, { method: "POST" }),
  abandonInterview: (id: number) => request<{ status: string }>(`/api/interviews/${id}/abandon`, { method: "POST" }),
};
