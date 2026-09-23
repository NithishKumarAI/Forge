export interface TopicState {
  mastery_score: number;
  confidence: string;
  status: string;
  attempts: number;
  last_studied_at: string | null;
  last_tested_at: string | null;
  next_review_at: string | null;
}

export interface Prerequisite {
  id: number;
  name: string;
  slug: string;
  mastery_score: number;
  status: string;
}

export interface Topic {
  id: number;
  track_id: number;
  track_name: string;
  name: string;
  slug: string;
  description: string;
  order_index: number;
  priority: number;
  target_level: string;
  estimated_minutes: number;
  state: TopicState;
  prerequisites: Prerequisite[];
  reason?: string | null;
}

export interface TrackSummary {
  id: number;
  curriculum_id: number;
  name: string;
  slug: string;
  description: string;
  order_index: number;
  priority: number;
  mastery: number;
  topic_count: number;
}

export interface Track extends TrackSummary { topics: Topic[] }

export interface Curriculum {
  id: number;
  name: string;
  description: string;
  source_type: string;
  status: string;
  version: number;
  created_at: string;
  confirmed_at: string | null;
  track_count: number;
  tracks: Track[];
}

export type CurriculumSummary = Omit<Curriculum, "tracks">;

export interface TopicProposal {
  key: string;
  name: string;
  description: string;
  priority: number;
  target_level: string;
  estimated_minutes: number;
  prerequisites: string[];
  added_as_prerequisite: boolean;
}

export interface TrackProposal {
  key: string;
  name: string;
  description: string;
  priority: number;
  topics: TopicProposal[];
}

export interface CurriculumProposal {
  name: string;
  description: string;
  goal: string;
  tracks: TrackProposal[];
}

export interface TutorTurn {
  message_markdown: string;
  turn_type: "explain" | "check" | "feedback" | "clarify" | "transition" | "wrap_up";
  question: string | null;
  concepts_covered: string[];
  suggested_next_action: string | null;
}

export interface AIStatus {
  configured: boolean;
  provider: string;
  model: string;
  this_month: {
    calls: number;
    input_tokens: number;
    output_tokens: number;
    thought_tokens: number;
    cached_tokens: number;
    estimated_cost_usd: number;
    budget: { monthly_gemini_budget: number; pause_nonessential_ai: boolean; used_percent: number; level: string; message: string; disclaimer: string };
  };
}

export interface Dashboard {
  interview_readiness: number;
  active_curriculum: { id: number; name: string; version: number } | null;
  tracks: TrackSummary[];
  recommendations: Topic[];
  readiness: { readiness: number; strong_or_ready_topics: number; ready_topics: number; total_topics: number; high_priority_gaps: number; disclaimer: string };
  reviews_due: number;
  today_plan: import("./adaptive").TodayPlan;
}
