import type { EditionIndex, EditionOverview, EditionConfirmation, TopicEditionMetadata } from "../types/editions";
import type { Curriculum, CurriculumProposal, CurriculumSummary, Dashboard, Topic } from "../types/api";
import type { Attempt, Exercise, PracticeHistory, PracticePack, PythonTest, ExecutionResult } from "../types/practice";
import type { AdaptiveAttempt, AdaptiveSubmission, MasteryBreakdown, PlannerSettings, ReviewQueueItem, ReviewSessionItem, TodayPlan, TransferSession } from "../types/adaptive";
import type { CourseTopic, LessonProgress } from "../types/course";
import type { ArenaProblem, ArenaSummary, ArenaValidation } from "../types/arena";
import type {
  ArenaStageDetail,
  BeginnerExerciseData,
  BeginnerExerciseResult,
  ConceptStepDetail,
  ConceptStepSummary,
  LearningPathDashboardData,
  LearningStage,
  SubjectProgressSummary,
} from "../types/learningPath";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
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
  editions: () => request<EditionIndex>("/api/editions"),
  edition: (key = "placement-foundations", curriculumId?: number) => request<EditionOverview>(`/api/editions/${key}${curriculumId ? `?curriculum_id=${curriculumId}` : ""}`),
  selectEdition: (key: string) => request<EditionIndex>(`/api/editions/${key}/select`, {method:"POST"}),
  createPlacementDraft: () => request<EditionOverview>("/api/editions/placement-foundations/draft", {method:"POST"}),
  editionReview: (id: number) => request<EditionOverview>(`/api/editions/curricula/${id}/review`),
  confirmEdition: (id: number, body: EditionConfirmation) => request<EditionOverview>(`/api/editions/curricula/${id}/confirm`, {method:"POST",body:JSON.stringify(body)}),
  activateEdition: (id: number) => request<EditionOverview>(`/api/editions/curricula/${id}/activate`, {method:"POST"}),
  topicEditionMetadata: (id: number) => request<TopicEditionMetadata>(`/api/editions/topics/${id}`),
  dashboard: () => request<Dashboard>("/api/dashboard"),
  arenaProblems: (params="") => request<ArenaProblem[]>(`/api/arena/problems${params}`),
  arenaProblem: (key:string) => request<ArenaProblem>(`/api/arena/problems/${key}`),
  arenaSummary: () => request<ArenaSummary>("/api/arena/summary"),
  arenaHint: (key:string) => request<{index:number;text:string}>(`/api/arena/problems/${key}/hint`,{method:"POST"}),
  submitArena: (key:string,body:{source:string;content_revision_id?:number}) => request<{attempt_id:number;passed:boolean;score:number;solution?:string;explanation?:string;complexity?:string}>(`/api/arena/problems/${key}/submit`,{method:"POST",body:JSON.stringify(body)}),
  giveUpArena: (key:string) => request<{solution:string;explanation:string;complexity:string}>(`/api/arena/problems/${key}/give-up`,{method:"POST"}),
  curricula: () => request<CurriculumSummary[]>("/api/curricula"),
  activeCurriculum: () => request<Curriculum>("/api/curricula/active"),
  curriculum: (id: number) => request<Curriculum>(`/api/curricula/${id}`),
  proposal: (id: number) => request<CurriculumProposal>(`/api/curricula/${id}/proposal`),
  topic: (id: number) => request<Topic>(`/api/topics/${id}`),
  createDraft: (proposal: CurriculumProposal, sourceRequirements: string) => request<Curriculum>("/api/curricula/drafts", { method: "POST", body: JSON.stringify({ proposal, source_requirements: sourceRequirements }) }),
  updateDraft: (id: number, proposal: CurriculumProposal, sourceRequirements = "") => request<Curriculum>(`/api/curricula/${id}/draft`, { method: "PUT", body: JSON.stringify({ proposal, source_requirements: sourceRequirements }) }),
  confirmCurriculum: (id: number) => request<Curriculum>(`/api/curricula/${id}/confirm`, { method: "POST" }),
  activateCurriculum: (id: number) => request<Curriculum>(`/api/curricula/${id}/activate`, { method: "POST" }),
  courseTopic: (topicId: number, lessonId?: number) => request<CourseTopic>(`/api/course/topics/${topicId}${lessonId ? `?lesson_id=${lessonId}` : ""}`),
  viewCourseSection: (topicId:number, slug:string, lessonId?:number) => request<LessonProgress>(`/api/course/topics/${topicId}/sections/${slug}/view${lessonId ? `?lesson_id=${lessonId}` : ""}`, {method:"POST"}),
  completeCourseSection: (topicId:number, slug:string, lessonId?:number) => request<LessonProgress>(`/api/course/topics/${topicId}/sections/${slug}/complete${lessonId ? `?lesson_id=${lessonId}` : ""}`, {method:"POST"}),
  practiceHistory: (topicId: number) => request<PracticeHistory>(`/api/practice/topics/${topicId}/history`),
  mastery: (topicId: number) => request<MasteryBreakdown>(`/api/topics/${topicId}/mastery`),
  reviewsDue: () => request<ReviewQueueItem[]>("/api/reviews/due"),
  reviewsUpcoming: () => request<{ tomorrow: number; next_7_days: number; items: ReviewQueueItem[]; recently_reviewed: { topic_id: number; topic_name: string; score: number; at: string }[] }>("/api/reviews/upcoming"),
  todayPlan: () => request<TodayPlan>("/api/planner/today"),
  regeneratePlan: () => request<TodayPlan>("/api/planner/regenerate",{method:"POST"}),
  plannerOptions: () => request<{key:string;topic_name:string;subject:string;kind:string}[]>("/api/planner/options"),
  replacePlanItem: (id:number,key:string) => request<TodayPlan>(`/api/planner/items/${id}/replace?activity_key=${encodeURIComponent(key)}`,{method:"POST"}),
  skipPlanItem: (id: number) => request<{ status: string }>(`/api/planner/items/${id}/skip`, { method: "POST" }),
  completePlanItem: (id: number) => request<{ status: string }>(`/api/planner/items/${id}/complete`, { method: "POST" }),
  plannerSettings: () => request<PlannerSettings>("/api/planner/settings"),
  updatePlannerSettings: (values: Partial<PlannerSettings>) => request<PlannerSettings>("/api/planner/settings", { method: "PUT", body: JSON.stringify(values) }),
  learningPathDashboard: (activeSubject = "python") => request<LearningPathDashboardData>(`/api/learning-path/dashboard?active_subject=${encodeURIComponent(activeSubject)}`),
  learningPathSubjects: () => request<SubjectProgressSummary[]>("/api/learning-path/subjects"),
  learningPathConcepts: (subjectKey: string) => request<ConceptStepSummary[]>(`/api/learning-path/subjects/${encodeURIComponent(subjectKey)}`),
  conceptStep: (stepKey: string) => request<ConceptStepDetail>(`/api/learning-path/steps/${encodeURIComponent(stepKey)}`),
  updateStepProgress: (stepKey: string, state: LearningStage) => request<{ status: string; step_key: string; progress_state: LearningStage }>(`/api/learning-path/steps/${encodeURIComponent(stepKey)}/progress?state=${encodeURIComponent(state)}`, { method: "POST" }),
  arenaStages: (track?: string) => request<ArenaStageDetail[]>(`/api/learning-path/arena/stages${track ? `?track=${encodeURIComponent(track)}` : ""}`),
  beginnerExercise: (key: string) => request<BeginnerExerciseData>(`/api/learning-path/exercises/${encodeURIComponent(key)}`),
  submitBeginnerExercise: (key: string, source: string) => request<BeginnerExerciseResult>(`/api/learning-path/exercises/${encodeURIComponent(key)}/submit`, { method: "POST", body: JSON.stringify({ source }) }),
};
