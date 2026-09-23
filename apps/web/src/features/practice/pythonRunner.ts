import type { ExecutionResult, PythonTest } from "../../types/practice";

let worker: Worker | null = null;
let ready: Promise<void> | null = null;
let nextId = 1;

function createWorker() {
  worker = new Worker(new URL("./python.worker.ts", import.meta.url), { type: "module" });
  const current = worker;
  ready = new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => { current.terminate(); worker = null; ready = null; reject(new Error("Python runtime could not initialize.")); }, 60000);
    const onMessage = (event: MessageEvent) => {
      if (event.data?.type === "init_error") {
        window.clearTimeout(timer);
        current.removeEventListener("message", onMessage);
        current.terminate(); worker = null; ready = null;
        reject(new Error(`Python runtime could not initialize: ${event.data.message}`));
        return;
      }
      if (event.data?.type !== "ready") return;
      window.clearTimeout(timer);
      current.removeEventListener("message", onMessage);
      resolve();
    };
    current.addEventListener("message", onMessage);
    current.addEventListener("error", () => { window.clearTimeout(timer); current.terminate(); worker = null; ready = null; reject(new Error("Python runtime could not initialize.")); }, { once: true });
  });
}

export async function runPython(options: {
  code: string;
  functionName?: string;
  tests: PythonTest[];
  timeoutMs?: number;
}): Promise<ExecutionResult> {
  if (!worker || !ready) createWorker();
  await ready;
  const current = worker!;
  const id = nextId++;
  return new Promise((resolve) => {
    const started = performance.now();
    const timer = window.setTimeout(() => {
      current.removeEventListener("message", onMessage);
      current.terminate();
      worker = null;
      ready = null;
      resolve({ status: "timeout", stdout: "", stderr: "Execution timed out. The Python worker was restarted.", tests: [], duration_ms: Math.round(performance.now() - started) });
    }, options.timeoutMs ?? 5000);
    const onMessage = (event: MessageEvent) => {
      if (event.data?.type !== "result" || event.data.id !== id) return;
      window.clearTimeout(timer);
      current.removeEventListener("message", onMessage);
      resolve(event.data.result as ExecutionResult);
    };
    current.addEventListener("message", onMessage);
    current.postMessage({ id, code: options.code, functionName: options.functionName, tests: options.tests });
  });
}
