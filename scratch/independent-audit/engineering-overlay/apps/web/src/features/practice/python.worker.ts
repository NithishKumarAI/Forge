import type { ExecutionResult, PythonTest } from "../../types/practice";
import { loadPyodide } from "pyodide";

type Pyodide = { globals: { set: (name: string, value: unknown) => void }; runPythonAsync: (code: string) => Promise<string> };
let pyodide: Pyodide | null = null;

const HARNESS = String.raw`
import contextlib, inspect, io, json, sys, time, traceback

def _typed(value):
    value_type = type(value)
    name = value_type.__name__
    if value is None or value_type in (bool, int, float, str): safe = value
    elif value_type in (list, tuple): safe = [_typed(item) for item in value]
    elif value_type is dict: safe = [{'key': _typed(key), 'value': _typed(item)} for key, item in value.items()]
    else: safe = None
    return {'type': name, 'display': repr(value)[:10000], 'value': safe}

def _from_typed(item):
    kind, value = item.get('type'), item.get('value')
    if kind == 'list': return [_from_typed(entry) for entry in value]
    if kind == 'tuple': return tuple(_from_typed(entry) for entry in value)
    if kind == 'dict': return {_from_typed(entry['key']): _from_typed(entry['value']) for entry in value}
    if kind == 'NoneType': return None
    return value

def _expected(case, stdin_mode=False):
    if stdin_mode: return case.get('expected_stdout', '')
    if case.get('expected_typed') is not None: return _from_typed(case['expected_typed'])
    return case.get('expected')

def _strict_equal(actual, expected):
    if type(actual) is not type(expected): return False
    if type(actual) in (list, tuple): return len(actual) == len(expected) and all(_strict_equal(a, e) for a, e in zip(actual, expected))
    if type(actual) is dict:
        if len(actual) != len(expected): return False
        unmatched = list(expected.items())
        for actual_key, actual_value in actual.items():
            found = next(((index, value) for index, (key, value) in enumerate(unmatched) if _strict_equal(actual_key, key)), None)
            if found is None or not _strict_equal(actual_value, found[1]): return False
            unmatched.pop(found[0])
        return not unmatched
    return actual == expected

def _normalize_stdout(value, rules):
    if rules.get('trim_trailing_whitespace', True): value = '\n'.join(line.rstrip() for line in value.splitlines())
    if rules.get('ignore_final_newline', True): value = value.rstrip('\n')
    return value

def _input_display(case, stdin_mode):
    if stdin_mode: return case.get('stdin', '')
    parts = [repr(item) for item in case.get('args', [])] + [str(key) + '=' + repr(value) for key, value in case.get('kwargs', {}).items()]
    return ', '.join(parts)

def _result(index, case, passed, expected, actual, stdout, stderr, started, error=None, line=None, message=''):
    return {'test_index': index + 1, 'name': case.get('name', 'Test ' + str(index + 1)), 'passed': passed,
        'input_display': _input_display(case, __forge_judge_mode == 'stdin_stdout'),
        'expected_value': _typed(expected), 'expected_type': type(expected).__name__,
        'actual_value': _typed(actual) if error is None else None, 'actual_type': type(actual).__name__ if error is None else 'Exception',
        'stdout': stdout[:30000], 'stderr': stderr[:30000], 'exception_type': type(error).__name__ if error else None,
        'exception_message': str(error)[:4000] if error else None, 'line_number': line,
        'duration_ms': round((time.perf_counter() - started) * 1000), 'message': message}

_tests = json.loads(__forge_tests_json)
_results, _global_stdout, _global_stderr, _status = [], io.StringIO(), io.StringIO(), 'passed'
try: _compiled = compile(__forge_source, '<learner-code>', 'exec')
except Exception as _compile_error:
    _status = 'runtime_error'; _line = getattr(_compile_error, 'lineno', None)
    for _index, _case in enumerate(_tests):
        _results.append(_result(_index, _case, False, _expected(_case, __forge_judge_mode == 'stdin_stdout'), None, '', '', time.perf_counter(), _compile_error, _line, type(_compile_error).__name__))
else:
    _namespace = {'__name__': '__forge_exercise__'}
    if __forge_judge_mode == 'function':
        try:
            with contextlib.redirect_stdout(_global_stdout), contextlib.redirect_stderr(_global_stderr): exec(_compiled, _namespace)
        except Exception as _load_error:
            _status = 'runtime_error'; _line = next((frame.lineno for frame in traceback.extract_tb(_load_error.__traceback__) if frame.filename == '<learner-code>'), None)
            for _index, _case in enumerate(_tests):
                _results.append(_result(_index, _case, False, _expected(_case), None, '', '', time.perf_counter(), _load_error, _line, type(_load_error).__name__))
    if _status == 'passed':
        for _index, _case in enumerate(_tests):
            _started, _out, _err, _actual = time.perf_counter(), io.StringIO(), io.StringIO(), None
            _expected_value = _expected(_case, __forge_judge_mode == 'stdin_stdout')
            try:
                with contextlib.redirect_stdout(_out), contextlib.redirect_stderr(_err):
                    if __forge_judge_mode == 'stdin_stdout':
                        _old_stdin = sys.stdin; sys.stdin = io.StringIO(_case.get('stdin', ''))
                        try: exec(_compiled, {'__name__': '__main__'})
                        finally: sys.stdin = _old_stdin
                        _actual = _out.getvalue(); _rules = _case.get('stdout_normalization', {})
                        _passed = _strict_equal(_normalize_stdout(_actual, _rules), _normalize_stdout(_expected_value, _rules))
                    else:
                        _function = _namespace[__forge_function_name]
                        _actual = _function(*_case.get('args', []), **_case.get('kwargs', {}))
                        if inspect.isawaitable(_actual): _actual = await _actual
                        _passed = _strict_equal(_actual, _expected_value)
                if _case.get('expected_exception'): _passed, _message = False, 'Expected ' + _case['expected_exception'] + ' but no exception was raised.'
                else: _message = '' if _passed else ('Wrong type' if type(_actual) is not type(_expected_value) else 'Wrong value')
                _results.append(_result(_index, _case, _passed, _expected_value, _actual, _out.getvalue(), _err.getvalue(), _started, message=_message))
                if not _passed: _status = 'failed'
            except Exception as _error:
                _passed = bool(_case.get('expected_exception') and type(_error).__name__ == _case['expected_exception'])
                _line = next((frame.lineno for frame in traceback.extract_tb(_error.__traceback__) if frame.filename == '<learner-code>'), None)
                _results.append(_result(_index, _case, _passed, _expected_value, None, _out.getvalue(), _err.getvalue(), _started, _error, _line, '' if _passed else type(_error).__name__))
                if not _passed: _status = 'failed'
json.dumps({'status': _status, 'stdout': _global_stdout.getvalue()[:30000], 'stderr': _global_stderr.getvalue()[:30000], 'tests': _results})
`;

