import { Calculator, Puzzle, Languages, Code2, Database, Network, Layers3, Sparkles, MessagesSquare, Clock3, BookOpen } from "lucide-react";
import { Link } from "react-router-dom";
import type { EditionOverview, EditionTopic } from "../types/editions";

const icons = {calculator:Calculator, puzzle:Puzzle, languages:Languages, code:Code2, database:Database,
  network:Network, layers:Layers3, sparkles:Sparkles, messages:MessagesSquare};

export function filterTopics(topics: EditionTopic[], level: number) { return topics.filter(topic => topic.level === level); }
export function lessonLabel(topic: EditionTopic) {
  return topic.availability.lesson_status === "approved" ? "Approved lesson available" :
    topic.availability.lesson_status === "legacy" ? "Legacy lesson · not fully verified" : "Planned · content not published";
}

export function SubjectLevelNavigation({overview, subjectKey, level, onSubjectChange, onLevelChange}: {
  overview: EditionOverview; subjectKey: string; level: number;
  onSubjectChange: (key: string) => void; onLevelChange: (level: number) => void;
}) {
  const subject = overview.subjects.find(s => s.key === subjectKey) ?? overview.subjects[0];
  if (!subject) return <p>No subject scope is available yet.</p>;
  const names = new Map(overview.subjects.flatMap(s => s.topics.map(t => [t.key, t.title] as const)));
  const learning = overview.binding?.status === "confirmed";
  const topics = filterTopics(subject.topics, level);
  return <div>
    <nav aria-label="Placement subjects" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {overview.subjects.map(item => {
        const Icon = icons[item.icon as keyof typeof icons] ?? BookOpen;
        return <button type="button" key={item.key} aria-pressed={subject.key === item.key} onClick={() => onSubjectChange(item.key)}
          className={`rounded-2xl border p-4 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-600 ${subject.key === item.key ? "border-violet-400 bg-violet-50 shadow-sm" : "border-slate-200 bg-white hover:border-violet-300"}`}>
          <Icon size={21} className="mb-3 text-accent" aria-hidden="true"/><span className="block text-sm font-bold text-slate-900">{item.name}</span>
          <span className="mt-1 block text-xs leading-5 text-slate-500">{item.description}</span>
          <span className="mt-2 block text-xs font-semibold text-slate-500">{item.topics.length} topics · Levels 1–3</span>
        </button>;
      })}
    </nav>
    <section aria-label={`${subject.name} topics`} className="mt-6 rounded-3xl border border-slate-200 bg-white p-5 sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-4"><div><h2 className="display text-xl font-bold">{subject.name}</h2>
        <p className="mt-1 text-sm text-slate-500">Levels describe content difficulty. Choose any available topic.</p></div>
        <nav aria-label="Learning level" className="flex rounded-xl bg-slate-100 p-1">{[1,2,3].map(n => <button type="button" key={n} aria-pressed={level === n}
          onClick={() => onLevelChange(n)} className={`rounded-lg px-4 py-2 text-sm font-semibold ${level === n ? "bg-white text-accent shadow-sm" : "text-slate-500"}`}>Level {n}</button>)}</nav>
      </div>
      <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">{topics.length} topics · {topics.reduce((sum,t) => sum+t.estimated_minutes,0)} estimated minutes</p>
      <div className="mt-3 space-y-3">{topics.map(topic => <article key={topic.key} className="rounded-2xl border border-slate-200 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3"><div><h3 className="font-bold">{topic.title}</h3><p className="mt-1 max-w-2xl text-sm leading-6 text-slate-600">{topic.description}</p></div>
          <span className="flex items-center gap-1 text-xs text-slate-500"><Clock3 size={13}/>{topic.estimated_minutes} min</span></div>
        <div className="mt-3 flex flex-wrap gap-2 text-xs"><span className={`rounded-full px-3 py-1 ${topic.availability.lesson_status === "approved" ? "bg-emerald-50 text-emerald-800" : topic.availability.lesson_status === "legacy" ? "bg-amber-50 text-amber-900" : "bg-slate-100 text-slate-600"}`}>{lessonLabel(topic)}</span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">{topic.availability.approved_practice_available ? "Approved practice available" : "No approved practice available"}</span>
          {topic.availability.practice_available && !topic.availability.approved_practice_available && <span className="rounded-full bg-amber-50 px-3 py-1 text-amber-900">Legacy practice available</span>}</div>
        {topic.prerequisites.length > 0 && <p className="mt-3 text-xs text-slate-500">Helpful first: {topic.prerequisites.map(k => names.get(k) ?? k).join(", ")}. These are recommendations, not access locks.</p>}
        {topic.availability.total_sections > 0 && <div className="mt-3"><label className="text-xs text-slate-500">Reading progress · {topic.availability.completed_sections}/{topic.availability.total_sections} sections
          <progress aria-label={`${topic.title} reading progress`} value={topic.availability.reading_percent} max={100} className="mt-1 block h-2 w-full accent-violet-600"/></label></div>}
        <details className="mt-3 text-sm"><summary className="cursor-pointer font-semibold text-accent">Learning outcomes and coverage</summary>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-slate-600">{topic.learning_outcomes.map(item => <li key={item}>{item}</li>)}</ul>
          <p className="mt-2 text-xs text-slate-500">Coverage to review: {topic.coverage_requirements.join(" ")}</p></details>
        {learning && topic.id !== null ? <div className="mt-4 flex flex-wrap gap-3 text-sm font-semibold"><Link className="text-accent hover:underline" to={`/topics/${topic.id}`}>Open topic →</Link>
          {topic.availability.lesson_count > 0 && <Link className="text-accent hover:underline" to={`/topics/${topic.id}/learn`}>Read lesson</Link>}
          {(topic.availability.course_exercise_count > 0 || (topic.availability.assessment_item_count ?? 0) > 0) && <Link className="text-accent hover:underline" to={`/topics/${topic.id}/practice`}>Practice</Link>}
          {topic.availability.arena_count > 0 && <Link className="text-accent hover:underline" to="/arena">Open Arena</Link>}</div>
          : <p className="mt-3 text-xs text-slate-500">Scope preview. Review and confirm the draft before opening its learning topics.</p>}
      </article>)}</div>
    </section>
  </div>;
}
