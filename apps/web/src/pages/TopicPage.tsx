import { ArrowLeft, BookOpen, CheckCircle2, Clock3, Dumbbell, FlaskConical, Sparkles } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { ProgressBar } from "../components/ProgressBar";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

export function TopicPage() {
  const id = Number(useParams().topicId);
  const topic = useApi(() => api.topic(id), [id]);
  const history = useApi(() => api.practiceHistory(id), [id]);
  const mastery = useApi(() => api.mastery(id), [id]);
  if (topic.loading) return <LoadingState />;
  if (topic.error || !topic.data) return <ErrorState message={topic.error ?? "Topic unavailable"} />;
  const current = topic.data;
  const incomplete = current.prerequisites.filter((item) => item.mastery_score < 60);

  return <div className="mx-auto max-w-4xl">
    <Link to="/curriculum" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-accent"><ArrowLeft size={16} /> Back to curriculum</Link>
    <section className="mt-6 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-soft">
      <div className="border-b border-slate-100 p-7 sm:p-10">
        <p className="text-sm font-semibold text-accent">{current.track_name}</p>
        <h1 className="display mt-2 text-3xl font-extrabold sm:text-4xl">{current.name}</h1>
        <p className="mt-4 max-w-2xl leading-7 text-slate-600">{current.description}</p>
        <div className="mt-6 flex flex-wrap gap-3 text-sm"><span className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1.5"><Clock3 size={15} /> {current.estimated_minutes} min</span><span className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1.5"><CheckCircle2 size={15} /> Target: {current.target_level.replace("_", " ")}</span></div>
        {incomplete.length > 0 && <div className="mt-5 rounded-xl bg-amber-50 p-3 text-sm text-amber-900">Recommended first: {incomplete.map((item) => item.name).join(", ")}. You can still start this topic now.</div>}
      </div>
      <div className="grid gap-8 p-7 sm:p-10 lg:grid-cols-[1fr_.8fr]">
        <div>
          <h2 className="display font-bold">Current mastery</h2>
          <div className="mt-3 flex items-center gap-4"><div className="flex-1"><ProgressBar value={current.state.mastery_score} /></div><strong>{current.state.mastery_score}%</strong></div>
          <p className="mt-3 text-sm capitalize text-slate-500">Status: {current.state.status.replace("_", " ")} · Confidence: {current.state.confidence}</p>
          <h2 className="display mt-7 font-bold">Prerequisites</h2>
          {current.prerequisites.length ? <div className="mt-3 flex flex-wrap gap-2">{current.prerequisites.map((item) => <span key={item.id} className="rounded-lg bg-accent-soft px-3 py-2 text-sm font-medium text-accent">{item.name} · {item.mastery_score}%</span>)}</div> : <p className="mt-2 text-sm text-slate-500">No prerequisites — a good place to begin.</p>}
        </div>
        <div className="rounded-2xl bg-slate-50 p-5">
          <h2 className="display font-bold">Choose how to study</h2><p className="mt-1 text-sm text-slate-500">You stay in control of your learning path.</p>
          <div className="mt-4 space-y-2">
            <Link to={`/topics/${current.id}/learn`} className="flex w-full items-center gap-3 rounded-xl bg-accent p-3.5 text-left font-semibold text-white hover:bg-violet-700"><BookOpen size={18} /> Learn Course<span className="ml-auto text-xs font-normal text-violet-200">Static lesson</span></Link>
            <Link to={`/topics/${current.id}/tutor`} className="flex w-full items-center gap-3 rounded-xl border border-violet-200 bg-white p-3.5 text-left font-semibold text-accent hover:bg-accent-soft"><Sparkles size={18} /> AI Tutor<span className="ml-auto text-xs font-normal">Grounded professor</span></Link>
            <Link to={`/topics/${current.id}/practice`} className="flex w-full items-center gap-3 rounded-xl border border-violet-200 bg-white p-3.5 text-left font-semibold text-accent hover:bg-accent-soft"><Dumbbell size={18} /> Guided Practice<span className="ml-auto text-xs font-normal">Lesson exercises</span></Link>
            {mastery.data?.transfer_eligible ? <Link to={`/topics/${current.id}/transfer`} className="flex w-full items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-3.5 text-left font-semibold text-emerald-800"><FlaskConical size={18} /> Transfer Check<span className="ml-auto text-xs font-normal">Unseen task</span></Link> : <button disabled className="flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-white p-3.5 text-left font-semibold text-slate-400"><FlaskConical size={18} /> Transfer Check<span className="ml-auto text-xs font-normal">More mixed evidence needed</span></button>}
          </div>
        </div>
      </div>
    </section>
    {mastery.data && <section className="mt-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"><h2 className="display text-lg font-bold">Why this score?</h2><div className="mt-4 grid gap-3 sm:grid-cols-4"><div className="rounded-xl bg-slate-50 p-3"><p className="text-xs text-slate-400">Practice evidence</p><strong>{mastery.data.practice_score === null ? "None" : `${mastery.data.practice_score}%`}</strong></div><div className="rounded-xl bg-slate-50 p-3"><p className="text-xs text-slate-400">Transfer</p><strong>{mastery.data.transfer ? `${mastery.data.transfer.score}%` : mastery.data.transfer_eligible ? "Ready" : "Not yet"}</strong></div><div className="rounded-xl bg-slate-50 p-3"><p className="text-xs text-slate-400">Delayed recall</p><strong>{mastery.data.delayed_recall ? `${mastery.data.delayed_recall.score}%` : "Not yet"}</strong></div><div className="rounded-xl bg-slate-50 p-3"><p className="text-xs text-slate-400">Current maximum</p><strong>{mastery.data.current_cap}%</strong></div></div><p className="mt-4 text-sm text-slate-600">{mastery.data.cap_reason}</p>{mastery.data.next_review_at && <p className="mt-2 text-sm text-slate-500">Next review: {new Date(mastery.data.next_review_at).toLocaleString()}</p>}{mastery.data.mistakes.length > 0 && <div className="mt-5"><h3 className="font-semibold">Recurring mistakes</h3><ul className="mt-2 space-y-1 text-sm text-slate-600">{mastery.data.mistakes.slice(0, 4).map((mistake) => <li key={`${mistake.category}-${mistake.description}`}>{mistake.description} ×{mistake.occurrence_count}</li>)}</ul></div>}</section>}
    <section className="mt-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="display text-lg font-bold">Attempt history</h2>
      {history.loading ? <p className="mt-3 text-sm text-slate-400">Loading history…</p> : history.error ? <p className="mt-3 text-sm text-amber-700">History unavailable: {history.error}</p> : history.data && history.data.attempt_count > 0 ? <>
        <p className="mt-2 text-sm text-slate-500">{history.data.attempt_count} attempts · Recent average: {history.data.recent_average === null ? "pending" : `${history.data.recent_average}%`} · Last practiced: {history.data.last_practiced_at ? new Date(history.data.last_practiced_at).toLocaleDateString() : "—"}</p>
        <div className="mt-4 space-y-2">{history.data.attempts.slice(0, 5).map((attempt) => <div key={attempt.attempt_id} className="flex flex-wrap justify-between gap-2 rounded-xl bg-slate-50 p-3 text-sm"><span>{attempt.exercise_title} <span className="text-slate-400">· {attempt.exercise_type.replaceAll("_", " ")}</span></span><span className="font-semibold">{attempt.score === null ? "Pending" : `${attempt.score}%`} · {attempt.hints_used_count} hints</span></div>)}</div>
      </> : <p className="mt-2 text-sm text-slate-500">No scored attempts yet. Learn or start directly with Practice.</p>}
    </section>
  </div>;
}
