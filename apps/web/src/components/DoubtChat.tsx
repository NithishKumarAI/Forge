import { FormEvent, useEffect, useMemo, useState } from "react";
import { LoaderCircle, MessageCircle, Send, X } from "lucide-react";
import { useLocation } from "react-router-dom";
import { api } from "../services/api";
import { Markdown } from "./Markdown";

type Message = { role: "user" | "assistant"; content: string };

export function DoubtChat() {
  const location = useLocation();
  const topicId = useMemo(() => {
    const match = location.pathname.match(/^\/topics\/(\d+)/);
    return match ? Number(match[1]) : null;
  }, [location.pathname]);
  const interviewActive = /^\/interview\/\d+(?:$|\/)/.test(location.pathname) && !location.pathname.endsWith("/report");
  const [context, setContext] = useState("General");
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSessionId(null);
    setMessages([]);
    setError(null);
    if (topicId === null) { setContext("General"); return; }
    let active = true;
    api.topic(topicId)
      .then((topic) => { if (active) setContext(`${topic.track_name} → ${topic.name}`); })
      .catch(() => { if (active) setContext("Current topic"); });
    return () => { active = false; };
  }, [topicId]);

  async function send(event: FormEvent) {
    event.preventDefault();
    const content = input.trim();
    if (!content || sending) return;
    setMessages((current) => [...current, { role: "user", content }]);
    setInput("");
    setSending(true);
    setError(null);
    try {
      const response = await api.doubtMessage({ session_id: sessionId, topic_id: topicId, message: content });
      setSessionId(response.session_id);
      setMessages((current) => [...current, { role: "assistant", content: response.reply }]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Forge Doubts is unavailable.");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {open && (
        <section aria-label="Doubt chat" className="mb-3 flex h-[430px] w-[min(380px,calc(100vw-2.5rem))] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-soft">
          <header className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
            <div><div className="font-semibold text-slate-900">Forge Doubts</div><div className="max-w-64 truncate text-xs text-slate-500">Context: {context} · no mastery effect</div></div>
            <button aria-label="Close chat" onClick={() => setOpen(false)} className="rounded-full p-2 text-slate-500 hover:bg-slate-100"><X size={18} /></button>
          </header>
          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.length === 0 && <div className="rounded-2xl bg-slate-100 px-3.5 py-3 text-sm text-slate-600">{interviewActive ? "Forge Doubts is unavailable during a scored interview. Finish or save the interview to use tutoring." : "Ask a focused technical question. Forge will use the current topic when one is open."}</div>}
            {messages.map((message, index) => (
              <div key={index} className={`max-w-[88%] rounded-2xl px-3.5 py-2.5 text-sm ${message.role === "user" ? "ml-auto bg-ink text-white" : "bg-slate-100 text-slate-700"}`}>{message.role === "assistant" ? <Markdown>{message.content}</Markdown> : message.content}</div>
            ))}
            {sending && <div className="flex items-center gap-2 text-xs text-slate-400"><LoaderCircle size={14} className="animate-spin" /> Thinking…</div>}
            {error && <div role="alert" className="rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-800">{error}</div>}
          </div>
          {!interviewActive && <form onSubmit={send} className="flex gap-2 border-t border-slate-100 p-3">
            <label htmlFor="doubt-input" className="sr-only">Ask a doubt</label>
            <input id="doubt-input" value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask a doubt…" disabled={sending} className="min-w-0 flex-1 rounded-xl bg-slate-100 px-3 py-2.5 text-sm outline-none disabled:opacity-60" />
            <button aria-label="Send message" disabled={sending || !input.trim()} className="rounded-xl bg-accent p-2.5 text-white hover:bg-violet-700 disabled:opacity-40"><Send size={18} /></button>
          </form>}
        </section>
      )}
      <button aria-label="Open doubt chat" onClick={() => setOpen((value) => !value)} className="ml-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-ink text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-slate-700">
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>
    </div>
  );
}
