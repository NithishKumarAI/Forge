import { useEffect } from "react";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";

export function CodeEditor({ value, onChange, language = "python" }: { value: string; onChange: (value: string) => void; language?: string }) {
  useEffect(() => {
    const environment = self as typeof self & { MonacoEnvironment?: { getWorker: () => Worker } };
    environment.MonacoEnvironment = { getWorker: () => new Worker(new URL("../../node_modules/monaco-editor/esm/vs/editor/editor.worker.js", import.meta.url), { type: "module" }) };
    loader.config({ monaco });
  }, []);
  return <div className="overflow-hidden rounded-xl border border-slate-200"><Editor height="350px" language={language} theme="vs" value={value} onChange={(next) => onChange(next ?? "")} options={{ minimap: { enabled: false }, automaticLayout: true, fontSize: 14, lineNumbers: "on", tabSize: 4, scrollBeyondLastLine: false }} /></div>;
}
