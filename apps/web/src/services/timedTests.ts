import {request} from "./api";
import type {StaticSubmission} from "../types/assessment";
import type {TimedSession,TimedReport} from "../types/timedTests";
export const timedTests={
 start:(kind:string,subject?:string,level?:number)=>request<TimedSession>("/api/timed-tests/start",{method:"POST",body:JSON.stringify({kind,subject:subject||null,level:level||null})}),
 read:(id:string)=>request<TimedSession>(`/api/timed-tests/${id}`),
 draft:(id:string,position:number,body:StaticSubmission)=>request<TimedSession>(`/api/timed-tests/${id}/draft`,{method:"POST",body:JSON.stringify({...body,position})}),
 answer:(id:string,position:number,body:StaticSubmission)=>request<TimedSession>(`/api/timed-tests/${id}/answer`,{method:"POST",body:JSON.stringify({...body,position})}),
 complete:(id:string)=>request<TimedReport>(`/api/timed-tests/${id}/complete`,{method:"POST"}),
 abandon:(id:string)=>request<TimedSession>(`/api/timed-tests/${id}/abandon`,{method:"POST"}),
 history:()=>request<{id:string;status:string;started_at:string;deadline_at:string}[]>("/api/timed-tests/history")
};
