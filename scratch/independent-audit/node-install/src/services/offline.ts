import { request } from "./api";
import type { StaticAssessment,StaticSubmission,StaticInterview,StaticReport } from "../types/assessment";
const post=(body?:unknown)=>({method:"POST",...(body===undefined?{}:{body:JSON.stringify(body)})});
export const offline={
  start:(topic_id:number,purpose="practice")=>request<StaticAssessment>("/api/assessment/start",post({topic_id,purpose})),
  assessment:(id:string)=>request<StaticAssessment>(`/api/assessment/${id}`),
  submit:(id:string,body:StaticSubmission)=>request<StaticAssessment>(`/api/assessment/${id}/submit`,post(body)),
  hint:(id:string)=>request<{text:string}>(`/api/assessment/${id}/hint`,post()),
  reveal:(id:string)=>request<StaticAssessment["result"]>(`/api/assessment/${id}/give-up`,post()),
  search:(q:string,topic?:number)=>request<{results:{url:string;title:string;markdown:string;revision:string;section_slug:string;approval:string;sources:{title:string;url:string}[]}[];message:string}>(`/api/guidance/search?q=${encodeURIComponent(q)}${topic?`&topic_id=${topic}`:""}`),
  history:(topic?:number)=>request<{id:number;role:string;content:string}[]>(`/api/guidance/history${topic?`?topic_id=${topic}`:""}`),
  interviews:()=>request<{id:number;mode:string;status:string;legacy:boolean}[]>("/api/interviews/history"),
  startInterview:(mode:string)=>request<StaticInterview>("/api/interviews/start",post({mode})),
  interview:(id:number)=>request<StaticInterview>(`/api/interviews/${id}`),
  answerInterview:(id:number,question_id:number,body:StaticSubmission)=>request<StaticInterview>(`/api/interviews/${id}/answer`,post({...body,question_id})),
  completeInterview:(id:number)=>request<StaticReport>(`/api/interviews/${id}/complete`,post()),
  report:(id:number)=>request<StaticReport>(`/api/interviews/${id}/report`),
  transition:(id:number,action:string)=>request<StaticInterview>(`/api/interviews/${id}/${action}`,post()),
};
