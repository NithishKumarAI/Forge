import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Check, ChevronLeft, ExternalLink } from "lucide-react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Markdown } from "../components/Markdown";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import type { LessonProgress } from "../types/course";

export function LearnPage() {
  const topicId = Number(useParams().topicId);
  const [params, setParams] = useSearchParams();
  const value = params.get("lesson_id");
  const lessonId = value === null ? undefined : Number(value);
  if (lessonId !== undefined && (!Number.isInteger(lessonId) || lessonId < 1)) {
    return <ErrorState message="Invalid lesson selection" />;
  }
  // Remount on identity changes so a prior lesson's section can never be marked in the next one.
  return <LearnLesson key={`${topicId}:${lessonId ?? "primary"}`} topicId={topicId} lessonId={lessonId}
    onSelect={(id) => setParams({ lesson_id: String(id) })} />;
}

function LearnLesson({ topicId, lessonId, onSelect }: { topicId: number; lessonId?: number; onSelect: (id: number) => void }) {
  const course = useApi(() => api.courseTopic(topicId, lessonId), [topicId, lessonId]);
  const [slug, setSlug] = useState<string | null>(null);
  const [done, setDone] = useState<LessonProgress | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const navigate = useNavigate();
  useEffect(() => {
    if (course.data) {
      setSlug(new URLSearchParams(window.location.search).get("section") ?? course.data.progress.current_section_slug);
      setDone(course.data.progress);
    }
  }, [course.data]);
  const revisionId = course.data?.progress.content_revision_id;
  useEffect(() => {
    if (!slug || !course.data) return;
    localStorage.setItem(`forge-course-section-${topicId}-${revisionId ?? "primary"}`, slug);
    void api.viewCourseSection(topicId, slug, revisionId).catch(() => setActionError("Reading progress could not be saved."));
  }, [topicId, revisionId, slug, course.data]);
  const lesson = course.data?.lesson;
  const index = lesson?.sections.findIndex((section) => section.slug === slug) ?? -1;
  const section = lesson?.sections[index];
  if (course.loading || (course.data && slug === null)) return <LoadingState />;
  if (course.error || !lesson || !section || !done) return <ErrorState message={course.error ?? "Static lesson unavailable"} />;
  if (lessonId !== undefined && revisionId === undefined) return <ErrorState message="Restart Forge to load the selected lesson." />;
  const choices = course.data?.lessons ?? [];

  async function next(finish = false) {
    try {
      const saved = await api.completeCourseSection(topicId, section!.slug, revisionId);
      setDone(saved);
      setActionError(null);
      if (finish) navigate(`/topics/${topicId}/practice`);
      else if (lesson!.sections[index + 1]) setSlug(lesson!.sections[index + 1].slug);
    } catch {
      setActionError("Reading progress could not be saved. Please retry.");
    }
  }

  return <div className="mx-auto max-w-6xl">
    <Link to={`/topics/${topicId}`} className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500"><ArrowLeft size={16} /> Topic overview</Link>
    <header className="mt-5 flex flex-wrap items-end justify-between gap-3">
      <div><p className="text-sm font-semibold text-accent">{lesson.track_slug} · Learn Course</p><h1 className="display text-3xl font-extrabold">{lesson.title}</h1></div>
      <div className="text-right text-sm"><strong>{done.completed_sections} / {lesson.sections.length}</strong><p className="text-slate-500">Lesson progress · mastery unchanged</p></div>
    </header>
    {choices.length > 1 && <label className="mt-5 block text-sm font-semibold">Lessons in this topic
      <select aria-label="Lessons in this topic" value={revisionId} onChange={(event) => onSelect(Number(event.target.value))} className="ml-3 rounded-xl border bg-white p-2">
        {choices.map((choice) => <option key={choice.content_revision_id} value={choice.content_revision_id}>{choice.order_index + 1}. {choice.title}</option>)}
      </select>
    </label>}
    {actionError && <p role="alert" className="mt-3 text-sm text-red-700">{actionError}</p>}
    <div className="mt-6 grid gap-5 lg:grid-cols-[260px_1fr]">
      <aside className="h-fit rounded-2xl border bg-white p-3"><p className="px-2 pb-2 text-xs font-bold uppercase tracking-wider text-slate-400">Contents</p>
        {lesson.sections.map((item) => <button key={item.slug} onClick={() => setSlug(item.slug)} className={`flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm ${item.slug === slug ? "bg-accent-soft font-semibold text-accent" : "hover:bg-slate-50"}`}>
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-100 text-xs">{(done.completed_section_slugs?.includes(item.slug) ?? item.order_index < done.completed_sections) ? <Check size={12} /> : item.order_index + 1}</span>{item.title}
        </button>)}
      </aside>
      <main className="rounded-3xl border bg-white p-6 shadow-soft sm:p-9">
        <p className="text-xs font-bold uppercase tracking-widest text-accent">Section {index + 1}</p><h2 className="display mt-2 text-2xl font-bold">{section.title}</h2>
        <p className="mt-2 text-sm text-slate-500">{section.learning_objective} · {section.estimated_minutes} min</p>
        <div className="mt-6"><Markdown>{section.markdown}</Markdown></div>
        {section.examples.map((example, i) => <div key={i} className="mt-5">
          <pre className="overflow-x-auto rounded-xl bg-ink p-4 text-sm text-slate-100"><code>{example.code}</code></pre>
          {example.expected_output && <p className="mt-2 text-xs text-slate-500">Output: <code>{example.expected_output}</code></p>}
          <p className="mt-2 text-sm text-slate-600">{example.explanation}</p>
        </div>)}
        <div className="mt-6 rounded-2xl bg-slate-50 p-4"><strong>Key points</strong><ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">{section.key_points.map((point) => <li key={point}>{point}</li>)}</ul></div>
        <div className="mt-8 flex justify-between">
          <button disabled={index === 0} onClick={() => setSlug(lesson.sections[index - 1].slug)} className="flex items-center gap-2 rounded-xl border px-4 py-2 disabled:opacity-30"><ChevronLeft size={16} /> Previous</button>
          {index < lesson.sections.length - 1
            ? <button onClick={() => void next()} className="flex items-center gap-2 rounded-xl bg-accent px-4 py-2 font-semibold text-white">Next <ArrowRight size={16} /></button>
            : <button onClick={() => void next(true)} className="rounded-xl bg-emerald-700 px-4 py-2 font-semibold text-white">Lesson complete · Start Practice</button>}
        </div>
      </main>
    </div>
    <details className="mt-5 rounded-2xl border bg-white p-5"><summary className="cursor-pointer font-semibold">Sources / References</summary>
      <div className="mt-3 space-y-2">{lesson.sources.map((source) => <a key={`${source.source_id}:${source.url}`} href={source.url} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-sm text-accent">
        {source.title}<ExternalLink size={13} /><span className="text-slate-400">{new URL(source.url).hostname} · {new Date(source.retrieved_at).toLocaleDateString()}</span>
      </a>)}</div>
    </details>
  </div>;
}
