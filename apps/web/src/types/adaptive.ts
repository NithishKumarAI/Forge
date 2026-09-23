import type { Attempt, ExecutionResult, Exercise } from "./practice";

export interface MasteryBreakdown {
  topic_id: number; mastery_score: number; status: string; confidence: string;
  practice_score: number | null; practice_attempts: number; evidence_types: string[];
  transfer_eligible: boolean;
  transfer: { score: number; passed: boolean; assisted: boolean; at: string } | null;
  delayed_recall: { score: number; passed: boolean; at: string } | null;
  current_cap: number; cap_reason: string;
  mistakes: { category: string; description: string; occurrence_count: number; last_seen_at: string }[];
  next_review_at: string | null;
}

export interface TransferSession { session_id: number; topic_id: number; exercise: Exercise }
export interface AdaptiveSubmission { selected_index?: number; answer?: string; source?: string; execution?: ExecutionResult; assisted?: boolean }
export interface AdaptiveAttempt extends Attempt { transfer_passed?: boolean; message?: string; fsrs_rating?: number; next_due_at?: string }
export interface ReviewQueueItem { topic_id: number; topic_name: string; track_name: string; due_at: string }
export interface ReviewSessionItem { session_id: number; topic_id: number; topic_name: string; exercise: Exercise }
export interface PlannerItem { id: number; topic_id: number | null; topic_name: string | null; track_name: string | null; item_type: string; reason: string; estimated_minutes: number; order_index: number; status: string; action_path: string }
export interface TodayPlan { date: string; target_minutes: number; planned_minutes: number; items: PlannerItem[] }
export interface PlannerSettings { daily_study_target: number; python_daily_minimum: number; sql_daily_minimum: number; dsa_daily_minimum: number; max_review_topics: number; desired_retention: number }
