import { lazy, Suspense, useEffect, useState } from "react";
import { ArrowLeft, LoaderCircle, Play, Send } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { Markdown } from "../components/Markdown";
import { ErrorState, LoadingState } from "../components/Status";
import { runPython } from "../features/practice/pythonRunner";
import { api } from "../services/api";
import type { AdaptiveAttempt, TransferSession } from "../types/adaptive";
import type { ExecutionResult } from "../types/practice";

const CodeEditor = lazy(() => import("../components/CodeEditor").then((module) => ({ default: module.CodeEditor })));

export function TransferPage() {
  const topicId = Number(useParams().topicId);
  const [session, setSession] = useState<TransferSession | null>(null);
  const [choice, setChoice] = useState<number | null>(null); const [answer, setAnswer] = useState(""); const [code, setCode] = useState("");
  const [result, setResult] = useState<ExecutionResult | null>(null); const [attempt, setAttempt] = useState<AdaptiveAttempt | null>(null);
  const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null);
  useEffect(() => { api.startTransfer(topicId).then(async (loaded) => {
    if (loaded.exercise.validation_status === "pending") {
      const validation = await api.referenceValidation(loaded.exercise.id);
      const execution = await runPython({ code: validation.reference_solution, functionName: validation.function_name, tests: validation.tests, timeoutMs: validation.time_limit_ms });
      const passed = execution.status === "passed" && execution.tests.every((test) => test.passed);
      await api.reportReferenceValidation(loaded.exercise.id, passed);
      if (!passed) throw new Error("The generated transfer exercise failed validation. Reopen this page to generate a replacement.");
      loaded.exercise.validation_status = "valid";
    }
    setSession(loaded); setCode(loaded.exercise.content.starter_code ?? "");
  }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Transfer check unavailable.")); }, [topicId]);
  if (error && !session) return <ErrorState message={error} />; if (!session) return <LoadingState />;
  const activeSession = session; const exercise = activeSession.exercise; const isCode = exercise.exercise_type.startsWith("python_");
  async function run() { setBusy(true); setError(null); try { setResult(await runPython({ code, functionName: exercise.content.function_name, tests: exercise.content.sample_tests ?? [], timeoutMs: exercise.content.time_limit_ms })); } catch (reason) { setError(reason instanceof Error ? reason.message : "Execution failed"); } finally { setBusy(false); } }
  async function submit() { setBusy(true); setError(null); try {
    if (exercise.exercise_type === "multiple_choice") setAttempt(await api.submitTransfer(activeSession.session_id, { selected_index: choice ?? undefined }));
    else if (exercise.exercise_type === "short_answer") setAttempt(await api.submitTransfer(activeSession.session_id, { answer }));
    else { const tests = await api.submissionTests(exercise.id); const execution = await runPython({ code, functionName: tests.function_name, tests: tests.tests, timeoutMs: tests.time_limit_ms }); setResult(execution); setAttempt(await api.submitTransfer(activeSession.session_id, { source: code, execution })); }
  } catch (reason) { setError(reason instanceof Error ? reason.message : "Submission failed"); } finally { setBusy(false); } }
  return <div className="mx-auto max-w-5xl"><Link to={`/topics/${topicId}`} className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500"><ArrowLeft size={16} /> Topic</Link><section className="mt-6 rounded-3xl border border-slate-200 bg-white p-7 shadow-soft"><p className="text-xs font-bold uppercase tracking-widest text-accent">Unseen transfer check · no hints</p><h1 className="display mt-3 text-3xl font-extrabold">{exercise.title}</h1><div className="mt-4"><Markdown>{exercise.prompt_markdown}</Markdown></div>
    {exercise.exercise_type === "multiple_choice" && <div className="mt-6 space-y-2">{exercise.content.choices?.map((item, index) => <label key={item} className="flex gap-3 rounded-xl border p-4"><input type="radio" checked={choice === index} disabled={Boolean(attempt)} onChange={() => setChoice(index)} />{item}</label>)}</div>}
    {exercise.exercise_type === "short_answer" && <textarea aria-label="Transfer answer" rows={8} value={answer} disabled={Boolean(attempt)} onChange={(event) => setAnswer(event.target.value)} className="mt-6 w-full rounded-xl border bg-slate-50 p-4" />}
    {isCode && <div className="mt-6"><Suspense fallback={<p>Loading editor…</p>}><CodeEditor value={code} onChange={setCode} /></Suspense><button onClick={() => void run()} disabled={busy || Boolean(attempt)} className="mt-3 inline-flex items-center gap-2 rounded-xl border px-4 py-2 font-semibold"><Play size={16} /> Run samples</button></div>}
    {result && <div className="mt-5 rounded-xl bg-slate-950 p-4 text-sm text-white"><strong>{result.status.replaceAll("_", " ")} · {result.duration_ms} ms</strong>{result.stdout && <pre className="mt-2 whitespace-pre-wrap">{result.stdout}</pre>}{result.stderr && <pre className="mt-2 whitespace-pre-wrap text-rose-300">{result.stderr}</pre>}{result.tests.map((test) => <p key={test.name} className={test.passed ? "text-emerald-300" : "text-rose-300"}>{test.passed ? "✓" : "✗"} {test.name} {test.message}</p>)}</div>}
    {attempt && <div className={`mt-6 rounded-2xl p-5 ${attempt.transfer_passed ? "bg-emerald-50 text-emerald-900" : "bg-amber-50 text-amber-900"}`}><strong>Transfer score: {attempt.score ?? "Pending"}% · {attempt.transfer_passed ? "PASS" : "NOT YET"}</strong><p className="mt-2">{attempt.message}</p><Link to={`/topics/${topicId}`} className="mt-4 inline-block font-semibold underline">Return to topic</Link></div>}
    {error && <p role="alert" className="mt-4 rounded-xl bg-red-50 p-4 text-red-700">{error}</p>}{!attempt && <div className="mt-6 flex justify-end"><button onClick={() => void submit()} disabled={busy || (exercise.exercise_type === "multiple_choice" && choice === null) || (exercise.exercise_type === "short_answer" && !answer.trim())} className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-3 font-semibold text-white disabled:opacity-40">{busy ? <LoaderCircle className="animate-spin" size={17} /> : <Send size={17} />} Submit transfer</button></div>}</section></div>;
}
