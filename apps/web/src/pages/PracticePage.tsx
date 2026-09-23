import { FormEvent, lazy, Suspense, useEffect, useRef, useState } from "react";
import { ArrowLeft, CheckCircle2, ChevronRight, LoaderCircle, Play, RotateCcw, Send } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { Markdown } from "../components/Markdown";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { runPython } from "../features/practice/pythonRunner";
import type { Attempt, ExecutionResult, Exercise, PracticePack } from "../types/practice";

const CodeEditor = lazy(() => import("../components/CodeEditor").then((module) => ({ default: module.CodeEditor })));

export function PracticePage() {
  const topicId = Number(useParams().topicId);
  const topic = useApi(() => api.topic(topicId), [topicId]);
  const [pack, setPack] = useState<PracticePack | null>(null);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [choice, setChoice] = useState<number | null>(null);
  const [code, setCode] = useState("");
  const [hints, setHints] = useState<string[]>([]);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [submissions, setSubmissions] = useState<Record<number, Attempt>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingPack, setLoadingPack] = useState(true);
  const startedTopicId = useRef<number | null>(null);

  useEffect(() => {
    if (startedTopicId.current === topicId) return;
    startedTopicId.current = topicId;
    setLoadingPack(true);
    setPack(null);
    setSubmissions({});
    setIndex(0);
    setError(null);
    const key = `forge-practice-session-${topicId}`;
    const saved = Number(localStorage.getItem(key));
    const load = saved ? api.practiceSession(saved).catch(() => api.startPractice(topicId)) : api.startPractice(topicId);
    load.then(async (loaded) => {
      let current = loaded;
      let validationError: string | null = null;
      for (let round = 0; round < 2; round++) {
        let foundInvalid = false;
        for (const exercise of current.exercises) {
          if (exercise.validation_status !== "pending") continue;
          try {
            const validation = await api.referenceValidation(exercise.id);
            const execution = await runPython({ code: validation.reference_solution, functionName: validation.function_name, tests: validation.tests, timeoutMs: validation.time_limit_ms });
            const passed = execution.status === "passed" && execution.tests.length === validation.tests.length;
            await api.reportReferenceValidation(exercise.id, passed);
            if (!passed) foundInvalid = true;
            else exercise.validation_status = "valid";
          } catch (reason) {
            validationError = reason instanceof Error ? reason.message : "Python reference validation is unavailable.";
            break;
          }
        }
        if (validationError || !foundInvalid) break;
        current = await api.startPractice(topicId);
      }
      if (!validationError && current.exercises.some((exercise) => exercise.validation_status === "pending")) {
        setError("A replacement coding exercise still needs validation. Reopen Practice to retry.");
      }
      if (validationError) setError(`Python reference validation is unavailable: ${validationError}`);
      localStorage.setItem(key, String(current.session_id));
      setPack(current);
      const history = await api.practiceHistory(topicId);
      const completed = Object.fromEntries(history.attempts.filter((attempt) => attempt.session_id === current.session_id).map((attempt) => [attempt.exercise_id, attempt]));
      setSubmissions(completed);
      const firstOpen = current.exercises.findIndex((exercise) => !completed[exercise.id]);
      setIndex(firstOpen < 0 ? current.exercises.length : firstOpen);
    }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Practice is unavailable."))
      .finally(() => setLoadingPack(false));
  }, [topicId]);

  const exercise = pack?.exercises[index];
  useEffect(() => {
    setAnswer(""); setChoice(null); setHints([]); setResult(null);
    setCode(exercise?.content.starter_code ?? "");
  }, [exercise?.id]);

  async function openHint() {
    if (!exercise || !pack || busy) return;
    setBusy(true); setError(null);
    try {
      const hint = await api.revealHint(exercise.id, pack.session_id);
      setHints((current) => [...current, hint.text]);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Hint unavailable."); }
    finally { setBusy(false); }
  }

  async function runSample() {
    if (!exercise) return;
    setBusy(true); setError(null);
    try {
      const execution = await runPython({ code, functionName: exercise.content.function_name, tests: exercise.content.sample_tests ?? [], timeoutMs: exercise.content.time_limit_ms });
      setResult(execution);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Python execution failed."); }
    finally { setBusy(false); }
  }

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    if (!exercise || !pack || busy) return;
    setBusy(true); setError(null);
    try {
      let attempt: Attempt;
      if (exercise.exercise_type === "multiple_choice") {
        if (choice === null) return;
        attempt = await api.submitMcq(exercise.id, pack.session_id, choice);
      } else if (exercise.exercise_type === "short_answer") {
        if (!answer.trim()) return;
        attempt = await api.submitShortAnswer(exercise.id, pack.session_id, answer.trim());
      } else {
        const tests = await api.submissionTests(exercise.id);
        const execution = await runPython({ code, functionName: tests.function_name, tests: tests.tests, timeoutMs: tests.time_limit_ms });
        setResult(execution);
        attempt = await api.submitCode(exercise.id, pack.session_id, code, execution);
      }
      setSubmissions((current) => ({ ...current, [exercise.id]: attempt }));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Submission failed."); }
    finally { setBusy(false); }
  }

  function next() {
    if (!pack) return;
    const nextIndex = index + 1;
    setIndex(nextIndex);
    if (nextIndex >= pack.exercises.length) localStorage.removeItem(`forge-practice-session-${topicId}`);
  }

  if (topic.loading || loadingPack) return <LoadingState />;
  if (topic.error || !topic.data) return <ErrorState message={topic.error ?? "Topic unavailable"} />;
  if (!pack) return <div className="mx-auto max-w-3xl"><Link to={`/topics/${topicId}`} className="text-sm text-accent">← Topic</Link><div className="mt-6 rounded-2xl bg-amber-50 p-6 text-amber-900">{error ?? "Practice is unavailable."}</div></div>;
  const completed = Object.values(submissions);
  if (index >= pack.exercises.length) {
    const scored = completed.filter((item) => item.score !== null);
    const passed = completed.filter((item) => item.passed).length;
    const average = scored.length ? Math.round(scored.reduce((sum, item) => sum + (item.score ?? 0), 0) / scored.length) : null;
    const hintCount = completed.reduce((sum, item) => sum + item.hints_used_count, 0);
    return <div className="mx-auto max-w-3xl"><div className="rounded-3xl bg-white p-10 text-center shadow-soft"><CheckCircle2 className="mx-auto text-accent" size={42} /><h1 className="display mt-4 text-3xl font-extrabold">Practice complete</h1><p className="mt-2 text-slate-500">Evidence saved for future mastery evaluation.</p><div className="mt-8 grid grid-cols-3 gap-3 text-center"><div><strong className="text-2xl">{passed}/{pack.exercises.length}</strong><p className="text-xs text-slate-500">Passed</p></div><div><strong className="text-2xl">{average === null ? "Pending" : `${average}%`}</strong><p className="text-xs text-slate-500">Average score</p></div><div><strong className="text-2xl">{hintCount}</strong><p className="text-xs text-slate-500">Hints used</p></div></div><div className="mt-8 flex flex-wrap justify-center gap-3"><Link to={`/topics/${topicId}`} className="rounded-xl bg-accent px-5 py-3 font-semibold text-white">Return to topic</Link><Link to={`/topics/${topicId}/learn`} className="rounded-xl border px-5 py-3 font-semibold">Return to Learn</Link></div></div></div>;
  }
  if (!exercise) return <ErrorState message="This practice exercise is unavailable" />;
  const attempt = exercise ? submissions[exercise.id] : undefined;
  const isCode = exercise?.exercise_type.startsWith("python_");
  return <div className="mx-auto max-w-5xl"><Link to={`/topics/${topicId}`} className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-accent"><ArrowLeft size={16} /> Topic overview</Link><header className="mt-5 flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-semibold text-accent">{topic.data.track_name} → {topic.data.name}</p><h1 className="display mt-1 text-3xl font-extrabold">Practice</h1></div><p className="rounded-full bg-white px-4 py-2 text-sm font-semibold">Exercise {index + 1} of {pack.exercises.length}</p></header><div className="mt-5 flex gap-2">{pack.exercises.map((item, position) => <span key={item.id} className={`h-2 flex-1 rounded-full ${position < index ? "bg-emerald-400" : position === index ? "bg-accent" : "bg-slate-200"}`} />)}</div><section className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sm:p-8"><div className="flex flex-wrap items-center gap-2"><span className="rounded-full bg-accent-soft px-3 py-1 text-xs font-bold uppercase tracking-wider text-accent">{exercise.exercise_type.replaceAll("_", " ")}</span><span className="text-xs text-slate-400">{exercise.difficulty}</span></div><h2 className="display mt-4 text-2xl font-bold">{exercise.title}</h2><div className="mt-4"><Markdown>{exercise.prompt_markdown}</Markdown></div>{isCode && exercise.validation_status !== "valid" && <div className="mt-5 rounded-xl bg-amber-50 p-4 text-sm text-amber-900">This exercise is being validated. Start a fresh pack if validation did not complete.</div>}{exercise.exercise_type === "multiple_choice" && <div className="mt-6 space-y-2">{exercise.content.choices?.map((item, position) => <label key={position} className={`flex cursor-pointer items-start gap-3 rounded-xl border p-4 ${choice === position ? "border-accent bg-accent-soft" : "border-slate-200"}`}><input type="radio" name={`choice-${exercise.id}`} checked={choice === position} disabled={Boolean(attempt)} onChange={() => setChoice(position)} /><span>{item}</span></label>)}</div>}{exercise.exercise_type === "short_answer" && <textarea aria-label="Your answer" value={answer} onChange={(event) => setAnswer(event.target.value)} disabled={Boolean(attempt)} rows={7} placeholder="Explain your reasoning in your own words…" className="mt-6 w-full rounded-xl border border-slate-200 bg-slate-50 p-4 outline-none" />}{isCode && <div className="mt-6"><Suspense fallback={<div className="rounded-xl bg-slate-50 p-6 text-sm text-slate-500">Loading editor…</div>}><CodeEditor value={code} onChange={setCode} /></Suspense><div className="mt-3 flex flex-wrap gap-2"><button onClick={() => setCode(exercise.content.starter_code ?? "")} disabled={busy || Boolean(attempt)} className="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-semibold"><RotateCcw size={16} /> Reset</button><button onClick={() => void runSample()} disabled={busy || Boolean(attempt)} className="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-semibold"><Play size={16} /> Run sample tests</button></div></div>}{result && <section className="mt-6 rounded-2xl bg-slate-950 p-5 text-sm text-slate-100"><h3 className="font-bold">Output · {result.status.replaceAll("_", " ")} · {result.duration_ms} ms</h3>{result.stdout && <pre className="mt-3 overflow-x-auto whitespace-pre-wrap">{result.stdout}</pre>}{result.stderr && <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-rose-300">{result.stderr}</pre>}{result.tests.length > 0 && <div className="mt-4 space-y-1">{result.tests.map((test, position) => <p key={position} className={test.passed ? "text-emerald-300" : "text-rose-300"}>{test.passed ? "✓" : "✗"} {test.name}{test.message && ` — ${test.message}`}</p>)}</div>}</section>}{exercise.hints_available > 0 && <div className="mt-6 rounded-2xl bg-slate-50 p-4"><div className="flex items-center justify-between"><h3 className="font-semibold">Hints ({hints.length}/{exercise.hints_available})</h3>{hints.length < exercise.hints_available && !attempt && <button onClick={() => void openHint()} disabled={busy} className="text-sm font-semibold text-accent">Reveal next hint</button>}</div>{hints.map((hint, hintIndex) => <p key={hintIndex} className="mt-3 text-sm text-slate-600">{hintIndex + 1}. {hint}</p>)}</div>}{attempt && <div className={`mt-6 rounded-2xl p-4 ${attempt.passed ? "bg-emerald-50 text-emerald-900" : "bg-amber-50 text-amber-900"}`}><strong>{attempt.evaluation_status === "pending" ? "Evaluation pending" : `${attempt.score}% · ${attempt.passed ? "Passed" : "Keep practicing"}`}</strong><div className="mt-2"><Markdown>{attempt.feedback}</Markdown></div><p className="mt-2 text-xs">Hints used: {attempt.hints_used_count}</p></div>}{error && <div role="alert" className="mt-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div>}<div className="mt-6 flex justify-end">{attempt ? <button onClick={next} className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-3 font-semibold text-white">{index + 1 === pack.exercises.length ? "Finish practice" : "Next exercise"}<ChevronRight size={17} /></button> : <button onClick={() => void submit()} disabled={busy || (exercise.exercise_type === "multiple_choice" && choice === null) || (exercise.exercise_type === "short_answer" && !answer.trim()) || (isCode && exercise.validation_status !== "valid")} className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-3 font-semibold text-white disabled:opacity-40">{busy ? <LoaderCircle size={17} className="animate-spin" /> : <Send size={17} />} Submit</button>}</div></section></div>;
}
