import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Code2,
  HelpCircle,
  Lightbulb,
  ListChecks,
  Play,
  RotateCcw,
  Sparkles,
  Target,
  XCircle,
  AlertTriangle,
} from "lucide-react";

import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import type { ConceptStepDetail, LearningStage } from "../types/learningPath";

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

export function ConceptLearnPage() {
  const { stepKey = "" } = useParams<{ stepKey: string }>();
  const resource = useApi(() => api.conceptStep(stepKey), [stepKey]);

  if (resource.loading) return <LoadingState />;
  if (resource.error || !resource.data) {
    return <ErrorState message={resource.error ?? "Concept step not found"} />;
  }

  const step: ConceptStepDetail = resource.data;
  const content = step.teaching_content;

  return (
    <div className="mx-auto max-w-5xl space-y-8 pb-16">
      {/* Top Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft size={16} /> Back to Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600 uppercase tracking-wider">
            {step.subject_key}
          </span>
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800 uppercase tracking-wider">
            {step.stage.replace("_", " ")}
          </span>
          <StageBadge stage={step.progress_state} />
        </div>
      </div>

      {/* Hero Header */}
      <header className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-600">
          <BookOpen size={16} /> Concept Step {step.order_index}
        </div>
        <h1 className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
          {step.title}
        </h1>
        <p className="mt-3 text-lg font-medium text-slate-600">
          {step.objective}
        </p>

        {step.action_path && step.action_label && (
          <div className="mt-6 flex flex-wrap items-center gap-4 border-t border-slate-100 pt-6">
            <Link
              to={step.action_path}
              className="inline-flex items-center gap-2 rounded-2xl bg-emerald-600 px-6 py-3 font-bold text-white shadow-md transition-all hover:bg-emerald-700 hover:shadow-lg"
            >
              <Play size={18} fill="currentColor" /> {step.action_label}
            </Link>
            {step.progress_state === "ready_to_advance" && (
              <span className="inline-flex items-center gap-2 text-sm font-bold text-emerald-700">
                <CheckCircle2 size={18} /> Verified: Concept mastered!
              </span>
            )}
          </div>
        )}
      </header>

      {/* Candidate Notice if applicable */}
      {step.availability_status === "candidate_unreviewed" && (
        <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          <AlertTriangle size={18} className="mt-0.5 shrink-0 text-amber-600" />
          <div>
            <strong className="font-semibold">Candidate Material (Pending Independent Review):</strong>{" "}
            This lesson is authored under the Placement Foundations rubric. Guided practice exercises are verified and deterministically graded.
          </div>
        </div>
      )}

      {/* Main Teaching Content View */}
      {content ? (
        <div className="space-y-8">
          {/* Section 1: Mental Model & Intuition */}
          <section className="space-y-4 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="flex items-center gap-2 text-xl font-extrabold text-slate-900">
              <Sparkles size={20} className="text-emerald-600" /> Concept Meaning & Mental Model
            </h2>
            <p className="text-base leading-relaxed text-slate-700">
              {content.summary}
            </p>

            <div className="grid gap-4 sm:grid-cols-2 pt-2">
              <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-5">
                <h3 className="flex items-center gap-2 text-sm font-bold text-blue-900">
                  <Lightbulb size={16} /> Mental Intuition
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-blue-800">
                  {content.intuition}
                </p>
              </div>

              <div className="rounded-2xl border border-purple-100 bg-purple-50/60 p-5">
                <h3 className="flex items-center gap-2 text-sm font-bold text-purple-900">
                  <Target size={16} /> Real-World Analogy
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-purple-800">
                  {content.analogy}
                </p>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-100 bg-slate-50 p-4 text-xs text-slate-600">
              <strong className="font-semibold text-slate-800">Why It Matters in Software Engineering:</strong>{" "}
              {content.why_it_matters}
            </div>
          </section>

          {/* Section 2: Syntax Guide */}
          <section className="space-y-4 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="flex items-center gap-2 text-xl font-extrabold text-slate-900">
              <Code2 size={20} className="text-emerald-600" /> Syntax & Mechanics
            </h2>
            <div className="overflow-x-auto rounded-2xl bg-slate-900 p-5 font-mono text-sm leading-relaxed text-emerald-300">
              <pre>{content.syntax_guide}</pre>
            </div>
          </section>

          {/* Section 3: Worked Example with Tracing Table */}
          <section className="space-y-4 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="flex items-center gap-2 text-xl font-extrabold text-slate-900">
              <CheckCircle2 size={20} className="text-emerald-600" /> Worked Example: {content.worked_example_title}
            </h2>
            <p className="text-sm text-slate-600">
              {content.worked_example_explanation}
            </p>

            <div className="overflow-x-auto rounded-2xl bg-slate-900 p-5 font-mono text-sm leading-relaxed text-emerald-300">
              <pre>{content.worked_example_code}</pre>
            </div>

            {content.tracing_steps.length > 0 && (
              <div className="mt-6 space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                  Step-by-Step Execution Trace
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-700">
                    <thead className="border-b border-slate-200 bg-slate-50 text-xs font-bold text-slate-500 uppercase tracking-wider">
                      <tr>
                        <th className="py-3 px-4">Step</th>
                        <th className="py-3 px-4">Expression / Line</th>
                        <th className="py-3 px-4">State Description</th>
                        <th className="py-3 px-4">Result / Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {content.tracing_steps.map((trace) => (
                        <tr key={trace.step_number} className="hover:bg-slate-50/50">
                          <td className="py-3 px-4 font-bold text-slate-900">{trace.step_number}</td>
                          <td className="py-3 px-4 font-mono text-xs text-blue-700 font-semibold">{trace.line_or_expression}</td>
                          <td className="py-3 px-4">{trace.state_description}</td>
                          <td className="py-3 px-4 font-mono text-xs text-emerald-700 font-bold">{trace.result_or_value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>

          {/* Section 4: Common Beginner Mistakes */}
          {content.common_mistakes.length > 0 && (
            <section className="space-y-4 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <h2 className="flex items-center gap-2 text-xl font-extrabold text-slate-900">
                <AlertTriangle size={20} className="text-rose-600" /> Common Mistakes & Fixes
              </h2>

              <div className="grid gap-6 md:grid-cols-2">
                {content.common_mistakes.map((mistake, idx) => (
                  <div key={idx} className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50/50 p-5">
                    <h3 className="text-sm font-bold text-slate-900">
                      {idx + 1}. {mistake.mistake_description}
                    </h3>
                    <div className="rounded-xl border border-rose-200 bg-rose-50/50 p-3 font-mono text-xs text-rose-900">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-rose-500">Wrong:</div>
                      <pre className="mt-1 whitespace-pre-wrap">{mistake.wrong_code}</pre>
                    </div>
                    <p className="text-xs leading-relaxed text-slate-600">
                      {mistake.explanation}
                    </p>
                    <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-3 font-mono text-xs text-emerald-900">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-600">Correct:</div>
                      <pre className="mt-1 whitespace-pre-wrap">{mistake.correct_code}</pre>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Section 5: Revision Notes */}
          {content.revision_notes.length > 0 && (
            <section className="space-y-4 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <h2 className="flex items-center gap-2 text-xl font-extrabold text-slate-900">
                <ListChecks size={20} className="text-emerald-600" /> Key Takeaways Checklist
              </h2>
              <ul className="space-y-2">
                {content.revision_notes.map((note, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-700">
                    <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-600" />
                    <span>{note}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      ) : (
        /* Fallback if worked example exists without full teaching content */
        step.worked_example && (
          <section className="space-y-4 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-xl font-extrabold text-slate-900">
              Worked Example: {step.worked_example.title}
            </h2>
            <div className="overflow-x-auto rounded-2xl bg-slate-900 p-5 font-mono text-sm leading-relaxed text-emerald-300">
              <pre>{step.worked_example.code}</pre>
            </div>
            <p className="text-sm text-slate-600">{step.worked_example.explanation}</p>
          </section>
        )
      )}

      {/* Section 6: Guided & Independent Practice Progression */}
      <section className="space-y-6 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <h2 className="text-xl font-extrabold text-slate-900">
          Practice & Evidence Progression
        </h2>

        {/* Guided practice exercises */}
        {step.guided_practice_refs.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Guided Interactive Exercises ({step.guided_practice_refs.length})
            </h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {step.guided_practice_refs.map((refKey) => (
                <Link
                  key={refKey}
                  to={`/arena/exercises/${refKey}`}
                  className="group flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50/50 p-4 transition-all hover:border-emerald-500 hover:bg-white hover:shadow-sm"
                >
                  <div>
                    <span className="text-xs font-bold text-slate-400">Exercise</span>
                    <h4 className="font-bold text-slate-900 group-hover:text-emerald-700">
                      {refKey.replace(/^py-first-|^sql-first-|^dsa-first-/, "").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    </h4>
                  </div>
                  <ArrowRight size={18} className="text-slate-400 group-hover:text-emerald-600" />
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Independent practice in arena */}
        {step.independent_practice_refs.length > 0 && (
          <div className="space-y-3 pt-4 border-t border-slate-100">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Independent Practice in Arena
            </h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {step.independent_practice_refs.map((probKey) => (
                <Link
                  key={probKey}
                  to={`/arena/problems/${probKey}`}
                  className="group flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50/50 p-4 transition-all hover:border-emerald-500 hover:bg-white hover:shadow-sm"
                >
                  <div>
                    <span className="text-xs font-bold text-slate-400">Arena Challenge</span>
                    <h4 className="font-bold text-slate-900 group-hover:text-emerald-700">
                      {probKey.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    </h4>
                  </div>
                  <ArrowRight size={18} className="text-slate-400 group-hover:text-emerald-600" />
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
