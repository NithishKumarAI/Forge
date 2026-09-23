import type { ExecutionResult, PythonTest } from "../../types/practice";
import { loadPyodide } from "pyodide";

type Pyodide = {
  globals: { set: (name: string, value: unknown) => void };
  runPythonAsync: (code: string) => Promise<string>;
};

let pyodide: Pyodide | null = null;

const HARNESS = `
import asyncio, contextlib, inspect, io, json, traceback
_stdout = io.StringIO()
_stderr = io.StringIO()
_results = []
_status = 'passed'
_namespace = {'__name__': '__forge_exercise__'}
try:
    with contextlib.redirect_stdout(_stdout), contextlib.redirect_stderr(_stderr):
        exec(__forge_source, _namespace)
except Exception:
    _status = 'runtime_error'
    _stderr.write(traceback.format_exc())
if _status == 'passed':
    for _case in json.loads(__forge_tests_json):
        try:
            with contextlib.redirect_stdout(_stdout), contextlib.redirect_stderr(_stderr):
                _function = _namespace[__forge_function_name]
                _received = _function(*_case.get('args', []), **_case.get('kwargs', {}))
                if inspect.isawaitable(_received):
                    _received = await _received
            if _case.get('expected_exception'):
                _results.append({'name': _case['name'], 'passed': False, 'message': 'Expected ' + _case['expected_exception'] + ' but no exception was raised.'})
            else:
                _expected = _case.get('expected')
                _passed = _received == _expected
                _results.append({'name': _case['name'], 'passed': _passed, 'message': '' if _passed else 'Expected: ' + repr(_expected) + '; Received: ' + repr(_received)})
                if not _passed: _status = 'failed'
        except Exception as _error:
            _expected_exception = _case.get('expected_exception')
            _passed = bool(_expected_exception and type(_error).__name__ == _expected_exception)
            _results.append({'name': _case['name'], 'passed': _passed, 'message': '' if _passed else type(_error).__name__ + ': ' + str(_error)})
            if not _passed: _status = 'failed'
json.dumps({'status': _status, 'stdout': _stdout.getvalue()[:30000], 'stderr': _stderr.getvalue()[:30000], 'tests': _results})
`;

async function initialize() {
  if (pyodide) return pyodide;
  const indexURL = new URL(`${import.meta.env.BASE_URL}assets/pyodide/`, self.location.origin).href;
  pyodide = await loadPyodide({ indexURL }) as unknown as Pyodide;
  self.postMessage({ type: "ready" });
  return pyodide;
}

self.onmessage = async (event: MessageEvent<{ id: number; code: string; functionName?: string; tests: PythonTest[] }>) => {
  const started = performance.now();
  try {
    const runtime = await initialize();
    runtime.globals.set("__forge_source", event.data.code);
    runtime.globals.set("__forge_tests_json", JSON.stringify(event.data.tests));
    runtime.globals.set("__forge_function_name", event.data.functionName ?? "");
    const raw = await runtime.runPythonAsync(HARNESS);
    const result = JSON.parse(raw) as ExecutionResult;
    result.duration_ms = Math.round(performance.now() - started);
    self.postMessage({ type: "result", id: event.data.id, result });
  } catch (reason) {
    const result: ExecutionResult = {
      status: "runtime_error", stdout: "", stderr: reason instanceof Error ? reason.message : String(reason),
      tests: [], duration_ms: Math.round(performance.now() - started),
    };
    self.postMessage({ type: "result", id: event.data.id, result });
  }
};

void initialize().catch((reason: unknown) => {
  self.postMessage({ type: "init_error", message: reason instanceof Error ? reason.message : String(reason) });
});
