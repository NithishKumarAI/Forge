import {StudyPlanPanel} from "../components/StudyPlanPanel";
import { ArrowRight, CalendarClock, Clock3, Flame, Play, SkipForward } from "lucide-react";
import { Link } from "react-router-dom";
import { ProgressBar } from "../components/ProgressBar";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

const shortNames: Record<string, string> = {
  "Backend Engineering": "Backend", "SQL + Computer Science": "SQL + CS", "Machine Learning Fundamentals": "ML", "Frontend Basics": "Frontend", "Interview Engineering": "Interview"
};

export function DashboardPage() {
  const { data, error, loading } = useApi(api.dashboard, []);
  if (loading) return <LoadingState />;
  if (error || !data) return <ErrorState message={error ?? "No dashboard data returned"} />;
  const first = data.recommendations[0];

  return (
    <div className="mx-auto max-w-6xl">
      <header className="mb-9 flex flex-wrap items-end justify-between gap-4">
        <div><p className="mb-2 text-sm font-semibold uppercase tracking-[.18em] text-accent">Your learning command center</p><h1 className="display text-3xl font-extrabold tracking-tight sm:text-4xl">Welcome back to Forge.</h1><p className="mt-2 text-slate-500">Build evidence. Close gaps. Get interview-ready.</p>{data.active_curriculum && <p className="mt-3 inline-flex rounded-full bg-accent-soft px-3 py-1 text-xs font-semibold text-accent">Active: {data.active_curriculum.name} · v{data.active_curriculum.version}</p>}</div>
        <div className="rounded-2xl bg-white px-5 py-3 shadow-sm"><span className="text-sm text-slate-500">Curriculum readiness</span><span className="ml-3 text-2xl font-bold">{data.interview_readiness}%</span><p className="mt-1 text-xs text-slate-400">Not a hiring probability</p></div>
      </header>

      <section className="grid gap-5 lg:grid-cols-[1.25fr_.75fr]">
        <div className="rounded-3xl bg-ink p-6 text-white shadow-soft sm:p-8">
          <div className="flex items-center gap-2 text-sm font-semibold text-violet-300"><Flame size={18} /> RECOMMENDED TODAY</div>
          {first ? <><h2 className="display mt-7 text-3xl font-bold">{first.name}</h2><p className="mt-2 text-slate-400">{first.track_name} · {first.reason}</p><div className="mt-7 flex flex-wrap gap-4 text-sm text-slate-300"><span className="flex items-center gap-2"><Clock3 size={16} /> {first.estimated_minutes} min</span><span>Target: {first.target_level.replace("_", " ")}</span></div><Link to={`/topics/${first.id}`} className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-ink transition hover:bg-violet-100"><Play size={17} fill="currentColor" /> Start recommended session</Link></> : <p className="mt-7 text-slate-300">All current topics are interview-ready.</p>}
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="display text-lg font-bold">Up next</h2>
          <div className="mt-4 space-y-2">
            {data.recommendations.slice(1).map((topic, index) => <Link key={topic.id} to={`/topics/${topic.id}`} className="group flex items-center gap-3 rounded-2xl p-3 hover:bg-slate-50"><span className="flex h-8 w-8 items-center justify-center rounded-xl bg-accent-soft text-sm font-bold text-accent">{index + 2}</span><span className="min-w-0 flex-1"><span className="block truncate font-semibold">{topic.name}</span><span className="text-xs text-slate-500">{topic.reason}</span></span><ArrowRight size={17} className="text-slate-300 group-hover:text-accent" /></Link>)}
          </div>
          <p className="mt-4 border-t border-slate-100 pt-4 text-xs leading-5 text-slate-500">Recommendations guide you, but never lock you in. Pick any subject below.</p>
        </div>
      </section>

      {data.content_status&&<section className="mt-6 rounded-2xl border bg-white p-5"><h2 className="display text-lg font-bold">Learning availability and progress</h2><p className="mt-2 text-sm">{data.content_status.approved_lessons} approved lessons · {data.content_status.legacy_lessons} legacy lessons · {data.content_status.missing_topics} topics without a lesson</p><p className="mt-2 text-sm text-slate-500">{data.readiness.strong_or_ready_topics} / {data.readiness.total_topics} strong or ready topics. {data.reading_progress?.completed_revision_sections??0} saved revision-section completions; reading does not award mastery.</p>{data.content_status.missing_topics>0&&<p className="mt-3 text-sm text-amber-800">Some teaching and assessment pools are missing or unpublished. Legacy availability is separate from approved Placement Foundations coverage.</p>}</section>}
      <StudyPlanPanel initial={data.today_plan}/>
      {Boolean(data.recent_mistakes?.length)&&<section className="mt-6 rounded-2xl border bg-white p-5"><h2 className="display text-lg font-bold">Recent recorded mistakes</h2><ul className="mt-3 space-y-2">{data.recent_mistakes?.map((item,index)=><li key={index}><Link className="font-semibold text-accent" to={`/topics/${item.topic_id}`}>{item.topic_name}</Link><p className="text-sm text-slate-500">{item.description} · {item.occurrence_count} recorded occurrences</p></li>)}</ul></section>}

      <section className="mt-6 grid gap-4 sm:grid-cols-3"><Link className="rounded-2xl border bg-white p-5" to="/review"><h2 className="font-bold">Due revisions</h2><p className="mt-2">{data.reviews_due} topics · FSRS queue</p></Link><Link className="rounded-2xl border bg-white p-5" to="/tests"><h2 className="font-bold">Timed mock tests</h2><p className="mt-2 text-sm">Subject, level, mixed and coding tests from approved pools.</p></Link><Link className="rounded-2xl border bg-white p-5" to="/interview"><h2 className="font-bold">Interview rehearsal</h2><p className="mt-2 text-sm">Objective technical work and unscored communication practice.</p></Link></section>


      <section className="mt-10"><div className="mb-4 flex items-center justify-between"><h2 className="display text-xl font-bold">Subjects</h2><Link to="/curriculum" className="text-sm font-semibold text-accent hover:text-violet-800">View full curriculum →</Link></div><div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{data.tracks.map((track) => <Link key={track.id} to={`/curriculum?track=${track.id}`} className="group rounded-2xl border border-slate-200 bg-white p-5 transition hover:-translate-y-0.5 hover:border-violet-300 hover:shadow-md"><div className="flex items-center justify-between"><h3 className="font-semibold">{shortNames[track.name] ?? track.name}</h3><span className="text-sm font-bold text-slate-500">{track.mastery}%</span></div><div className="mt-4"><ProgressBar value={track.mastery} /></div><p className="mt-3 text-xs text-slate-400">{track.topic_count} topics</p></Link>)}</div></section>
    </div>
  );
}
