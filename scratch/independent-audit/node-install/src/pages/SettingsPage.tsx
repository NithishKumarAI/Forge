import {useEffect,useState} from "react";
import {api} from "../services/api";
import type {PlannerSettings} from "../types/adaptive";
const fields=[
 {key:"daily_study_target",label:"Net study minutes",min:30,max:480,step:1},
 {key:"python_daily_minimum",label:"Python target minimum",min:0,max:180,step:1},
 {key:"sql_daily_minimum",label:"SQL target minimum",min:0,max:180,step:1},
 {key:"dsa_daily_minimum",label:"DSA target minimum",min:0,max:120,step:1},
 {key:"max_review_topics",label:"Maximum review topics",min:1,max:30,step:1},
 {key:"desired_retention",label:"FSRS desired retention",min:.7,max:.97,step:.01}
] as const;
export function SettingsPage(){
 const [form,setForm]=useState<PlannerSettings>({daily_study_target:300,python_daily_minimum:45,sql_daily_minimum:30,dsa_daily_minimum:30,max_review_topics:10,desired_retention:.9,study_timezone:"Asia/Kolkata"}),[message,setMessage]=useState("");
 useEffect(()=>{api.plannerSettings().then(setForm).catch(e=>setMessage(String(e)));},[]);
 async function save(){try{setForm(await api.updatePlannerSettings(form));setMessage("Settings saved. Regenerate today's plan explicitly to apply the new budget.");}catch(e){setMessage(e instanceof Error?e.message:"Save failed");}}
 return <div className="mx-auto max-w-4xl"><h1 className="display text-3xl font-bold">Settings</h1><p className="mt-3 text-slate-600">Static learning and deterministic assessment require no model account or API key.</p><form onSubmit={e=>{e.preventDefault();void save();}} className="mt-6 rounded-3xl border bg-white p-6"><h2 className="display text-xl font-bold">Advisory study plan</h2><p className="mt-2 text-sm text-slate-500">Breaks are outside net study minutes. Minima are clipped to the budget and actual content. Task completion never awards mastery.</p><fieldset className="mt-4"><legend className="text-sm font-semibold">Daily target presets</legend><div className="mt-2 flex flex-wrap gap-2">{[300,360,480].map(minutes=><button type="button" key={minutes} aria-pressed={form.daily_study_target===minutes} className="rounded-xl border px-4 py-2 aria-pressed:bg-accent-soft" onClick={()=>setForm({...form,daily_study_target:minutes})}>{minutes/60} hours · {minutes} min</button>)}</div></fieldset><div className="mt-5 grid gap-4 sm:grid-cols-2">{fields.map(({key,label,min,max,step})=><label key={key} className="text-sm font-semibold">{label}<input required type="number" min={min} max={max} step={step} value={form[key]} onChange={e=>setForm({...form,[key]:Number(e.target.value)})} className="mt-2 w-full rounded-xl border p-3"/></label>)}<label className="text-sm font-semibold">Study timezone<input required value={form.study_timezone} onChange={e=>setForm({...form,study_timezone:e.target.value})} className="mt-2 w-full rounded-xl border p-3"/><span className="mt-1 block text-xs text-slate-500">IANA name, for example Asia/Kolkata, UTC or America/New_York. Recall still uses UTC elapsed time.</span></label></div><button className="mt-5 rounded-xl bg-accent px-5 py-3 font-semibold text-white">Save plan settings</button>{message&&<p role="status" className="mt-4">{message}</p>}</form></div>;
}
