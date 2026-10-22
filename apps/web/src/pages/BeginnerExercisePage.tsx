import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, Lightbulb, Play, RotateCcw, Send, XCircle } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { CodeEditor } from "../components/CodeEditor";
import { Markdown } from "../components/Markdown";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import type { BeginnerExerciseResult } from "../types/learningPath";

export function BeginnerExercisePage() {
  const { key = "" } = useParams<{ key: string }>();
  const resource = useApi(() => api.beginnerExercise(key), [key]);
  const [source, setSource] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<BeginnerExerciseResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [hintsRevealed, setHintsRevealed] = useState<number>(0);

  useEffect(() => {
    if (resource.data) {
      const initialCode =
        resource.data.track === "sql"
          ? resource.data.starter_query ?? "SELECT "
          : resource.data.starter_code ?? "";
      setSource(initialCode);
      setResult(null);
      setErrorMsg("");
      setHintsRevealed(0);
    }
  }, [resource.data?.key]);

  if (resource.loading) return <LoadingState />;
  if (resource.error || !resource.data) {
    return <ErrorState message={resource.error ?? "Beginner exercise not found"} />;
  }

  const ex = resource.data;

  async function submit() {
    setBusy(true);
    setErrorMsg("");
    try {
      const res = await api.submitBeginnerExercise(key, source);
      setResult(res);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    const initialCode =
      ex.track === "sql" ? ex.starter_query ?? "SELECT " : ex.starter_code ?? "";
    setSource(initialCode);
    setResult(null);
    setErrorMsg("");
  }

  function revealNextHint() {
    if (hintsRevealed < ex.hints.length) {
      setHintsRevealed((prev) => prev + 1);
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link
          to="/arena"
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft size={16} /> Back to Coding Arena
        </Link>
        {ex.concept_key && (
          <Link
            to={`/concepts/${ex.concept_key}`}
            className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-800 hover:bg-emerald-100"
          >
            ← Back to Concept: {ex.concept_title ?? ex.concept_key}
          </Link>
        )}
      </div>

      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-emerald-100 px-3 py-0.5 text-xs font-bold text-emerald-800 uppercase tracking-wide">
              {ex.stage.replace("_", " ")}
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-0.5 text-xs font-semibold text-slate-600 uppercase">
              {ex.track.toUpperCase()}
            </span>
            {ex.solved && (
              <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600">
                <CheckCircle2 size={14} /> Solved
              </span>
            )}
          </div>
          <h1 className="display mt-2 text-3xl font-extrabold text-slate-900">{ex.title}</h1>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[.9fr_1.1fr]">
        {/* Left: Instructions, Examples & Hints */}
        <div className="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Instructions</h2>
            <div className="mt-2 text-slate-800 leading-relaxed">
              <Markdown>{ex.instructions}</Markdown>
            </div>
          </div>

          {ex.examples.length > 0 && (
            <div>
              <h3 className="font-bold text-slate-900">Example</h3>
              <div className="mt-2 space-y-2">
                {ex.examples.map((eg, i) => (
                  <div key={i} className="rounded-xl bg-slate-50 p-3 text-sm font-mono space-y-1">
                    <p className="text-slate-600">Input: <span className="text-slate-900 font-semibold">{eg.input}</span></p>
                    <p className="text-slate-600">Output: <span className="text-emerald-700 font-semibold">{eg.output}</span></p>
                    {eg.explanation && (
                      <p className="font-sans text-xs text-slate-500 pt-1">{eg.explanation}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {ex.hints.length > 0 && (
            <div className="border-t border-slate-100 pt-4">
              <button
                type="button"
                onClick={revealNextHint}
                disabled={hintsRevealed >= ex.hints.length}
                className="inline-flex items-center gap-2 text-xs font-bold text-accent hover:underline disabled:opacity-50"
              >
                <Lightbulb size={14} /> Reveal Hint ({hintsRevealed}/{ex.hints.length})
              </button>
              {hintsRevealed > 0 && (
                <div className="mt-3 space-y-2">
                  {ex.hints.slice(0, hintsRevealed).map((h, i) => (
                    <div key={i} className="rounded-xl bg-amber-50 p-3 text-xs text-amber-900 border border-amber-200/60">
                      <strong>Hint {i + 1}:</strong> {h}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Code Editor & Execution Results */}
        <div className="space-y-4">
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-2 text-xs font-semibold text-slate-500">
              <span>{ex.track === "sql" ? "SQL Query" : "Python Solution"}</span>
              <button
                onClick={reset}
                className="inline-flex items-center gap-1 text-slate-500 hover:text-slate-900"
              >
                <RotateCcw size={13} /> Reset
              </button>
            </div>
            <CodeEditor
              value={source}
              onChange={setSource}
              language={ex.track === "sql" ? "sql" : "python"}
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              disabled={busy || !source.trim()}
              onClick={submit}
              className="inline-flex items-center gap-2 rounded-xl bg-accent px-6 py-3 font-bold text-white shadow-sm transition hover:bg-violet-700 disabled:opacity-50"
            >
              <Send size={16} /> Submit & Check
            </button>
            {busy && <span className="text-xs text-slate-500">Checking solution...</span>}
          </div>

          {errorMsg && (
            <div className="rounded-xl bg-rose-50 p-4 text-sm text-rose-800 border border-rose-200">
              {errorMsg}
            </div>
          )}

          {result && (
            <div
              className={`rounded-2xl border p-5 space-y-3 ${
                result.passed
                  ? "border-emerald-200 bg-emerald-50/40"
                  : "border-rose-200 bg-rose-50/40"
              }`}
            >
              <div className="flex items-center gap-2">
                {result.passed ? (
                  <CheckCircle2 size={20} className="text-emerald-600" />
                ) : (
                  <XCircle size={20} className="text-rose-600" />
                )}
                <h3
                  className={`font-bold ${
                    result.passed ? "text-emerald-900" : "text-rose-900"
                  }`}
                >
                  {result.passed ? "Solution Passed!" : "Checks Did Not Pass"}
                </h3>
                <span className="ml-auto text-xs font-bold text-slate-500">
                  Score: {result.score}%
                </span>
              </div>

              <p className="text-sm text-slate-700">{result.feedback}</p>

              {result.output && (
                <pre className="rounded-xl bg-white p-3 font-mono text-xs text-slate-800 border overflow-x-auto">
                  {result.output}
                </pre>
              )}

              {result.passed && result.solution && (
                <div className="mt-4 rounded-xl bg-white p-4 border border-emerald-200 space-y-2">
                  <h4 className="text-xs font-bold uppercase text-emerald-800">Reference Solution</h4>
                  <pre className="rounded-lg bg-slate-900 p-3 font-mono text-xs text-white overflow-x-auto">
                    {result.solution}
                  </pre>
                  {result.explanation && (
                    <p className="text-xs text-slate-600 pt-1">{result.explanation}</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
