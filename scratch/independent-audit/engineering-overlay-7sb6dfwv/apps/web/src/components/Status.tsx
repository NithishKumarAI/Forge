import { AlertCircle, LoaderCircle } from "lucide-react";

export function LoadingState() {
  return <div className="flex min-h-56 items-center justify-center gap-3 text-slate-500"><LoaderCircle className="animate-spin" size={20} /> Loading Forge…</div>;
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-800">
      <div className="flex items-center gap-2 font-semibold"><AlertCircle size={19} /> Forge could not load this page</div>
      <p className="mt-2 text-sm">{message}. Make sure the API is running on port 8000.</p>
    </div>
  );
}

