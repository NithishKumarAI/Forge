import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  Calculator,
  CheckCircle2,
  Clock3,
  Code2,
  Database,
  Flame,
  Languages,
  Layers,
  MessageSquare,
  Network,
  Play,
  Puzzle,
  RotateCcw,
  Sparkles,
} from "lucide-react";

import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import type {
  LearningPathDashboardData,
  LearningRecommendation,
  LearningStage,
  SubjectProgressSummary,
} from "../types/learningPath";

const iconMap: Record<string, React.ReactNode> = {
  code: <Code2 size={20} className="text-accent" />,
  database: <Database size={20} className="text-accent" />,
  network: <Network size={20} className="text-accent" />,
  calculator: <Calculator size={20} className="text-accent" />,
  puzzle: <Puzzle size={20} className="text-accent" />,
  languages: <Languages size={20} className="text-accent" />,
  layers: <Layers size={20} className="text-accent" />,
  sparkles: <Sparkles size={20} className="text-accent" />,
  messages: <MessageSquare size={20} className="text-accent" />,
};

function StageBadge({ stage }: { stage: LearningStage }) {
  switch (stage) {
    case "not_started":
      return (
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          Not started
        </span>
      );
    case "learning":
      return (
        <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
          Learning
        </span>
      );
    case "practising":
      return (
        <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
          Practising
        </span>
      );
    case "ready_to_advance":
      return (
        <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
          Ready to advance
        </span>
      );
    case "retained":
      return (
        <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-purple-700">
          Retained
        </span>
      );
    case "review_due":
      return (
        <span className="rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700">
          Review due
        </span>
      );
    default:
      return null;
  }
}

