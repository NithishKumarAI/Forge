import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";

// Configure before the Editor child mounts; a parent effect runs too late and
// may let the loader start its default CDN request on first render.
loader.config({ monaco });
if (typeof self !== "undefined") {
  const environment = self as typeof self & { MonacoEnvironment?: { getWorker: () => Worker } };
  environment.MonacoEnvironment = { getWorker: () => new Worker(new URL("../../node_modules/monaco-editor/esm/vs/editor/editor.worker.js", import.meta.url), { type: "module" }) };
}

export function CodeEditor({ value, onChange, language = "python", readOnly=false }: { value: string; onChange: (value: string) => void; language?: string; readOnly?:boolean }) {
  return <div className="overflow-hidden rounded-xl border border-slate-200"><Editor height="350px" language={language} theme="vs" value={value} onChange={(next) => onChange(next ?? "")} options={{ readOnly,ariaLabel:"Assessment source",minimap: { enabled: false }, automaticLayout: true, fontSize: 14, lineNumbers: "on", tabSize: 4, scrollBeyondLastLine: false }} /></div>;
}
