import { useState } from "react";
import { Link,useParams } from "react-router-dom";
import { offline } from "../services/offline";
import { Markdown } from "../components/Markdown";
export function TutorPage(){
 const id=Number(useParams().topicId)||undefined,[query,setQuery]=useState(""),[results,setResults]=useState<Awaited<ReturnType<typeof offline.search>>|null>(null),[history,setHistory]=useState<Awaited<ReturnType<typeof offline.history>>>([]),[error,setError]=useState("");
 async function search(){setError("");try{setResults(await offline.search(query,id));}catch(e){setError(e instanceof Error?e.message:"Search unavailable");}}
 async function legacy(){try{setHistory(await offline.history(id));}catch(e){setError(String(e));}}
 return <div className="mx-auto max-w-4xl"><h1 className="display text-3xl font-bold">Static learning guidance</h1><p className="mt-3 text-slate-600">Search exact authored explanations, examples and common mistakes in your curriculum. No conversational generation. Help during an open transfer is recorded as assistance.</p>
 <form onSubmit={e=>{e.preventDefault();void search();}} className="mt-6 flex gap-3"><label className="flex-1">Search local lessons<input minLength={2} required value={query} onChange={e=>setQuery(e.target.value)} className="mt-1 w-full rounded-xl border p-3"/></label><button className="self-end rounded-xl bg-accent px-5 py-3 font-semibold text-white">Search</button></form>
 {error&&<p role="alert" className="mt-4 rounded-xl bg-amber-50 p-4">{error}</p>}{results&&results.results.length===0&&<p className="mt-5">No matching stored explanation. Try a shorter concept or open the subject outline.</p>}
 {results?.results.map(r=><article key={r.url+r.section_slug} className="mt-4 rounded-2xl border bg-white p-5"><Link className="font-bold text-accent" to={r.url+`&section=${encodeURIComponent(r.section_slug)}`}>{r.title} · revision {r.revision}</Link><p className="mt-2 text-xs font-semibold">{r.approval==="approved"?"Approved lesson":"Legacy lesson · not fully verified"}</p><div className="mt-3"><Markdown>{r.markdown}</Markdown></div><ul className="mt-3 text-xs">{r.sources?.map(source=><li key={source.url}><a className="text-accent underline" href={source.url} target="_blank" rel="noreferrer">{source.title}</a></li>)}</ul></article>)}
 <button onClick={()=>void legacy()} className="mt-6 rounded-xl border px-4 py-2">Read legacy conversation history</button>{history.map(h=><article key={h.id} className="mt-3 rounded-xl border p-4"><p className="text-xs font-semibold">Historical {h.role} message · unverified model-era guidance</p><Markdown>{h.content}</Markdown></article>)}</div>;
}
