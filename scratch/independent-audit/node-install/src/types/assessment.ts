import type { PythonTest } from "./practice";
export interface StaticAssessment {
  id:string;session_id:number;topic_id:number|null;purpose:string;kind:"single_choice"|"multi_choice"|"numeric"|"python"|"sql"|"reflection";
  prompt:string;item_key:string;content_sha256:string;status:string;approval:string;assisted:boolean;hints_used:number;hints_available:number;
  contract:{choices?:Record<string,string>;unit?:string;rounding?:string;boundary?:string;starter_code?:string;function_name?:string;mode?:"function"|"stdin_stdout";sample_tests?:PythonTest[];public_dataset?:{setup_sql:string};rubric?:unknown[]};
  result:{score:number|null;passed:boolean;explanation:string;message?:string;example?:string;answer?:unknown;worked_answer?:unknown;verification?:string}|null;
  draft?:StaticSubmission;error?:string;policy_version:string;judge_version:string;
}
export interface StaticSubmission {content_sha256:string;answer:string|string[];unit:string;source:string}
export interface StaticInterview {id:number;mode:string;status:string;legacy:boolean;read_only?:boolean;message?:string;deadline_at?:string|null;responses?:{id:number;saved_answer:string|null;score:number;evaluation_json:string}[];questions:{id:number;competency:string;assessment?:StaticAssessment;prompt_markdown?:string}[]}
export interface StaticReport {label?:string;overall_score:number|null;disclaimer?:string;questions?:{competency:string;score:number|null;explanation:string;example?:string;answer?:unknown}[];[key:string]:unknown}
