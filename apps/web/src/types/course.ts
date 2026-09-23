export type SourceReference={source_id:string;title:string;url:string;retrieved_at:string};
export type CodeExample={language:string;code:string;expected_output?:string|null;explanation:string};
export type LessonSection={slug:string;title:string;order_index:number;estimated_minutes:number;learning_objective:string;markdown:string;examples:CodeExample[];key_points:string[];checkpoint?:string|null};
export type StaticLesson={curriculum_key:string;track_slug:string;topic_slug:string;title:string;description:string;version:string;learning_objectives:string[];prerequisites:string[];sections:LessonSection[];summary:string[];interview_takeaways:string[];common_mistakes:string[];sources:SourceReference[];content_hash:string;generated_at:string};
export type LessonProgress={completed_sections:number;total_sections:number;percent:number;current_section_slug:string};
export type CourseTopic={lesson:StaticLesson;progress:LessonProgress};
