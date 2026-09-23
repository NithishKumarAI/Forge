import { FormEvent, useEffect, useRef, useState } from "react";
import { ArrowLeft, LoaderCircle, Send, Sparkles } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { Markdown } from "../components/Markdown";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

type ConversationMessage = { role: "assistant" | "user"; content: string };

export function LearnPage() {
  const topicId = Number(useParams().topicId);
  const topic = useApi(() => api.topic(topicId), [topicId]);
  const ai = useApi(api.aiStatus, []);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!topic.data || !ai.data?.configured || started.current) return;
    started.current = true;
    setBusy(true);
    api.startTutor(topicId)
      .then((response) => {
        setSessionId(response.session_id);
        setMessages([{ role: "assistant", content: response.turn.message_markdown }]);
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "The tutor is unavailable."))
      .finally(() => setBusy(false));
  }, [topic.data, ai.data, topicId]);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, busy]);

  async function send(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || !sessionId || busy) return;
    setMessages((current) => [...current, { role: "user", content: message }]);
    setInput("");
    setBusy(true);
    setError(null);
    try {
      const turn = await api.tutorMessage(sessionId, message);
      setMessages((current) => [...current, { role: "assistant", content: turn.message_markdown }]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The tutor is temporarily unavailable.");
    } finally {
      setBusy(false);
    }
  }

  if (topic.loading || ai.loading) return <LoadingState />;
  if (topic.error || !topic.data) return <ErrorState message={topic.error ?? "Topic not found"} />;
  if (ai.error || !ai.data) return <ErrorState message={ai.error ?? "AI status unavailable"} />;
  const currentTopic = topic.data;

  return <div className="mx-auto flex max-w-4xl flex-col"><header className="mb-5"><Link to={`/topics/${topicId}`} className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-accent"><ArrowLeft size={16} /> Topic overview</Link><div className="mt-5 flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-semibold text-accent">{currentTopic.track_name} · Learn</p><h1 className="display mt-1 text-3xl font-extrabold">{currentTopic.name}</h1></div><span className="rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-slate-500">Mastery stays {currentTopic.state.mastery_score}% in Learn mode</span></div></header>{!ai.data.configured ? <div className="rounded-3xl border border-amber-200 bg-amber-50 p-8"><Sparkles className="text-amber-600" /><h2 className="display mt-4 text-xl font-bold text-amber-950">Gemini isn’t configured yet</h2><p className="mt-2 max-w-xl text-sm leading-6 text-amber-800">Add <code>GEMINI_API_KEY</code> to <code>apps/api/.env</code>, restart the backend, then return here. The rest of Forge remains available without AI.</p><Link to="/settings" className="mt-5 inline-flex rounded-xl bg-amber-900 px-4 py-2.5 text-sm font-semibold text-white">View setup status</Link></div> : <section className="flex min-h-[620px] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-soft"><div className="border-b border-slate-100 px-6 py-4 text-sm text-slate-500">Forge Tutor · concise, practical, interview-focused</div><div className="flex-1 space-y-5 overflow-y-auto p-5 sm:p-7">{messages.map((message, index) => <div key={index} className={message.role === "user" ? "ml-auto max-w-[80%] rounded-2xl bg-ink px-4 py-3 text-sm text-white" : "max-w-[92%] rounded-2xl bg-slate-50 px-5 py-4"}>{message.role === "assistant" ? <><div className="mb-2 text-xs font-bold uppercase tracking-widest text-accent">Forge</div><Markdown>{message.content}</Markdown></> : message.content}</div>)}{busy && <div className="flex items-center gap-2 text-sm text-slate-400"><LoaderCircle size={17} className="animate-spin" /> Forge is thinking…</div>}{error && <div role="alert" className="rounded-xl bg-amber-50 p-3 text-sm text-amber-800">{error}</div>}<div ref={bottom} /></div><form onSubmit={send} className="border-t border-slate-100 p-4"><div className="flex gap-3"><label htmlFor="tutor-input" className="sr-only">Answer or ask a question</label><input id="tutor-input" value={input} onChange={(event) => setInput(event.target.value)} disabled={!sessionId || busy} placeholder="Type your answer or ask a question…" className="min-w-0 flex-1 rounded-xl bg-slate-100 px-4 py-3 text-sm outline-none disabled:opacity-50" /><button disabled={!sessionId || busy || !input.trim()} className="flex items-center gap-2 rounded-xl bg-accent px-4 py-3 font-semibold text-white hover:bg-violet-700 disabled:opacity-40"><Send size={17} /> Send</button></div></form></section>}</div>;
}

