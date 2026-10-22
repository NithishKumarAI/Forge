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

export interface Dashboard {
  content_status?:{approved_lessons:number;legacy_lessons:number;missing_topics:number;total_topics:number};
  reading_progress?:{saved_revision_sections:number;completed_revision_sections:number};
  recent_mistakes?:{topic_id:number;topic_name:string;description:string;occurrence_count:number}[];
  interview_readiness: number;
  active_curriculum: { id: number; name: string; version: number } | null;
  tracks: TrackSummary[];
  recommendations: Topic[];
  readiness: { readiness: number; strong_or_ready_topics: number; ready_topics: number; total_topics: number; high_priority_gaps: number; disclaimer: string };
  reviews_due: number;
  today_plan: import("./adaptive").TodayPlan;
}
