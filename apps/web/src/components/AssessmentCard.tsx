import { useState,lazy,Suspense } from "react";
import { Markdown } from "./Markdown";
import type { StaticAssessment,StaticSubmission } from "../types/assessment";
import { offline } from "../services/offline";
import { runPython } from "../features/practice/pythonRunner";
import { runSql } from "../features/arena/sqlRunner";
import { AssessmentInputs } from "./AssessmentInputs";
const CodeEditor=lazy(()=>import("./CodeEditor").then(module=>({default:module.CodeEditor})));

export function AssessmentCard({item,onChange,onSubmit}:{item:StaticAssessment;onChange:(item:StaticAssessment)=>void;onSubmit?:(body:StaticSubmission)=>Promise<void>}) {
  const [answer,setAnswer]=useState<string[]>([]),[text,setText]=useState(""),[unit,setUnit]=useState(item.contract.unit??"");
  const [source,setSource]=useState(item.contract.starter_code??""),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
  const [worked,setWorked]=useState<unknown>();
  async function act(run:()=>Promise<void>){setBusy(true);setMessage("");try{await run();}catch(e){setMessage(e instanceof Error?e.message:"Action failed");}finally{setBusy(false);}}
  const canRun=item.kind==="python"?Boolean(item.contract.sample_tests?.length):Boolean(item.contract.public_dataset);
  const coding=item.kind==="python"||item.kind==="sql",open=item.status==="open",interview=item.purpose==="interview";
  async function submit(){const body={content_sha256:item.content_sha256,answer:item.kind==="single_choice"||item.kind==="multi_choice"?answer:text,unit,source};
    if(onSubmit)await onSubmit(body);else{const value=await offline.submit(item.id,body);onChange(value);if(value.error)setMessage(value.error);}}
  async function run(){if(item.kind==="python") {const value=await runPython({code:source,functionName:item.contract.function_name,judgeMode:item.contract.mode,tests:item.contract.sample_tests??[]});setMessage(`Public samples: ${value.status}. ${value.stdout} ${value.stderr}`);}
    else if(item.contract.public_dataset){const value=await runSql(item.contract.public_dataset.setup_sql,source);setMessage(value.ok?JSON.stringify(value.rows):value.error??"Query failed");}
    else setMessage("No public SQL sample is published. Submit uses isolated complete fixtures.");}
  return <article className="mt-5 rounded-3xl border bg-white p-6 sm:p-8"><div className="flex flex-wrap gap-2 text-xs font-semibold"><span>{item.approval==="approved"?"Approved static assessment":item.kind==="reflection"?"Reflection only":"Historical unverified exercise"}</span><span>· {item.purpose} · {item.status}</span>{item.assisted&&<span>· Assisted</span>}</div>
    <div className="mt-4"><Markdown>{item.prompt}</Markdown></div>
    <AssessmentInputs item={item} answer={answer} text={text} unit={unit} disabled={!open||busy} onAnswer={setAnswer} onText={setText} onUnit={setUnit}/>
    {item.kind==="reflection"&&<><p className="mt-3 text-sm text-slate-600">Write your response. This is unscored and never raises mastery.</p><ul className="mt-3 list-disc pl-5">{item.contract.rubric?.map((r,i)=><li key={i}>{typeof r==="string"?r:JSON.stringify(r)}</li>)}</ul><textarea aria-label="Reflection response" disabled={!open||busy} value={text} onChange={e=>setText(e.target.value)} rows={7} className="mt-4 w-full rounded-xl border p-3"/></>}
    {item.kind==="sql"&&item.contract.public_dataset&&<details className="mt-4 rounded-xl border p-3"><summary className="cursor-pointer font-semibold">Public SQL schema and sample data</summary><pre className="mt-3 overflow-auto text-sm">{item.contract.public_dataset.setup_sql}</pre></details>}
    {coding&&<section className="mt-4"><h2 className="mb-2 font-semibold">{item.kind==="sql"?"SQL query":"Python source"}</h2><Suspense fallback={<p>Loading code editor…</p>}><CodeEditor value={source} onChange={setSource} language={item.kind==="sql"?"sql":"python"} readOnly={!open||busy}/></Suspense></section>}
    {open&&<div className="mt-5 flex flex-wrap gap-3">{coding&&canRun&&<button disabled={busy} onClick={()=>void act(run)} className="rounded-xl border px-4 py-2">Run public samples</button>}<button disabled={busy} onClick={()=>void act(submit)} className="rounded-xl bg-accent px-4 py-2 font-semibold text-white">{item.kind==="reflection"?"Save reflection":"Submit"}</button>
      {!interview&&item.hints_available>0&&<button disabled={busy} onClick={()=>void act(async()=>{setMessage((await offline.hint(item.id)).text);onChange(await offline.assessment(item.id));})} className="rounded-xl border px-4 py-2">Reveal hint</button>}
      {!interview&&<button disabled={busy} onClick={()=>void act(async()=>{await offline.reveal(item.id);onChange(await offline.assessment(item.id));})} className="rounded-xl border px-4 py-2">Give up and reveal</button>}</div>}
    {message&&<p role="status" className="mt-4 whitespace-pre-wrap rounded-xl bg-amber-50 p-3 text-sm">{message}</p>}
    {item.result&&<section className="mt-5 rounded-xl bg-slate-50 p-4"><p className="font-semibold">{item.result.score===null?(item.kind==="reflection"?"Reflection only":"Revealed · no mastery credit"):`${item.result.passed?"Passed":"Not passed"} · ${item.result.score}%`}</p><Markdown>{item.result.explanation}</Markdown>{item.result.example&&<p>{item.result.example}</p>}</section>}
    {item.result&&<button disabled={busy} className="mt-4 rounded-xl border px-4 py-2" onClick={()=>void act(async()=>{setWorked((await offline.reveal(item.id))?.worked_answer);})}>View worked answer</button>}
    {(worked!==undefined||item.result?.worked_answer!==undefined)&&<pre className="mt-4 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950 p-4 text-sm text-white">{typeof (worked??item.result?.worked_answer)==="string"?String(worked??item.result?.worked_answer):JSON.stringify(worked??item.result?.worked_answer,null,2)}</pre>}
    {!open&&!item.result&&<p className="mt-4 text-sm">Response saved. Detailed feedback is available after the full interview is complete.</p>}
  </article>;
}
