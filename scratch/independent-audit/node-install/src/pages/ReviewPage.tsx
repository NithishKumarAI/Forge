import { useEffect,useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { offline } from "../services/offline";
import { AssessmentCard } from "../components/AssessmentCard";
import type { StaticAssessment } from "../types/assessment";
import type { ReviewQueueItem } from "../types/adaptive";
export function ReviewPage(){
 const [due,setDue]=useState<ReviewQueueItem[]>([]),[item,setItem]=useState<StaticAssessment|null>(null),[error,setError]=useState("");
 const load=()=>api.reviewsDue().then(setDue).catch(e=>setError(String(e)));
 useEffect(()=>{void load();},[]);
 async function start(id:number){setError("");try{setItem(await offline.start(id,"recall"));}catch(e){setError(e instanceof Error?e.message:"No approved recall questions");}}
 return <div className="mx-auto max-w-4xl"><h1 className="display text-3xl font-bold">Delayed recall</h1><p className="mt-3 text-slate-600">FSRS controls when review is due. Independent recall after clean transfer requires at least 24 elapsed hours.</p>{error&&<p role="alert" className="mt-4 rounded-xl bg-amber-50 p-4">{error}</p>}
 {due.length===0&&<p className="mt-5">No reviews are due. <Link to="/curriculum" className="text-accent">Choose any topic manually.</Link></p>}
 <ul className="mt-5 space-y-3">{due.map(row=><li key={row.topic_id} className="flex items-center justify-between rounded-xl border bg-white p-4"><span>{row.topic_name}</span><button className="font-semibold text-accent" onClick={()=>void start(row.topic_id)}>Start due recall</button></li>)}</ul>
 {item&&<AssessmentCard key={item.id} item={item} onChange={value=>{setItem(value);if(value.status!=="open")void load();}}/>}</div>;
}
