export type LearningStage =
  | "not_started"
  | "learning"
  | "practising"
  | "ready_to_advance"
  | "retained"
  | "review_due";

export type ExerciseProgressionStage =
  | "first_steps"
  | "beginner"
  | "developing"
  | "intermediate"
  | "challenging";

export interface WorkedExample {
  title: string;
  code: string;
  explanation: string;
}

export interface TracingStep {
  step_number: number;
  line_or_expression: string;
  state_description: string;
  result_or_value: string;
}

export interface CommonMistake {
  mistake_description: string;
  wrong_code: string;
  explanation: string;
  correct_code: string;
}

export interface ConceptTeachingContent {
  summary: string;
  why_it_matters: string;
  intuition: string;
  analogy: string;
  syntax_guide: string;
  worked_example_title: string;
  worked_example_code: string;
  worked_example_explanation: string;
  tracing_steps: TracingStep[];
  common_mistakes: CommonMistake[];
  revision_notes: string[];
}

export interface TeachingRef {
  source_type: string;
  content_key: string;
  section_slug: string;
}

export interface ConceptStepSummary {
  key: string;
  subject_key: string;
  topic_slug: string;
  title: string;
  stage: ExerciseProgressionStage;
  order_index: number;
  objective: string;
  prerequisite_keys: string[];
  progress_state: LearningStage;
  prerequisites_met: boolean;
  is_current: boolean;
  action_path: string;
  action_label: string;
}

export interface ConceptStepDetail extends ConceptStepSummary {
  teaching_ref?: TeachingRef;
  worked_example?: WorkedExample;
  teaching_content?: ConceptTeachingContent;
  guided_practice_refs: string[];
  independent_practice_refs: string[];
  availability_status: string;
  review_eligible: boolean;
}

export interface LearningRecommendation {
  kind: "resume" | "review" | "prerequisite" | "next_concept" | "practice" | "secondary_subject";
  subject_key: string;
  subject_name: string;
  concept_key: string;
  concept_title: string;
  stage: string;
  objective: string;
  progress_state: LearningStage;
  progress_summary: string;
  reason: string;
  action_path: string;
  action_label: string;
  priority_tier: number;
  is_primary: boolean;
}

export interface SubjectProgressSummary {
  subject_key: string;
  subject_name: string;
  description: string;
  icon: string;
  total_concepts: number;
  completed_concepts: number;
  in_progress_concepts: number;
  current_concept_title?: string | null;
  current_concept_key?: string | null;
  progress_state: LearningStage;
  action_path: string;
}

export interface LearningPathDashboardData {
  primary_recommendation: LearningRecommendation | null;
  secondary_recommendations: LearningRecommendation[];
  active_subject: string;
  subjects: SubjectProgressSummary[];
  content_availability: {
    status: string;
    description: string;
    approved_lessons: number;
    legacy_reference_lessons: number;
    beginner_exercises_ready: number;
    total_curriculum_topics: number;
    note: string;
  };
  recent_mistakes: Array<{
    id?: number;
    topic_id?: number;
    topic_name: string;
    category?: string;
    description: string;
    occurrence_count: number;
  }>;
  reviews_due_count: number;
  active_curriculum?: {
    id: number;
    name: string;
    version: number;
  } | null;
}

export interface ArenaStageProblem {
  key: string;
  title: string;
  track: "python" | "sql" | "dsa";
  difficulty: "easy" | "medium";
  stage: ExerciseProgressionStage;
  concept?: string;
  prerequisites?: string[];
  solved?: boolean;
  topic_tags: string[];
  estimated_minutes: number;
}

export interface ArenaStageDetail {
  key: ExerciseProgressionStage;
  name: string;
  description: string;
  order_index: number;
  badge_color: string;
  problems: ArenaStageProblem[];
  solved_count: number;
  total_count: number;
}

export interface BeginnerExerciseData {
  key: string;
  track: "python" | "sql" | "dsa";
  stage: string;
  title: string;
  concept_key: string;
  concept_title?: string;
  instructions: string;
  starter_code?: string;
  starter_query?: string;
  setup_sql?: string;
  examples: Array<{ input: string; output: string; explanation?: string }>;
  hints: string[];
  solved: boolean;
}

export interface BeginnerExerciseResult {
  exercise_key: string;
  passed: boolean;
  score: number;
  output: string;
  errors?: string;
  feedback: string;
  solution?: string | null;
  explanation?: string | null;
}
