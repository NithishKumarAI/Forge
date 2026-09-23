import { ArrowDown, ArrowLeft, ArrowUp, LoaderCircle, Plus, Sparkles, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { CurriculumProposal, TopicProposal, TrackProposal } from "../types/api";

export function CurriculumBuilderPage() {
  const draftIdParam = useParams().curriculumId;
  const initialDraftId = draftIdParam ? Number(draftIdParam) : null;
  const [requirements, setRequirements] = useState("");
  const [preferredName, setPreferredName] = useState("");
  const [goal, setGoal] = useState("");
  const [proposal, setProposal] = useState<CurriculumProposal | null>(null);
  const [draftId, setDraftId] = useState<number | null>(initialDraftId);
  const [confirmed, setConfirmed] = useState(false);
  const [confirmReady, setConfirmReady] = useState(false);
  const [busy, setBusy] = useState(Boolean(initialDraftId));
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (!initialDraftId) return;
    api.proposal(initialDraftId)
      .then(setProposal)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Could not load draft."))
      .finally(() => setBusy(false));
  }, [initialDraftId]);

  async function generate() {
    if (requirements.trim().length < 3) { setError("Paste at least a few words describing what you want to learn."); return; }
    setBusy(true); setError(null); setNotice(null);
    try {
      const generated = await api.generateCurriculum({ requirements, name: preferredName || undefined, goal: goal || undefined });
      setProposal(generated);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Curriculum generation failed."); }
    finally { setBusy(false); }
  }

  function updateTrack(index: number, patch: Partial<TrackProposal>) {
    setProposal((current) => current && ({ ...current, tracks: current.tracks.map((track, trackIndex) => trackIndex === index ? { ...track, ...patch } : track) }));
  }
  function updateTopic(trackIndex: number, topicIndex: number, patch: Partial<TopicProposal>) {
    setProposal((current) => current && ({ ...current, tracks: current.tracks.map((track, ti) => ti === trackIndex ? { ...track, topics: track.topics.map((topic, i) => i === topicIndex ? { ...topic, ...patch } : topic) } : track) }));
  }
  function removeTopic(trackIndex: number, topicIndex: number) {
    setProposal((current) => current && ({ ...current, tracks: current.tracks.map((track, ti) => ti === trackIndex ? { ...track, topics: track.topics.filter((_, i) => i !== topicIndex) } : track) }));
  }
  function moveTopic(trackIndex: number, topicIndex: number, direction: -1 | 1) {
    setProposal((current) => {
      if (!current) return current;
      const tracks = [...current.tracks];
      const track = { ...tracks[trackIndex], topics: [...tracks[trackIndex].topics] };
      const destination = topicIndex + direction;
      if (destination < 0 || destination >= track.topics.length) return current;
      [track.topics[topicIndex], track.topics[destination]] = [track.topics[destination], track.topics[topicIndex]];
      tracks[trackIndex] = track;
      return { ...current, tracks };
    });
  }
  function addTopic(trackIndex: number) {
    const topic: TopicProposal = { key: `new-topic-${Date.now()}`, name: "New topic", description: "Describe what the learner should understand and apply.", priority: 50, target_level: "working", estimated_minutes: 45, prerequisites: [], added_as_prerequisite: false };
    setProposal((current) => current && ({ ...current, tracks: current.tracks.map((track, index) => index === trackIndex ? { ...track, topics: [...track.topics, topic] } : track) }));
  }

  async function persistDraft(): Promise<number | null> {
    if (!proposal) return null;
    setBusy(true); setError(null); setNotice(null);
    try {
      const saved = draftId ? await api.updateDraft(draftId, proposal, requirements) : await api.createDraft(proposal, requirements);
      setDraftId(saved.id);
      setNotice("Draft saved. Review it carefully before confirmation.");
      return saved.id;
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not save draft."); return null; }
    finally { setBusy(false); }
  }

  async function confirm() {
    const id = await persistDraft();
    if (!id) return;
    setBusy(true); setError(null);
    try { await api.confirmCurriculum(id); setConfirmed(true); setConfirmReady(false); setNotice("Curriculum confirmed and now structurally fixed."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not confirm curriculum."); }
    finally { setBusy(false); }
  }

  async function activate() {
    if (!draftId) return;
    setBusy(true); setError(null);
    try { await api.activateCurriculum(draftId); window.location.assign("/curriculum"); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not activate curriculum."); setBusy(false); }
  }

  return <div className="mx-auto max-w-5xl"><Link to="/curriculum" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-accent"><ArrowLeft size={16} /> Curriculum</Link><header className="mt-5"><p className="text-sm font-bold uppercase tracking-widest text-accent">Custom curriculum</p><h1 className="display mt-2 text-3xl font-extrabold">{initialDraftId ? "Review and edit draft" : "What do you want to learn?"}</h1><p className="mt-2 text-slate-500">Gemini proposes. You review and edit. Nothing becomes active until you explicitly confirm and activate it.</p></header>{!proposal && !initialDraftId && <section className="mt-7 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"><div className="grid gap-4 sm:grid-cols-2"><label className="text-sm font-semibold">Optional name<input value={preferredName} onChange={(event) => setPreferredName(event.target.value)} placeholder="Backend interview plan" className="mt-2 w-full rounded-xl bg-slate-100 px-4 py-3 font-normal outline-none" /></label><label className="text-sm font-semibold">Optional goal<input value={goal} onChange={(event) => setGoal(event.target.value)} placeholder="Prepare for a junior AI backend role" className="mt-2 w-full rounded-xl bg-slate-100 px-4 py-3 font-normal outline-none" /></label></div><label className="mt-5 block text-sm font-semibold">Requirements<textarea value={requirements} onChange={(event) => setRequirements(event.target.value)} rows={9} placeholder="Paste skills, a job description, technologies, interview requirements, or a syllabus…" className="mt-2 w-full resize-y rounded-2xl bg-slate-100 px-4 py-3 font-normal leading-6 outline-none" /></label><button onClick={() => void generate()} disabled={busy} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-3 font-semibold text-white hover:bg-violet-700 disabled:opacity-50">{busy ? <LoaderCircle className="animate-spin" size={18} /> : <Sparkles size={18} />} Generate curriculum</button></section>}{busy && initialDraftId && !proposal && <div className="mt-8 flex items-center gap-2 text-slate-500"><LoaderCircle className="animate-spin" size={18} /> Loading draft…</div>}{proposal && <><section className="mt-7 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"><div className="grid gap-4"><label className="text-xs font-bold uppercase tracking-wider text-slate-400">Curriculum name<input value={proposal.name} onChange={(event) => setProposal({ ...proposal, name: event.target.value })} disabled={confirmed} className="mt-2 w-full rounded-xl bg-slate-100 px-4 py-3 text-base font-semibold normal-case tracking-normal text-slate-900 outline-none disabled:opacity-60" /></label><label className="text-xs font-bold uppercase tracking-wider text-slate-400">Description<textarea value={proposal.description} onChange={(event) => setProposal({ ...proposal, description: event.target.value })} disabled={confirmed} rows={2} className="mt-2 w-full rounded-xl bg-slate-100 px-4 py-3 text-sm font-normal normal-case tracking-normal text-slate-900 outline-none disabled:opacity-60" /></label><label className="text-xs font-bold uppercase tracking-wider text-slate-400">Goal<textarea value={proposal.goal} onChange={(event) => setProposal({ ...proposal, goal: event.target.value })} disabled={confirmed} rows={2} className="mt-2 w-full rounded-xl bg-slate-100 px-4 py-3 text-sm font-normal normal-case tracking-normal text-slate-900 outline-none disabled:opacity-60" /></label></div></section><div className="mt-5 space-y-5">{proposal.tracks.map((track, trackIndex) => <section key={track.key} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7"><div className="grid gap-3 sm:grid-cols-[1fr_120px]"><input aria-label="Track name" value={track.name} onChange={(event) => updateTrack(trackIndex, { name: event.target.value })} disabled={confirmed} className="display rounded-xl bg-slate-100 px-4 py-3 text-lg font-bold outline-none disabled:opacity-60" /><input aria-label="Track priority" type="number" min={1} max={100} value={track.priority} onChange={(event) => updateTrack(trackIndex, { priority: Number(event.target.value) })} disabled={confirmed} className="rounded-xl bg-slate-100 px-4 py-3 outline-none disabled:opacity-60" /></div><textarea aria-label="Track description" value={track.description} onChange={(event) => updateTrack(trackIndex, { description: event.target.value })} disabled={confirmed} rows={2} className="mt-3 w-full rounded-xl bg-slate-100 px-4 py-3 text-sm outline-none disabled:opacity-60" /><div className="mt-5 space-y-3">{track.topics.map((topic, topicIndex) => <div key={topic.key} className="rounded-2xl border border-slate-200 p-4"><div className="flex flex-wrap items-center gap-2"><input aria-label="Topic name" value={topic.name} onChange={(event) => updateTopic(trackIndex, topicIndex, { name: event.target.value })} disabled={confirmed} className="min-w-52 flex-1 rounded-lg bg-slate-100 px-3 py-2 font-semibold outline-none disabled:opacity-60" />{topic.added_as_prerequisite && <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-800">prerequisite</span>}{!confirmed && <><button aria-label="Move topic up" onClick={() => moveTopic(trackIndex, topicIndex, -1)} className="rounded-lg p-2 text-slate-400 hover:bg-slate-100"><ArrowUp size={16} /></button><button aria-label="Move topic down" onClick={() => moveTopic(trackIndex, topicIndex, 1)} className="rounded-lg p-2 text-slate-400 hover:bg-slate-100"><ArrowDown size={16} /></button><button aria-label="Remove topic" onClick={() => removeTopic(trackIndex, topicIndex)} className="rounded-lg p-2 text-red-400 hover:bg-red-50"><Trash2 size={16} /></button></>}</div><textarea aria-label="Topic description" value={topic.description} onChange={(event) => updateTopic(trackIndex, topicIndex, { description: event.target.value })} disabled={confirmed} rows={2} className="mt-3 w-full rounded-lg bg-slate-50 px-3 py-2 text-sm outline-none disabled:opacity-60" /><div className="mt-3 grid gap-3 sm:grid-cols-3"><label className="text-xs text-slate-500">Priority<input type="number" min={1} max={100} value={topic.priority} onChange={(event) => updateTopic(trackIndex, topicIndex, { priority: Number(event.target.value) })} disabled={confirmed} className="mt-1 w-full rounded-lg bg-slate-100 px-3 py-2 text-sm outline-none" /></label><label className="text-xs text-slate-500">Minutes<input type="number" min={10} max={480} value={topic.estimated_minutes} onChange={(event) => updateTopic(trackIndex, topicIndex, { estimated_minutes: Number(event.target.value) })} disabled={confirmed} className="mt-1 w-full rounded-lg bg-slate-100 px-3 py-2 text-sm outline-none" /></label><label className="text-xs text-slate-500">Target level<input value={topic.target_level} onChange={(event) => updateTopic(trackIndex, topicIndex, { target_level: event.target.value })} disabled={confirmed} className="mt-1 w-full rounded-lg bg-slate-100 px-3 py-2 text-sm outline-none" /></label></div><label className="mt-3 block text-xs text-slate-500">Prerequisite keys, comma separated<input value={topic.prerequisites.join(", ")} onChange={(event) => updateTopic(trackIndex, topicIndex, { prerequisites: event.target.value.split(",").map((value) => value.trim()).filter(Boolean) })} disabled={confirmed} className="mt-1 w-full rounded-lg bg-slate-100 px-3 py-2 font-mono text-xs outline-none" /></label><p className="mt-2 text-[11px] text-slate-400">Key: {topic.key}</p></div>)}{!confirmed && <button onClick={() => addTopic(trackIndex)} className="inline-flex items-center gap-2 rounded-xl border border-dashed border-violet-300 px-4 py-2.5 text-sm font-semibold text-accent"><Plus size={16} /> Add topic</button>}</div></section>)}</div><section className="mt-6 rounded-3xl border border-slate-200 bg-white p-6"><div className="flex flex-wrap gap-3">{!confirmed && <button onClick={() => void persistDraft()} disabled={busy} className="rounded-xl border border-slate-300 px-5 py-3 font-semibold hover:bg-slate-50 disabled:opacity-50">Save draft</button>}{draftId && !confirmed && !confirmReady && <button onClick={() => setConfirmReady(true)} className="rounded-xl bg-ink px-5 py-3 font-semibold text-white">Review confirmation</button>}{confirmReady && !confirmed && <div className="w-full rounded-2xl bg-amber-50 p-4"><p className="font-semibold text-amber-950">Once confirmed, Forge will treat this curriculum as fixed. You can create another version later.</p><div className="mt-3 flex gap-3"><button onClick={() => void confirm()} disabled={busy} className="rounded-xl bg-amber-900 px-4 py-2.5 font-semibold text-white">Confirm curriculum</button><button onClick={() => setConfirmReady(false)} className="px-3 text-sm font-semibold text-amber-900">Keep editing</button></div></div>}{confirmed && <button onClick={() => void activate()} disabled={busy} className="rounded-xl bg-accent px-5 py-3 font-semibold text-white hover:bg-violet-700">Activate curriculum</button>}</div>{notice && <p role="status" className="mt-4 text-sm text-emerald-700">{notice}</p>}</section></>}{error && <div role="alert" className="mt-5 rounded-2xl bg-red-50 p-4 text-sm text-red-700">{error}</div>}</div>;
}
