import type {StaticAssessment} from "./assessment";
export interface TimedReport {
 label:string;overall_score:number;earned_points:number;maximum_points:number;completion_reason:string;disclaimer:string;
 questions:{position:number;subject:string;item_key:string;score:number;points:number;unanswered:boolean;explanation:string;worked_answer:unknown;submitted_answer:unknown;mistake_analysis:string|null}[];
}
export interface TimedSession {
 id:string;status:string;started_at:string;deadline_at:string;remaining_seconds:number;
 blueprint:{id:string;title:string;question_count:number;allowed_seconds:number;negative_mark:number;notice:string};
 questions:{position:number;weight:number;negative_mark:number;assessment:StaticAssessment}[];
 report:TimedReport|null;error?:string;
}
