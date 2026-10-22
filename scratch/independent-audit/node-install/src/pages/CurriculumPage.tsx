import { EditionLearningPanel } from "../components/EditionLearningPanel";
import { ChevronDown, ChevronRight, LockKeyhole, Plus, Target } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ProgressBar } from "../components/ProgressBar";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

export function CurriculumPage() {
  const [params] = useSearchParams();
  const requestedTrack = Number(params.get("track"));
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [switching, setSwitching] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const list = useApi(api.curricula, []);
  const active = useApi(api.activeCurriculum, []);

  useEffect(() => { if (requestedTrack) setExpanded(new Set([requestedTrack])); }, [requestedTrack]);
  if (list.loading || active.loading) return <LoadingState />;
  if (list.error || active.error || !list.data || !active.data) return <ErrorState message={list.error ?? active.error ?? "No curriculum data returned"} />;
  const curriculum = active.data;
  const confirmed = list.data.filter((item) => item.status === "confirmed");
  const drafts = list.data.filter((item) => item.status === "draft");

  async function activate(id: number) {
    if (id === curriculum.id) return;
    setSwitching(true);
    setActionError(null);
    try { await api.activateCurriculum(id); window.location.reload(); }
    catch (reason) { setActionError(reason instanceof Error ? reason.message : "Could not switch curriculum."); setSwitching(false); }
  }
  function toggle(id: number) { setExpanded((current) => { const next = new Set(current); next.has(id) ? next.delete(id) : next.add(id); return next; }); }

  return <div className="mx-auto max-w-5xl"><EditionLearningPanel /><header className="mb-8"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex flex-wrap items-center gap-3"><h1 className="display text-3xl font-extrabold">Curriculum</h1><span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"><LockKeyhole className="mr-1 inline" size={13} /> Confirmed · v{curriculum.version}</span></div><p className="mt-2 max-w-2xl text-slate-500">{curriculum.description} Every topic remains available for manual study.</p></div><Link to="/curriculum/new" className="inline-flex items-center gap-2 rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-700"><Plus size={17} /> Create custom curriculum</Link></div><div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4"><label htmlFor="active-curriculum" className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-400">Active curriculum</label><select id="active-curriculum" value={curriculum.id} disabled={switching} onChange={(event) => void activate(Number(event.target.value))} className="w-full rounded-xl bg-slate-100 px-3 py-2.5 font-semibold outline-none">{confirmed.map((item) => <option key={item.id} value={item.id}>{item.name} · v{item.version}</option>)}</select>{actionError && <p className="mt-2 text-sm text-red-600">{actionError}</p>}</div>{drafts.length > 0 && <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4"><p className="text-xs font-bold uppercase tracking-wider text-amber-700">Drafts awaiting review</p><div className="mt-2 flex flex-wrap gap-2">{drafts.map((draft) => <Link key={draft.id} to={`/curriculum/drafts/${draft.id}`} className="rounded-lg bg-white px-3 py-2 text-sm font-semibold text-amber-900 shadow-sm">{draft.name} · Edit and confirm</Link>)}</div></div>}</header><div className="space-y-4">{curriculum.tracks.map((track) => { const open = expanded.has(track.id); return <section key={track.id} id={`track-${track.id}`} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"><button onClick={() => toggle(track.id)} aria-expanded={open} className="flex w-full items-center gap-4 p-5 text-left hover:bg-slate-50"><span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft font-bold text-accent">{track.order_index.toString().padStart(2,"0")}</span><span className="min-w-0 flex-1"><span className="display block font-bold">{track.name}</span><span className="mt-1 block truncate text-sm text-slate-500">{track.description}</span></span><span className="hidden w-36 sm:block"><span className="mb-1 block text-right text-xs font-semibold text-slate-500">{track.mastery}%</span><ProgressBar value={track.mastery} /></span>{open ? <ChevronDown size={20} /> : <ChevronRight size={20} />}</button>{open && <div className="border-t border-slate-100 bg-slate-50/70 p-3 sm:p-5"><div className="grid gap-2">{track.topics.map((topic) => <Link key={topic.id} to={`/topics/${topic.id}`} className="group flex items-center gap-3 rounded-xl border border-transparent bg-white p-4 hover:border-violet-200"><span className={`h-2.5 w-2.5 rounded-full ${topic.state.status === "not_started" ? "bg-slate-300" : "bg-accent"}`} /><span className="min-w-0 flex-1"><span className="font-medium group-hover:text-accent">{topic.name}</span>{topic.prerequisites.length > 0 && <span className="mt-1 block text-xs text-slate-400">After: {topic.prerequisites.map((item) => item.name).join(", ")}</span>}</span><span className="flex items-center gap-1 text-xs text-slate-400"><Target size={14} /> {topic.state.mastery_score}%</span><ChevronRight size={16} className="text-slate-300" /></Link>)}</div></div>}</section>; })}</div></div>;
}
