import type { LucideIcon } from "lucide-react";

export function PlaceholderPage({ title, description, icon: Icon, phase }: { title: string; description: string; icon: LucideIcon; phase: string }) {
  return <div className="mx-auto max-w-3xl"><div className="rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm"><span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-accent-soft text-accent"><Icon size={25} /></span><p className="mt-6 text-sm font-bold uppercase tracking-widest text-accent">Coming in {phase}</p><h1 className="display mt-2 text-3xl font-extrabold">{title}</h1><p className="mx-auto mt-3 max-w-lg leading-7 text-slate-500">{description}</p></div></div>;
}

