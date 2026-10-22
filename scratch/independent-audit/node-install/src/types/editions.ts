export interface ContentAvailability {
  lesson_status: "approved" | "legacy" | "planned";
  lesson_count: number; approved_lesson_count: number; legacy_lesson_count: number;
  practice_available: boolean; approved_practice_available: boolean;
  course_exercise_count: number; arena_count: number;
  assessment_item_count?: number;
  completed_sections: number; total_sections: number; reading_percent: number;
}
export interface EditionDefinition {
  key: "placement-foundations" | "advanced-engineering";
  label: string; name: string; description: string; levels: number[];
  status: "preparing" | "future"; subjects: string[];
}
export interface EditionTopic {
  id: number | null; key: string; subject_key: string; title: string; description: string;
  level: number; prerequisites: string[]; estimated_minutes: number; priority: number;
  learning_outcomes: string[]; coverage_requirements: string[];
  assessment_route: string; content_key: string; availability: ContentAvailability;
}
export interface EditionSubject {
  key: string; name: string; description: string; priority: number; icon: string; topics: EditionTopic[];
}
export interface EditionOverview {
  edition: EditionDefinition; subjects: EditionSubject[]; active_curriculum_id: number | null;
  scope_version?: string; scope_sha256?: string;
  binding: {curriculum_id: number; name: string; version: number; status: string;
    graph_sha256: string; reviewed_by: string | null; is_active: boolean} | null;
}
export interface EditionIndex {
  subjects: {key:string;name:string}[];
  editions: EditionDefinition[]; selected_edition_key: string | null; active_curriculum_id: number | null;
}
export interface EditionConfirmation {
  graph_sha256: string; scope_sha256: string; reviewer: string;
  scope_reviewed: boolean; missing_content_acknowledged: boolean;
}
export interface TopicEditionMetadata {
  placement: {subject_key: string; level: number; edition_key: string; curriculum_id: number} | null;
  curriculum_status: string; availability: ContentAvailability;
}