export function DashboardPage({ initialData }: { initialData?: LearningPathDashboardData } = {}) {
  const [activeSubject, setActiveSubject] = useState("python");
  const { data: fetchedData, error, loading } = useApi(
    () => api.learningPathDashboard(activeSubject),
    [activeSubject]
  );
  const data: LearningPathDashboardData | null = initialData ?? fetchedData;

  if (!initialData && loading) return <LoadingState />;
  if (!data) {
    return <ErrorState message={error ?? "Unable to load learning recommendations"} />;
  }

  const primary = data.primary_recommendation;
  const secondaries = data.secondary_recommendations.slice(0, 3);

  return (
    <div className="mx-auto max-w-6xl space-y-10">
      {/* Header */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <p className="text-xs font-bold uppercase tracking-[.2em] text-accent">
            Concept-by-concept learning
          </p>
          <h1 className="display mt-1 text-3xl font-extrabold tracking-tight sm:text-4xl text-slate-900">
            Welcome back to Forge.
          </h1>
          <p className="mt-2 text-slate-500">
            Master one small concept, trace a guided example, and solve beginner exercises.
          </p>
          {data.active_curriculum && (
            <p className="mt-3 inline-flex rounded-full bg-accent-soft px-3 py-1 text-xs font-semibold text-accent">
              Curriculum: {data.active_curriculum.name} · v{data.active_curriculum.version}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Link
            to="/arena"
            className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
          >
            Coding Arena
          </Link>
          <Link
            to="/curriculum"
            className="rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
          >
            Browse All Topics
          </Link>
        </div>
      </header>

      {/* Subject quick switcher */}
      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">
            Focus Subject
          </h2>
          <span className="text-xs text-slate-400">Switch any time · Never locked in</span>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {data.subjects.map((s) => (
            <button
              key={s.subject_key}
              onClick={() => setActiveSubject(s.subject_key)}
              className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
                activeSubject === s.subject_key
                  ? "bg-accent text-white shadow-sm"
                  : "border border-slate-200 bg-white text-slate-700 hover:border-violet-300"
              }`}
            >
              {s.subject_name}
            </button>
          ))}
        </div>
      </section>

      {/* Main Learning Hub: CONTINUE LEARNING (Primary) + Secondary Recommendations */}
      <section className="grid gap-6 lg:grid-cols-[1.3fr_.7fr]">
        {/* Primary Continue Learning card */}
        <div className="flex flex-col justify-between rounded-3xl bg-slate-950 p-7 text-white shadow-soft sm:p-9">
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span className="inline-flex items-center gap-2 rounded-full bg-violet-900/60 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-violet-300">
                <Flame size={15} /> Continue Learning
              </span>
              {primary && <StageBadge stage={primary.progress_state} />}
            </div>

            {primary ? (
              <div className="mt-6">
                <p className="text-sm font-semibold text-violet-300 uppercase tracking-wide">
                  {primary.subject_name} · {primary.stage.replace("_", " ").toUpperCase()}
                </p>
                <h2 className="display mt-2 text-2xl font-extrabold sm:text-3xl text-white">
                  {primary.concept_title}
                </h2>
                <p className="mt-3 text-slate-300 leading-relaxed">
                  {primary.objective}
                </p>

                <div className="mt-6 rounded-2xl bg-white/5 p-4 border border-white/10 text-sm text-slate-300 space-y-1">
                  <p className="font-semibold text-white">Why this step:</p>
                  <p className="text-xs text-slate-400">{primary.reason}</p>
                  <p className="text-xs text-violet-300 pt-1 font-mono">
                    Status: {primary.progress_summary}
                  </p>
                </div>
              </div>
            ) : (
              <div className="mt-8">
                <h2 className="display text-2xl font-bold">You are up to date!</h2>
                <p className="mt-2 text-slate-400">
                  All available concepts for this subject have been completed. Choose another subject below or practise in the Coding Arena.
                </p>
              </div>
            )}
          </div>

          <div className="mt-8 pt-4">
            {primary ? (
              <Link
                to={primary.action_path}
                className="inline-flex items-center gap-3 rounded-2xl bg-white px-7 py-4 text-base font-bold text-slate-950 transition hover:bg-violet-100 hover:scale-[1.01]"
              >
                <Play size={18} fill="currentColor" /> {primary.action_label}
              </Link>
            ) : (
              <Link
                to="/arena"
                className="inline-flex items-center gap-2 rounded-2xl bg-white px-6 py-3 font-semibold text-slate-950 transition hover:bg-slate-100"
              >
                Go to Coding Arena <ArrowRight size={17} />
              </Link>
            )}
          </div>
        </div>

        {/* Secondary Recommendations (Max 3) */}
        <div className="flex flex-col justify-between rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="display text-lg font-bold text-slate-900">Next Recommended Actions</h3>
              <span className="text-xs font-semibold text-slate-400">Max 3</span>
            </div>

            <div className="mt-4 space-y-3">
              {secondaries.length > 0 ? (
                secondaries.map((rec, index) => (
                  <Link
                    key={rec.concept_key}
                    to={rec.action_path}
                    className="group block rounded-2xl border border-slate-100 p-4 transition hover:border-violet-300 hover:bg-slate-50/80"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-accent">
                        {rec.kind === "secondary_subject"
                          ? "Switch Track"
                          : rec.kind === "review"
                          ? "Review Due"
                          : rec.kind === "prerequisite"
                          ? "Prerequisite"
                          : rec.kind === "practice"
                          ? "Independent Practice"
                          : "Alternative Concept"}
                      </span>
                      <StageBadge stage={rec.progress_state} />
                    </div>
                    <p className="mt-1.5 font-bold text-slate-900 group-hover:text-accent">
                      {rec.concept_title}
                    </p>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {rec.subject_name} · {rec.reason}
                    </p>
                  </Link>
                ))
              ) : (
                <div className="rounded-2xl bg-slate-50 p-5 text-center text-sm text-slate-500">
                  <CheckCircle2 size={24} className="mx-auto mb-2 text-emerald-600" />
                  No urgent revisions or pending prerequisites. Focus on your primary concept above!
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 border-t border-slate-100 pt-4 text-xs text-slate-400">
            Recommendations update automatically as you complete concepts and exercises.
          </div>
        </div>
      </section>

      {/* Subjects Overview (Manual navigation and skipping ahead allowed) */}
      <section>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 className="display text-xl font-bold text-slate-900">All Placement Subjects</h2>
            <p className="text-xs text-slate-500">
              Pick any subject to study or jump ahead. Manual access is always free.
            </p>
          </div>
          <Link to="/curriculum" className="text-sm font-semibold text-accent hover:underline">
            View full 157-topic syllabus →
          </Link>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.subjects.map((subj) => (
            <div
              key={subj.subject_key}
              className={`rounded-2xl border p-5 transition ${
                activeSubject === subj.subject_key
                  ? "border-accent bg-violet-50/30 shadow-sm"
                  : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="rounded-xl bg-slate-100 p-2 text-slate-700">
                    {iconMap[subj.icon] ?? <BookOpen size={20} />}
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 leading-snug">{subj.subject_name}</h3>
                    <p className="text-xs text-slate-400">
                      {subj.completed_concepts} / {subj.total_concepts} concepts ready
                    </p>
                  </div>
                </div>
                <StageBadge stage={subj.progress_state} />
              </div>

              {subj.current_concept_title && (
                <div className="mt-4 rounded-xl bg-slate-50 p-3 text-xs">
                  <span className="font-semibold text-slate-500">Next Concept:</span>
                  <p className="font-medium text-slate-800 truncate mt-0.5">
                    {subj.current_concept_title}
                  </p>
                </div>
              )}

              <div className="mt-4 flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => setActiveSubject(subj.subject_key)}
                  className="text-xs font-semibold text-slate-500 hover:text-slate-800"
                >
                  Set as focus
                </button>
                <Link
                  to={subj.action_path}
                  className="inline-flex items-center gap-1 text-xs font-bold text-accent hover:underline"
                >
                  Open subject <ArrowRight size={13} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Honest Course Availability & Progress Information */}
      {data.content_availability && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="display text-lg font-bold text-slate-900">
            Course Availability & Content Status
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            {data.content_availability.description}
          </p>

          <div className="mt-4 grid gap-3 sm:grid-cols-4">
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Approved Foundations</p>
              <p className="text-lg font-bold text-slate-900">
                {data.content_availability.approved_lessons} lessons
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Beginner Exercises Ready</p>
              <p className="text-lg font-bold text-slate-900">
                {data.content_availability.beginner_exercises_ready} exercises
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Reference Lessons</p>
              <p className="text-lg font-bold text-slate-900">
                {data.content_availability.legacy_reference_lessons} legacy
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Syllabus Scope</p>
              <p className="text-lg font-bold text-slate-900">
                {data.content_availability.total_curriculum_topics} topics
              </p>
            </div>
          </div>

          <p className="mt-3 text-xs text-slate-500 leading-relaxed">
            {data.content_availability.note}
          </p>
        </section>
      )}

      {/* Recent Mistakes revision (if any recorded) */}
      {data.recent_mistakes && data.recent_mistakes.length > 0 && (
        <section className="rounded-2xl border border-rose-200 bg-rose-50/30 p-6">
          <h2 className="display text-lg font-bold text-rose-900">
            Recorded Mistakes to Revisit
          </h2>
          <p className="mt-1 text-xs text-rose-700">
            Revisit concepts where past test errors occurred to ensure clean unassisted solves.
          </p>
          <ul className="mt-4 space-y-2">
            {data.recent_mistakes.map((item, idx) => (
              <li
                key={idx}
                className="flex items-center justify-between rounded-xl bg-white p-3 text-sm shadow-2xs border border-rose-100"
              >
                <div>
                  <span className="font-bold text-slate-900">{item.topic_name}</span>
                  <p className="text-xs text-slate-500">{item.description}</p>
                </div>
                <span className="rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-800">
                  Seen {item.occurrence_count}×
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Secondary Tools Navigation */}
      <section className="grid gap-4 sm:grid-cols-4">
        <Link
          to="/arena"
          className="group rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-violet-300 hover:shadow-sm"
        >
          <div className="flex items-center gap-2 font-bold text-slate-900 group-hover:text-accent">
            <Code2 size={18} className="text-accent" /> Coding Arena
          </div>
          <p className="mt-2 text-xs text-slate-500">
            5 exercise stages from First Steps to Challenging.
          </p>
        </Link>

        <Link
          to="/review"
          className="group rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-violet-300 hover:shadow-sm"
        >
          <div className="flex items-center gap-2 font-bold text-slate-900 group-hover:text-accent">
            <RotateCcw size={18} className="text-accent" /> Due Reviews
          </div>
          <p className="mt-2 text-xs text-slate-500">
            {data.reviews_due_count} topics due in the FSRS spaced repetition queue.
          </p>
        </Link>

        <Link
          to="/tests"
          className="group rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-violet-300 hover:shadow-sm"
        >
          <div className="flex items-center gap-2 font-bold text-slate-900 group-hover:text-accent">
            <Clock3 size={18} className="text-accent" /> Timed Mock Tests
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Resumable subject and mixed assessments with fixed weights.
          </p>
        </Link>

        <Link
          to="/interview"
          className="group rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-violet-300 hover:shadow-sm"
        >
          <div className="flex items-center gap-2 font-bold text-slate-900 group-hover:text-accent">
            <MessageSquare size={18} className="text-accent" /> Interview Rehearsal
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Objective technical questions and unscored communication practice.
          </p>
        </Link>
      </section>
    </div>
  );
}
