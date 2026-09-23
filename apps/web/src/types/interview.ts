import type { Exercise, ExecutionResult } from "./practice";

export interface InterviewMode { mode: string; title: string; target_minutes: number; question_count: number }
export interface InterviewQuestion { id: number; section: string; competency: string; question_type: string; prompt_markdown: string; difficulty: string; suggested_seconds: number; order_index: number; is_follow_up: boolean; exercise: Exercise | null }
export interface InterviewSession { id: number; mode: string; title: string; status: string; target_minutes: number; main_question_count: number; answered_count: number; current_question: InterviewQuestion | null; can_complete: boolean; started_at: string; completed_at: string | null; overall_score: number | null }
export interface InterviewHistory { id: number; mode: string; title: string; status: string; started_at: string; completed_at: string | null; overall_score: number | null }
export interface InterviewReport { label: string; overall_score: number; section_scores: Record<string, number>; strengths: string[]; priority_gaps: string[]; communication_feedback: string[]; recommended_topics: { topic_id: number; topic_name: string; reason: string }[]; summary: string; disclaimer: string }
export interface InterviewCodingSubmission { source: string; execution: ExecutionResult; duration_seconds?: number }
