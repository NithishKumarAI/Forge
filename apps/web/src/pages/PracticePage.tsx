import { useState,useEffect } from "react";
import { Link,useParams,useSearchParams } from "react-router-dom";
import { offline } from "../services/offline";
import { AssessmentCard } from "../components/AssessmentCard";
import type { StaticAssessment } from "../types/assessment";
export function PracticePage({purpose="practice"}:{purpose?:string}) {
 const id=Number(useParams().topicId),[params,setParams]=useSearchParams();
 const [item,setItem]=useState<StaticAssessment|null>(null),[error,setError]=useState(""),[busy,setBusy]=useState(false);
 const selected=params.get("assessment");
 useEffect(()=>{if(selected)offline.assessment(selected).then(setItem).catch(e=>setError(String(e)));},[selected]);
 async function start(){setBusy(true);setError("");try{const value=await offline.start(id,purpose);setItem(value);setParams({assessment:value.id});}catch(e){setError(e instanceof Error?e.message:"No approved questions");}finally{setBusy(false);}}
 return <div className="mx-auto max-w-4xl"><Link className="text-accent" to={`/topics/${id}`}>Topic overview</Link><h1 className="display mt-5 text-3xl font-bold">{purpose==="transfer"?"Independent transfer":purpose==="recall"?"Delayed recall":"Static practice"}</h1><p className="mt-3 text-slate-600">{purpose==="transfer"?"Reviewed unseen variants only. Help is recorded; revealing an answer disqualifies clean transfer.":"Questions come from stored content. Repetition supports learning without repeated mastery credit."}</p>
 {error&&<p role="alert" className="mt-5 rounded-xl bg-amber-50 p-4">{error} <Link className="font-semibold text-accent" to={`/topics/${id}/learn`}>Open available learning</Link></p>}
 {item&&<AssessmentCard key={item.id} item={item} onChange={setItem}/>}
 {(!item||item.status!=="open")&&<button disabled={busy} onClick={()=>void start()} className="mt-6 rounded-xl bg-accent px-5 py-3 font-semibold text-white">{item?"Choose next static item":"Start"}</button>}
 </div>;
}