async function initialize() {
  if (pyodide) return pyodide;
  const indexURL = new URL(`${import.meta.env.BASE_URL}assets/pyodide/`, self.location.origin).href;
  pyodide = await loadPyodide({ indexURL }) as unknown as Pyodide;
  self.postMessage({ type: "ready" });
  return pyodide;
}

self.onmessage = async (event: MessageEvent<{ id: number; code: string; functionName?: string; judgeMode?: "function" | "stdin_stdout"; tests: PythonTest[] }>) => {
  const started = performance.now();
  try {
    const runtime = await initialize();
    runtime.globals.set("__forge_source", event.data.code);
    runtime.globals.set("__forge_tests_json", JSON.stringify(event.data.tests));
    runtime.globals.set("__forge_function_name", event.data.functionName ?? "");
    runtime.globals.set("__forge_judge_mode", event.data.judgeMode ?? "function");
    const result = JSON.parse(await runtime.runPythonAsync(HARNESS)) as ExecutionResult;
    result.duration_ms = Math.round(performance.now() - started);
    self.postMessage({ type: "result", id: event.data.id, result });
  } catch (reason) {
    const result: ExecutionResult = { status: "runtime_error", stdout: "", stderr: reason instanceof Error ? reason.message : String(reason), tests: [], duration_ms: Math.round(performance.now() - started) };
    self.postMessage({ type: "result", id: event.data.id, result });
  }
};

void initialize().catch((reason: unknown) => self.postMessage({ type: "init_error", message: reason instanceof Error ? reason.message : String(reason) }));
