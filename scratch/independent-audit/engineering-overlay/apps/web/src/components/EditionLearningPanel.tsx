import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../services/api";
import type { EditionOverview } from "../types/editions";
import { SubjectLevelNavigation } from "./SubjectLevelNavigation";

export function EditionLearningPanel() {
  const [params, setParams] = useSearchParams();
  const [overview, setOverview] = useState<EditionOverview | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [reviewer, setReviewer] = useState("");
  const [scopeChecked, setScopeChecked] = useState(false);
  const [missingChecked, setMissingChecked] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [view, setView] = useState("placement-foundations");
  const curriculumId = Number(params.get("review")) || undefined;
  useEffect(() => { let live = true;
    api.edition("placement-foundations", curriculumId).then(data => {if (live) setOverview(data);})
      .catch(reason => {if (live) setError(String(reason));});
    api.editions().then(data => {if (live && data.selected_edition_key) setView(data.selected_edition_key);}).catch(() => {});
    return () => {live = false;};
  }, [curriculumId]);
  function changeQuery(key: string, value: string) { const next = new URLSearchParams(params); next.set(key,value); setParams(next); }
  async function action(run: () => Promise<EditionOverview>, message: string) {
    setBusy(true); setError(null); setNotice(null);
    try { setOverview(await run()); setNotice(message); setScopeChecked(false); setMissingChecked(false); return true; }
    catch (reason) { setError(reason instanceof Error ? reason.message : "This action could not be completed."); return false; }
    finally { setBusy(false); }
  }
  if (!overview) return <section className="mb-8 rounded-3xl border bg-white p-6"><p role={error ? "alert" : "status"}>{error ?? "Loading Placement Foundations…"}</p></section>;
  const binding = overview.binding;
  const topics = overview.subjects.flatMap(s => s.topics);
  const missing = topics.filter(t => t.availability.lesson_count === 0).length;
  const subject = params.get("subject") ?? "python";
  const levelParam = Number(params.get("level"));
  const level = [1,2,3].includes(levelParam) ? levelParam : 1;
  return <section className="mb-10" aria-label="Product editions">
    <div className="mb-4 flex flex-wrap gap-2"><button type="button" aria-pressed={view === "placement-foundations"}
      onClick={() => {setView("placement-foundations");void api.selectEdition("placement-foundations").catch(reason => setError(String(reason)));}}
      className="rounded-xl border bg-white px-4 py-2 text-sm font-semibold text-accent">Forge V1 · Placement Foundations</button>
      <button type="button" aria-expanded={view === "advanced-engineering"} onClick={() => setView(view === "advanced-engineering" ? "placement-foundations" : "advanced-engineering")}
        className="rounded-xl border bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-500">Forge V2 · Future edition</button></div>
    {view === "advanced-engineering" ? <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-8"><h2 className="display text-xl font-bold">Advanced Engineering is planned</h2>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">Future Levels 4 and 5 will extend these foundations in the same app. No compatible approved curriculum is available yet. Your current curriculum remains selected.</p></div>
      : <><header className="mb-5 rounded-3xl bg-ink p-6 text-white sm:p-8"><span className="rounded-full bg-white/10 px-3 py-1 text-xs font-bold tracking-wider">FORGE V1</span>
        <h2 className="display mt-4 text-3xl font-extrabold">Placement Foundations</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">Build a clear path across programming, problem solving and placement fundamentals. Explore all nine subjects and choose where to begin.</p>
        <div className="mt-5 flex flex-wrap gap-2 text-xs"><span className="rounded-full bg-white/10 px-3 py-1.5">9 subjects</span><span className="rounded-full bg-white/10 px-3 py-1.5">Levels 1–3</span><span className="rounded-full bg-white/10 px-3 py-1.5">{topics.length} outlined topics</span><span className="rounded-full bg-white/10 px-3 py-1.5">{binding?.is_active ? "Active curriculum" : binding?.status === "confirmed" ? "Confirmed · not active" : "Scope preview"}</span></div></header>
        <div className="mb-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-950">
          {binding?.is_active ? "This is your selected curriculum. Topic access stays open, and reading does not change mastery." : "This outline is a preview. Creating or confirming its draft does not change your active curriculum."}
          <p>{missing} of {topics.length} topics have no published lesson. An outline is not a complete course or a claim of interview readiness.</p></div>
        <div className="mb-6 rounded-2xl border bg-white p-5"><div className="flex flex-wrap gap-3">
          {!binding && <button disabled={busy} onClick={() => void action(api.createPlacementDraft, "Draft created. Review it before confirmation; your active curriculum is unchanged.")}
            className="rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50">Create reviewable draft</button>}
          {binding?.status === "draft" && <><Link to={`/curriculum/drafts/${binding.curriculum_id}`} className="rounded-xl border px-4 py-2.5 text-sm font-semibold text-accent">Edit draft</Link>
            <button aria-expanded={reviewOpen} onClick={() => setReviewOpen(!reviewOpen)} className="rounded-xl bg-ink px-4 py-2.5 text-sm font-semibold text-white">{reviewOpen ? "Close review summary" : "Review curriculum"}</button></>}
          {binding?.status === "confirmed" && !binding.is_active && <button disabled={busy} onClick={() => void action(() => api.activateEdition(binding.curriculum_id), "Curriculum activated. Reloading your curriculum…").then(success => { if (success) window.location.reload(); })}
            className="rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50">Activate this curriculum</button>}
          {binding?.is_active && <span className="text-sm font-semibold text-emerald-700">Your active Placement Foundations curriculum</span>}
        </div>
        {reviewOpen && binding?.status === "draft" && <div className="mt-5 border-t pt-5"><h3 className="font-bold">Review before confirmation</h3>
          <p className="mt-2 text-sm text-slate-600">Confirming fixes this curriculum's structure. It does not approve lesson content or activate the curriculum. Review the outcomes and prerequisites above, then acknowledge the missing teaching below.</p>
          <ul className="mt-3 grid gap-2 text-xs text-slate-600 sm:grid-cols-2">{overview.subjects.map(s => <li key={s.key}>{s.name}: {[1,2,3].map(n => `L${n}: ${s.topics.filter(t => t.level===n).length}`).join(" · ")}</li>)}</ul>
          <p className="mt-3 text-sm font-semibold">Missing lessons: {missing}. Approved lessons: {topics.filter(t => t.availability.approved_lesson_count > 0).length}. Prerequisites are validated and remain advisory.</p>
          <label className="mt-4 block text-sm font-semibold">Your name<input value={reviewer} onChange={event => setReviewer(event.target.value)} className="mt-1 block w-full rounded-xl border px-3 py-2" autoComplete="name"/></label>
          <label className="mt-3 flex gap-2 text-sm"><input type="checkbox" checked={scopeChecked} onChange={e => setScopeChecked(e.target.checked)}/>I reviewed all nine subjects, level coverage, outcomes and prerequisite links.</label>
          <label className="mt-3 flex gap-2 text-sm"><input type="checkbox" checked={missingChecked} onChange={e => setMissingChecked(e.target.checked)}/>I understand which content is missing and that confirmation does not publish or approve teaching.</label>
          <button disabled={busy || !scopeChecked || !missingChecked || reviewer.trim().length < 3} onClick={() => void action(() => api.confirmEdition(binding.curriculum_id, {
            graph_sha256:binding.graph_sha256,scope_sha256:overview.scope_sha256!,reviewer:reviewer.trim(),scope_reviewed:scopeChecked,missing_content_acknowledged:missingChecked}), "Curriculum confirmed. Activate it separately when you choose.")}
            className="mt-4 rounded-xl bg-amber-900 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-40">Confirm reviewed curriculum</button>
        </div>}</div>
        <SubjectLevelNavigation overview={overview} subjectKey={subject} level={level} onSubjectChange={key => changeQuery("subject",key)} onLevelChange={n => changeQuery("level",String(n))}/>
      </>}
    {notice && <p role="status" className="mt-4 text-sm font-semibold text-emerald-700">{notice}</p>}{error && <p role="alert" className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
  </section>;
}
