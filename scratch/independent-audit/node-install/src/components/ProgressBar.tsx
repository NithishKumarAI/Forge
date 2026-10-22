export function ProgressBar({ value }: { value: number }) {
  return <div className="progress-grid h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-accent transition-all" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div>;
}

