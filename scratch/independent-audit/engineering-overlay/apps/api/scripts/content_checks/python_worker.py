"""Standalone restricted teaching-code interpreter, launched with -I -S.

Only a deliberately small Python subset is executable. Unsupported examples require
context/manual review, never an unrestricted fallback. No learner/runtime imports.
"""
import ast
import builtins
import contextlib
import io
import json
import sys
from types import SimpleNamespace

_EXPORTS = {
    "math": "acos acosh asin asinh atan atan2 atanh ceil comb copysign cos cosh degrees dist e erf erfc exp expm1 fabs factorial floor fmod frexp fsum gamma gcd hypot inf isclose isfinite isinf isnan isqrt lcm ldexp lgamma log log10 log1p log2 modf nan nextafter perm pi pow prod radians remainder sin sinh sqrt tan tanh tau trunc ulp",
    "collections": "Counter defaultdict deque namedtuple OrderedDict ChainMap",
    "heapq": "heapify heappop heappush heappushpop heapreplace merge nlargest nsmallest",
    "itertools": "accumulate chain combinations combinations_with_replacement compress count cycle dropwhile filterfalse groupby islice pairwise permutations product repeat starmap takewhile tee zip_longest",
    "functools": "cache cached_property cmp_to_key lru_cache partial reduce",
    "bisect": "bisect bisect_left bisect_right insort insort_left insort_right",
    "statistics": "mean fmean geometric_mean harmonic_mean median median_low median_high mode multimode pstdev pvariance stdev variance quantiles",
    "re": "compile escape findall finditer fullmatch match search split sub subn A ASCII I IGNORECASE M MULTILINE S DOTALL X VERBOSE",
    "string": "ascii_letters ascii_lowercase ascii_uppercase digits hexdigits octdigits punctuation whitespace printable",
    "json": "dump dumps load loads JSONDecoder JSONEncoder JSONDecodeError",
}
# Real modules often export sys/os or powerful Formatter helpers. Never return
# a module object to candidate code, including through from-import statements.
MODULES = {name: SimpleNamespace(**{key: getattr(__import__(name), key) for key in names.split()}) for name, names in _EXPORTS.items()}
SAFE_NAMES = "abs all any bin bool bytearray bytes callable chr classmethod dict divmod enumerate Exception filter float frozenset hash IndexError int isinstance issubclass iter KeyError len list map max min next object ord pow print property range repr reversed round set slice sorted staticmethod StopIteration str sum super tuple TypeError ValueError zip".split()


def memory_bound():
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes as w
        class Basic(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64), ("flags", w.DWORD),
                        ("min_working", ctypes.c_size_t), ("max_working", ctypes.c_size_t), ("active", w.DWORD),
                        ("affinity", ctypes.c_size_t), ("priority", w.DWORD), ("scheduling", w.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]
        class Extended(ctypes.Structure):
            _fields_ = [("basic", Basic), ("io", IO), ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                        ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.restype = w.HANDLE
        kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        kernel.GetCurrentProcess.restype = w.HANDLE
        job = kernel.CreateJobObjectW(None, None)
        limits = Extended()
        limits.basic.flags = 0x100 | 0x8  # process memory + active-process limit
        limits.basic.active = 1
        limits.process_memory = 256 * 1024 * 1024
        if not job or not kernel.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not kernel.AssignProcessToJobObject(job, kernel.GetCurrentProcess()):
            raise RuntimeError("Cannot establish Windows validation memory/process limit")
    else:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (3, 3))


def checked_tree(code):
    if len(code) > 30000:
        raise ValueError("Executable content is too large")
    tree = ast.parse(code)
    banned = {"open", "eval", "exec", "compile", "getattr", "setattr", "delattr", "globals", "locals", "vars", "breakpoint", "help", "memoryview", "type"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and (node.id in banned or node.id.startswith("__") and node.id != "__name__"):
            raise ValueError("Unsupported executable name")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_") and not (isinstance(node.value, ast.Name) and node.value.id == "self" and not node.attr.startswith("__")):
            raise ValueError("Private/introspection attributes are unsupported")
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name.startswith("__") and node.name != "__init__":
            raise ValueError("Unsupported special method")
        if isinstance(node, ast.Import) and any(a.name not in MODULES for a in node.names):
            raise ValueError("Import is outside the teaching-code allowlist")
        if isinstance(node, ast.ImportFrom) and (node.module not in MODULES or node.level or any(a.name.startswith("_") or a.name == "*" for a in node.names)):
            raise ValueError("Import is outside the teaching-code allowlist")
    return tree


def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name not in MODULES or level:
        raise PermissionError("Import denied")
    return MODULES[name]


class Output(io.StringIO):
    def write(self, value):
        if self.tell() + len(value) > 64000:
            raise ValueError("Example output exceeds limit")
        return super().write(value)


def typed(value):
    if type(value) in (list, tuple):
        return {"type": type(value).__name__, "value": [typed(x) for x in value]}
    if type(value) is dict:
        return {"type": "dict", "value": [{"key": typed(k), "value": typed(v)} for k, v in value.items()]}
    if type(value) not in (str, bool, int, float, type(None)):
        raise ValueError("Unsupported returned type")
    return {"type": type(value).__name__, "value": value}


def execute(request):
    code = request["code"]
    tree = checked_tree(code)
    safe = {k: getattr(builtins, k) for k in SAFE_NAMES}
    safe.update({"__build_class__": builtins.__build_class__, "__import__": restricted_import})
    namespace = {"__builtins__": safe, "__name__": "__main__"}
    output = Output()
    input_stream = io.StringIO(request.get("stdin", ""))
    def read_input(prompt=""):
        output.write(str(prompt))
        line = input_stream.readline()
        if line == "":
            raise EOFError("Example requires explicit stdin")
        if line.endswith("\n"):
            line = line[:-1]
            if line.endswith("\r"):
                line = line[:-1]
        return line
    safe["input"] = read_input
    counter = 0
    def trace(frame, event, arg):
        nonlocal counter
        counter += 1
        if counter > 200000:
            raise TimeoutError("Instruction budget exceeded")
        return trace
    def audit(event, args):
        if event == "open" or event.startswith(("socket.", "subprocess.", "os.", "ctypes.")):
            raise PermissionError("Filesystem/network/process access denied")
    # Compile before audit; execution uses only our restricted namespace.
    compiled = compile(tree, "<content-example>", "exec")
    sys.addaudithook(audit)
    result = None
    exception = None
    sys.settrace(trace)
    try:
        with contextlib.redirect_stdout(output):
            exec(compiled, namespace)
            if request.get("function_name"):
                result = namespace[request["function_name"]](*request.get("args", []), **request.get("kwargs", {}))
    except Exception as error:
        exception = type(error).__name__
    finally:
        sys.settrace(None)
    return {"stdout": output.getvalue(), "returned": typed(result), "exception": exception}


if __name__ == "__main__":
    try:
        request = json.loads(sys.stdin.read(262144))
        memory_bound()
        print(json.dumps(execute(request), allow_nan=False))
    except Exception as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)
