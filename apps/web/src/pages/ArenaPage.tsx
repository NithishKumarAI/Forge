import { useEffect, useState } from "react";
import {
  ArrowLeft,
  BookOpen,
  CheckCircle2,
  Clock3,
  Code2,
  Database,
  Flame,
  Layers,
  Lightbulb,
  Network,
  Play,
  RotateCcw,
  Send,
  Sparkles,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { CodeEditor } from "../components/CodeEditor";
import { Markdown } from "../components/Markdown";
import { ErrorState, LoadingState } from "../components/Status";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { runPython } from "../features/practice/pythonRunner";
import { inspectSql, runSql, type SqlResult, type SqlSchemaResult } from "../features/arena/sqlRunner";
import { compareSql, type SqlComparison } from "../features/arena/judging";
import type { ExecutionResult, PythonTest, TypedValue } from "../types/practice";
import type { ArenaStageDetail, ExerciseProgressionStage } from "../types/learningPath";

const labels = { python: "Python", sql: "SQL", dsa: "DSA" };

export function ArenaHome() {
  const routeTrack = useParams().track ?? "";
  const [activeTab, setActiveTab] = useState<"guided" | "library">("guided");
  const [selectedTrack, setSelectedTrack] = useState<string>(routeTrack);
  const [selectedStage, setSelectedStage] = useState<string>("");

  // Guided stages API
  const stagesApi = useApi(
    () => api.arenaStages(selectedTrack || undefined),
    [selectedTrack]
  );

  // Challenge Library API
  const problems = useApi(() => api.arenaProblems(), []);
  const summary = useApi(api.arenaSummary, []);
  const [libTrack, setLibTrack] = useState(routeTrack);
  const [difficulty, setDifficulty] = useState("");
  const [status, setStatus] = useState("");
  const [tag, setTag] = useState("");

  if (problems.loading || summary.loading || stagesApi.loading) return <LoadingState />;
  if (problems.error || !problems.data) return <ErrorState message={problems.error ?? "Arena unavailable"} />;

  const filteredLib = problems.data.filter(
    (p) =>
      (!libTrack || p.track === libTrack) &&
      (!difficulty || p.difficulty === difficulty) &&
      (!status || (status === "solved" ? p.solved : !p.solved)) &&
      (!tag || p.topic_tags.includes(tag))
  );
  const tags = [...new Set(problems.data.flatMap((p) => p.topic_tags))].sort();

  const stagesData = stagesApi.data ?? [];
  const filteredStages = selectedStage
    ? stagesData.filter((s) => s.key === selectedStage)
    : stagesData;

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      {/* Header */}
      <header className="border-b border-slate-200 pb-6">
        <p className="text-xs font-bold uppercase tracking-[.2em] text-accent">
          Progressive coding & independent practice
        </p>
        <h1 className="display mt-1 text-3xl font-extrabold sm:text-4xl text-slate-900">
          Coding Arena
        </h1>
        <p className="mt-2 text-slate-500">
          From First Steps to Challenging algorithms. Deterministic in-browser judging with Pyodide and PGlite.
        </p>

        {/* View Switcher: Guided Learning Path vs Challenge Library */}
        <div className="mt-6 flex flex-wrap gap-2 border-b border-slate-200 pb-px">
          <button
            type="button"
            onClick={() => setActiveTab("guided")}
            className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-bold transition ${
              activeTab === "guided"
                ? "border-accent text-accent"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Sparkles size={16} /> Guided Learning Path
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("library")}
            className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-bold transition ${
              activeTab === "library"
                ? "border-accent text-accent"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Layers size={16} /> Challenge Library (110 Problems)
          </button>
        </div>
      </header>

      {/* Track Stats Overview */}
      <section className="grid gap-4 sm:grid-cols-3">
        {(["python", "sql", "dsa"] as const).map((t) => (
          <button
            key={t}
            onClick={() => {
              setSelectedTrack(selectedTrack === t ? "" : t);
              setLibTrack(libTrack === t ? "" : t);
            }}
            className={`rounded-3xl border p-6 text-left shadow-2xs transition ${
              (activeTab === "guided" ? selectedTrack === t : libTrack === t)
                ? "border-accent bg-violet-50/40 shadow-sm"
                : "border-slate-200 bg-white hover:border-slate-300"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {t === "sql" ? (
                  <Database className="text-accent" />
                ) : t === "dsa" ? (
                  <Network className="text-accent" />
                ) : (
                  <Code2 className="text-accent" />
                )}
                <h2 className="display text-xl font-bold text-slate-900">{labels[t]}</h2>
              </div>
              <span className="text-xs font-semibold uppercase text-slate-400">
                {activeTab === "guided" ? "Track" : "All 110"}
              </span>
            </div>
            <p className="mt-4 text-2xl font-extrabold text-slate-900">
              {summary.data?.tracks[t]?.solved ?? 0} / {summary.data?.tracks[t]?.total ?? 0}
            </p>
            <p className="text-xs text-slate-500">solved independently</p>
          </button>
        ))}
      </section>

      {/* TAB 1: GUIDED LEARNING PATH */}
      {activeTab === "guided" && (
        <div className="space-y-8">
          {/* Stage filter pills */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-bold text-slate-400 uppercase">Stage:</span>
              <button
                onClick={() => setSelectedStage("")}
                className={`rounded-xl px-3.5 py-1.5 text-xs font-bold transition ${
                  !selectedStage
                    ? "bg-slate-900 text-white"
                    : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                }`}
              >
                All 5 Stages
              </button>
              {stagesData.map((s) => (
                <button
                  key={s.key}
                  onClick={() => setSelectedStage(selectedStage === s.key ? "" : s.key)}
                  className={`rounded-xl px-3.5 py-1.5 text-xs font-bold transition ${
                    selectedStage === s.key
                      ? "bg-accent text-white shadow-xs"
                      : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  {s.name} ({s.solved_count}/{s.total_count})
                </button>
              ))}
            </div>

            {selectedTrack && (
              <button
                onClick={() => setSelectedTrack("")}
                className="text-xs font-semibold text-accent hover:underline"
              >
                Clear track filter ({labels[selectedTrack as keyof typeof labels]})
              </button>
            )}
          </div>

          {/* First Steps Beginner Exercises Callout */}
          {(!selectedStage || selectedStage === "first_steps") && (
            <div className="rounded-3xl border border-emerald-200 bg-emerald-50/40 p-6 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800 uppercase tracking-wide">
                    Stage 1: First Steps
                  </span>
                  <h3 className="display mt-1 text-xl font-bold text-emerald-950">
                    Step-by-Step Beginner Exercises
                  </h3>
                  <p className="text-xs text-emerald-800">
                    Genuinely simple exercises designed for day one. Trace examples, write starter code, and receive instant feedback.
                  </p>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {[
                  { key: "py-first-print-message", title: "Print a message", track: "python", desc: "Return 'Hello, Forge!'." },
                  { key: "py-first-variable", title: "Work with one variable", track: "python", desc: "Double a number and store in result." },
                  { key: "py-first-add-two", title: "Add two numbers", track: "python", desc: "Compute a + b using the + operator." },
                  { key: "py-first-compare-two", title: "Compare two numbers", track: "python", desc: "Check if a > b returning True/False." },
                  { key: "py-first-even-odd", title: "Check even or odd", track: "python", desc: "Use modulo % 2 to classify parity." },
                  { key: "py-first-count-numbers", title: "Count positive numbers", track: "python", desc: "Accumulate loop count for x > 0." },
                  { key: "py-first-find-max", title: "Find a maximum manually", track: "python", desc: "Linear scan tracking running maximum." },
                  { key: "sql-first-select-constant", title: "SELECT a constant", track: "sql", desc: "SELECT 42 AS answer without a table." },
                  { key: "sql-first-read-one-col", title: "Read one column", track: "sql", desc: "Project the title column from books." },
                  { key: "sql-first-where", title: "Filter with WHERE", track: "sql", desc: "Filter users where is_active is true." },
                  { key: "sql-first-null-check", title: "Check for NULL", track: "sql", desc: "Use IS NULL to detect missing data." },
                  { key: "dsa-first-tracing-list", title: "Trace and sum a list", track: "dsa", desc: "Iterate and accumulate elements." },
                  { key: "dsa-first-linear-scan", title: "Linear search for index", track: "dsa", desc: "Find target index or return -1." },
                  { key: "dsa-first-freq-counting", title: "Frequency counting", track: "dsa", desc: "Build counts map in single pass." },
                ]
                  .filter((e) => !selectedTrack || e.track === selectedTrack)
                  .map((ex) => (
                    <Link
                      key={ex.key}
                      to={`/arena/exercises/${ex.key}`}
                      className="group rounded-2xl border border-emerald-200/80 bg-white p-4 shadow-2xs transition hover:border-emerald-500 hover:shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">
                          {ex.track.toUpperCase()}
                        </span>
                        <Play size={13} className="text-emerald-600 group-hover:translate-x-0.5 transition" />
                      </div>
                      <p className="mt-1 font-bold text-slate-900 group-hover:text-emerald-700">
                        {ex.title}
                      </p>
                      <p className="mt-0.5 text-xs text-slate-500">{ex.desc}</p>
                    </Link>
                  ))}
              </div>
            </div>
          )}

          {/* 5 Stages Section */}
          <div className="space-y-8">
            {filteredStages.map((stage) => (
              <section
                key={stage.key}
                className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm space-y-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded-full px-3 py-0.5 text-xs font-bold uppercase ${
                          stage.badge_color === "emerald"
                            ? "bg-emerald-100 text-emerald-800"
                            : stage.badge_color === "teal"
                            ? "bg-teal-100 text-teal-800"
                            : stage.badge_color === "blue"
                            ? "bg-blue-100 text-blue-800"
                            : stage.badge_color === "amber"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-purple-100 text-purple-800"
                        }`}
                      >
                        Stage {stage.order_index}: {stage.name}
                      </span>
                      <span className="text-xs font-semibold text-slate-400">
                        {stage.solved_count} / {stage.total_count} solved
                      </span>
                    </div>
                    <p className="mt-1.5 text-xs text-slate-500">{stage.description}</p>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {stage.problems.map((p) => (
                    <Link
                      key={p.key}
                      to={`/arena/problems/${p.key}`}
                      className="group flex items-start justify-between gap-3 rounded-2xl border border-slate-100 bg-slate-50/50 p-4 transition hover:border-violet-300 hover:bg-white hover:shadow-sm"
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-accent">
                            {labels[p.track]}
                          </span>
                          <span className="text-[11px] text-slate-400">·</span>
                          <span className="text-[11px] text-slate-500">
                            {p.estimated_minutes} min
                          </span>
                        </div>
                        <p className="mt-1 font-bold text-slate-900 group-hover:text-accent truncate">
                          {p.title}
                        </p>
                        {p.concept && (
                          <p className="mt-0.5 text-xs text-slate-500">
                            Concept: {p.concept.replace("-", " ")}
                          </p>
                        )}
                        <div className="mt-2 flex flex-wrap gap-1">
                          {p.topic_tags.slice(0, 3).map((t) => (
                            <span
                              key={t}
                              className="rounded bg-slate-200/60 px-2 py-0.5 text-[10px] text-slate-600"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>

                      {p.solved ? (
                        <CheckCircle2 size={18} className="text-emerald-600 shrink-0 mt-1" />
                      ) : (
                        <Play size={15} className="text-slate-300 group-hover:text-accent shrink-0 mt-1" />
                      )}
                    </Link>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: CHALLENGE LIBRARY (Preserved full 110-problem library) */}
      {activeTab === "library" && (
        <div className="space-y-6">
          <div className="rounded-2xl bg-slate-50 p-4 border border-slate-200 text-xs text-slate-600">
            <strong>Challenge Library Notice:</strong> Contains all 110 original problems. Unfiltered historical problems remain here for exploratory practice. All historical attempts and solved records are preserved.
          </div>

          <div className="flex flex-wrap gap-3">
            {[
              [libTrack, setLibTrack, "All tracks", ["python", "sql", "dsa"]],
              [difficulty, setDifficulty, "All difficulties", ["easy", "medium"]],
              [status, setStatus, "All statuses", ["solved", "unsolved"]],
              [tag, setTag, "All topics", tags],
            ].map(([value, setter, label, options], i) => (
              <select
                key={i}
                value={value as string}
                onChange={(e) => (setter as (v: string) => void)(e.target.value)}
                className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-2xs"
              >
                <option value="">{label as string}</option>
                {(options as string[]).map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            ))}
          </div>

          <section className="grid gap-3">
            {filteredLib.map((p) => (
              <Link
                key={p.key}
                to={`/arena/problems/${p.key}`}
                className="flex flex-wrap items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-violet-300 hover:shadow-sm"
              >
                <span
                  className={`rounded-full px-2.5 py-1 text-xs font-bold ${
                    p.difficulty === "easy"
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {p.difficulty}
                </span>
                <span className="min-w-0 flex-1">
                  <strong className="text-slate-900">{p.title}</strong>
                  <span className="ml-3 text-sm text-slate-400">
                    {labels[p.track]} · {p.topic_tags.join(", ")}
                  </span>
                </span>
                <span className="text-sm text-slate-500">{p.estimated_minutes} min</span>
                {p.solved && <CheckCircle2 className="text-emerald-600" />}
              </Link>
            ))}
          </section>
        </div>
      )}
    </div>
  );
}

function TypedBlock({ value, type }: { value: TypedValue | null; type: string }) {
  return (
    <div>
      <pre className="max-w-sm overflow-x-auto whitespace-pre-wrap font-mono text-xs">
        {value?.display ?? "Exception"}
      </pre>
      <span className="mt-1 inline-block rounded bg-slate-100 px-2 py-0.5 text-[11px] font-bold text-slate-600">
        {type}
      </span>
    </div>
  );
}

function PythonConsole({ result }: { result: ExecutionResult }) {
  const [tab, setTab] = useState<"tests" | "output" | "errors">("tests");
  const output = result.tests.map((t) => t.stdout).filter(Boolean).join("\n") || result.stdout;
  const errors = result.tests.map((t) => t.stderr).filter(Boolean).join("\n") || result.stderr;
  return (
    <section className="overflow-hidden rounded-2xl border bg-white">
      <div className="flex border-b bg-slate-50">
        {(["tests", "output", "errors"] as const).map((item) => (
          <button
            key={item}
            onClick={() => setTab(item)}
            className={`px-4 py-3 text-xs font-bold uppercase tracking-wider ${
              tab === item
                ? "border-b-2 border-accent text-accent"
                : "text-slate-500"
            }`}
          >
            {item === "tests" ? "Test Results" : item}
          </button>
        ))}
      </div>
      {tab === "tests" && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-sm">
            <thead>
              <tr className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <th className="p-3">Test</th>
                <th className="p-3">Input</th>
                <th className="p-3">Expected</th>
                <th className="p-3">Actual</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {result.tests.map((test) => (
                <tr key={`${test.test_index}-${test.name}`} className="border-t align-top">
                  <td className="p-3 font-semibold">
                    #{test.test_index}
                    <br />
                    <span className="text-xs font-normal text-slate-500">{test.name}</span>
                  </td>
                  <td className="p-3">
                    <pre className="max-w-xs whitespace-pre-wrap text-xs">
                      {test.input_display || "—"}
                    </pre>
                  </td>
                  <td className="p-3">
                    <TypedBlock value={test.expected_value} type={test.expected_type} />
                  </td>
                  <td className="p-3">
                    {test.exception_type ? (
                      <div className="text-rose-700">
                        <strong>{test.exception_type}</strong>
                        {test.line_number && <span> · line {test.line_number}</span>}
                        <p className="mt-1 text-xs">{test.exception_message}</p>
                      </div>
                    ) : (
                      <TypedBlock value={test.actual_value} type={test.actual_type} />
                    )}
                  </td>
                  <td className={`p-3 font-bold ${test.passed ? "text-emerald-700" : "text-rose-700"}`}>
                    {test.passed ? "✓ Pass" : `✗ ${test.message || "Fail"}`}
                    <div className="mt-1 text-xs font-normal text-slate-400">
                      {test.duration_ms} ms
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {tab === "output" && (
        <pre className="min-h-28 whitespace-pre-wrap p-4 text-sm">{output || "No stdout."}</pre>
      )}
      {tab === "errors" && (
        <pre className={`min-h-28 whitespace-pre-wrap p-4 text-sm ${errors ? "text-rose-700" : "text-slate-400"}`}>
          {errors || "No stderr."}
        </pre>
      )}
    </section>
  );
}

function displayCell(value: unknown) {
  if (value === null) return "NULL";
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function HtmlTable({
  columns,
  rows,
  tone = "plain",
}: {
  columns: string[];
  rows: unknown[][];
  tone?: "plain" | "expected" | "actual";
}) {
  return (
    <div
      className={`overflow-x-auto rounded-xl border ${
        tone === "expected"
          ? "border-emerald-200"
          : tone === "actual"
          ? "border-violet-200"
          : ""
      }`}
    >
      <table className="w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((c) => (
              <th key={c} className="p-2 text-left">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length ? (
            rows.map((row, i) => (
              <tr key={i} className="border-t">
                {columns.map((c, j) => (
                  <td key={c} className="p-2 font-mono text-xs">
                    {displayCell(row[j])}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={Math.max(columns.length, 1)} className="p-3 text-slate-400">
                No rows
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function SqlActual({ result }: { result: SqlResult }) {
  if (!result.ok)
    return (
      <div className="rounded-xl bg-rose-50 p-4 text-sm text-rose-800">
        <strong>{result.errorCategory ?? "PostgreSQL error"}</strong>
        <pre className="mt-2 whitespace-pre-wrap">{result.error}</pre>
      </div>
    );
  const rows = result.rows.map((row) => result.columns.map((column) => row[column]));
  return (
    <div>
      <HtmlTable columns={result.columns} rows={rows} />
      <p className="mt-2 text-xs text-slate-500">
        {rows.length} rows returned · {result.duration_ms} ms
      </p>
    </div>
  );
}

function SchemaExplorer({ schema }: { schema: SqlSchemaResult }) {
  const [tab, setTab] = useState<"schema" | "data">("schema");
  const [selected, setSelected] = useState("");
  useEffect(() => {
    if (!selected && schema.tables[0]) setSelected(schema.tables[0].name);
  }, [schema, selected]);
  if (!schema.ok)
    return <div className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{schema.error}</div>;
  const table = schema.tables.find((item) => item.name === selected) ?? schema.tables[0];
  return (
    <section className="rounded-2xl border bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="flex items-center gap-2 font-bold">
          <Database size={17} /> Database
        </h3>
        <div className="flex rounded-lg bg-slate-100 p-1">
          {(["schema", "data"] as const).map((item) => (
            <button
              key={item}
              onClick={() => setTab(item)}
              className={`rounded-md px-3 py-1.5 text-xs font-bold uppercase ${
                tab === item ? "bg-white text-accent shadow-sm" : "text-slate-500"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {schema.tables.map((item) => (
          <button
            key={item.name}
            onClick={() => setSelected(item.name)}
            className={`rounded-lg border px-3 py-2 text-sm font-semibold ${
              table?.name === item.name ? "border-accent bg-accent-soft text-accent" : ""
            }`}
          >
            {item.name}
          </button>
        ))}
      </div>
      {table && tab === "schema" && (
        <div className="mt-4 overflow-x-auto">
          <p className="mb-2 text-xs font-bold uppercase text-slate-400">
            Table: {table.name}
          </p>
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-left">
                <th className="p-2">Column</th>
                <th className="p-2">Type</th>
                <th className="p-2">Keys</th>
              </tr>
            </thead>
            <tbody>
              {table.columns.map((column) => (
                <tr key={column.name} className="border-t">
                  <td className="p-2 font-mono">{column.name}</td>
                  <td className="p-2">
                    {column.dataType}
                    {column.nullable ? " · nullable" : ""}
                  </td>
                  <td className="p-2 text-xs">
                    {column.primaryKey && (
                      <span className="mr-2 rounded bg-amber-100 px-2 py-1">PRIMARY KEY</span>
                    )}
                    {column.foreignKey && (
                      <span className="rounded bg-blue-100 px-2 py-1">
                        FK → {column.foreignKey.table}.{column.foreignKey.column}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {table && tab === "data" && (
        <div className="mt-4">
          <p className="mb-2 text-xs text-slate-500">Visible rows · limited to 50</p>
          <HtmlTable
            columns={table.columns.map((c) => c.name)}
            rows={table.rows.map((row) => table.columns.map((c) => row[c.name]))}
          />
        </div>
      )}
    </section>
  );
}

function SqlComparisonView({
  name,
  result,
  comparison,
}: {
  name: string;
  result: SqlResult;
  comparison: SqlComparison;
}) {
  return (
    <section
      className={`rounded-2xl border p-4 ${
        comparison.passed
          ? "border-emerald-200 bg-emerald-50/40"
          : "border-rose-200 bg-rose-50/30"
      }`}
    >
      <h3
        className={`font-bold ${
          comparison.passed ? "text-emerald-700" : "text-rose-700"
        }`}
      >
        {comparison.passed ? "✓" : "✗"} {name}
      </h3>
      {!result.ok ? (
        <SqlActual result={result} />
      ) : (
        <>
          <div className="mt-4 grid gap-4 xl:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-bold uppercase text-emerald-700">
                Expected result
              </p>
              <HtmlTable
                columns={comparison.expectedColumns}
                rows={comparison.expectedRows}
                tone="expected"
              />
            </div>
            <div>
              <p className="mb-2 text-xs font-bold uppercase text-accent">Your result</p>
              <HtmlTable
                columns={comparison.actualColumns}
                rows={comparison.actualRows}
                tone="actual"
              />
            </div>
          </div>
          {!comparison.passed && (
            <div className="mt-4 rounded-xl bg-white p-3 text-sm">
              <strong>Difference</strong>
              {comparison.columnMismatch && (
                <p className="mt-1 text-rose-700">
                  Columns expected [{comparison.expectedColumns.join(", ")}], received [
                  {comparison.actualColumns.join(", ")}].
                </p>
              )}
              {comparison.orderMismatch && (
                <p className="mt-1 text-rose-700">
                  Rows contain the right values but are in the wrong order.
                </p>
              )}
              {comparison.diffs.slice(0, 20).map((diff, index) => (
                <p key={index} className="mt-1 font-mono text-xs">
                  Row {diff.row} · {diff.column}: expected {JSON.stringify(diff.expected)},
                  received {JSON.stringify(diff.actual)} ({diff.kind.replaceAll("_", " ")})
                </p>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}

type SqlOutcome = { name: string; result: SqlResult; comparison: SqlComparison };

export function ArenaProblemPage() {
  const key = useParams().key!;
  const resource = useApi(() => api.arenaProblem(key), [key]);
  const [source, setSource] = useState("");
  const [busy, setBusy] = useState(false);
  const [pyResult, setPyResult] = useState<ExecutionResult | null>(null);
  const [sqlResult, setSqlResult] = useState<SqlResult | null>(null);
  const [sqlSchema, setSqlSchema] = useState<SqlSchemaResult | null>(null);
  const [sqlOutcomes, setSqlOutcomes] = useState<SqlOutcome[]>([]);
  const [message, setMessage] = useState("");
  const [hints, setHints] = useState<string[]>([]);
  const [solution, setSolution] = useState<{
    solution?: string;
    explanation?: string;
    complexity?: string;
  } | null>(null);
  const [customOpen, setCustomOpen] = useState(false);
  const [customInput, setCustomInput] = useState('{"args": [], "kwargs": {}, "expected": null}');
  const [customOutput, setCustomOutput] = useState("");

  useEffect(() => {
    const p = resource.data;
    if (!p) return;
    setSource(p.track === "sql" ? p.starter_query ?? "" : p.starter_code ?? "");
    setPyResult(null);
    setSqlResult(null);
    setSqlOutcomes([]);
  }, [resource.data?.key]);

  useEffect(() => {
    const p = resource.data;
    if (p?.track !== "sql" || !p.validation.setup_sql) return;
    void inspectSql(p.validation.setup_sql).then(setSqlSchema);
  }, [resource.data?.key]);

  if (resource.loading) return <LoadingState />;
  if (resource.error || !resource.data) return <ErrorState message={resource.error ?? "Problem not found"} />;

  const p = resource.data;
  const judgeMode = p.validation.judge_mode ?? "function";

  async function run() {
    setBusy(true);
    setMessage("");
    setSqlOutcomes([]);
    try {
      if (p.track === "sql") {
        const result = await runSql(p.validation.setup_sql ?? "", source);
        setSqlResult(result);
      } else {
        setPyResult(
          await runPython({
            code: source,
            functionName: p.validation.function_name,
            judgeMode,
            tests: p.validation.sample_tests ?? [],
            timeoutMs: p.validation.time_limit_ms,
          })
        );
      }
    } finally {
      setBusy(false);
    }
  }

  async function customTest() {
    setBusy(true);
    try {
      let test: PythonTest;
      if (judgeMode === "stdin_stdout") {
        test = { name: "Custom test", stdin: customInput, expected_stdout: customOutput };
      } else {
        const parsed = JSON.parse(customInput) as Partial<PythonTest>;
        test = {
          name: "Custom test",
          args: parsed.args ?? [],
          kwargs: parsed.kwargs ?? {},
          expected: parsed.expected,
          expected_typed: parsed.expected_typed,
        };
      }
      setPyResult(
        await runPython({
          code: source,
          functionName: p.validation.function_name,
          judgeMode,
          tests: [test],
          timeoutMs: p.validation.time_limit_ms,
        })
      );
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Invalid custom test");
    } finally {
      setBusy(false);
    }
  }

  async function submit() {
    setBusy(true);
    setMessage("");
    try {
      const saved = await api.submitArena(key, { source, content_revision_id: p.content_revision_id });
      setMessage(
        `${saved.passed ? "Passed" : "Not passed"} · ${saved.score}% · complete local worker verification`
      );
      if (saved.solution) setSolution(saved);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Submission failed");
    } finally {
      setBusy(false);
    }
  }

  async function hint() {
    const h = await api.arenaHint(key);
    setHints((x) => [...x, h.text]);
  }

  async function giveUp() {
    setSolution(await api.giveUpArena(key));
    setMessage("Gave up · no mastery evidence recorded");
  }

  function reset() {
    setSource(p.track === "sql" ? p.starter_query ?? "" : p.starter_code ?? "");
    setPyResult(null);
    setSqlResult(null);
    setSqlOutcomes([]);
    setMessage(
      p.track === "sql"
        ? "Fresh isolated database will be created on the next run."
        : "Editor reset."
    );
  }

  return (
    <div className="mx-auto max-w-7xl">
      <Link to="/arena" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500">
        <ArrowLeft size={16} /> Coding Arena
      </Link>
      <header className="mt-5">
        <div className="flex flex-wrap gap-2 text-xs font-bold">
          <span className="rounded-full bg-accent-soft px-3 py-1 text-accent">{labels[p.track]}</span>
          <span className="rounded-full bg-slate-100 px-3 py-1">{p.difficulty}</span>
          {p.topic_tags.map((t) => (
            <span key={t} className="rounded-full bg-slate-100 px-3 py-1">
              {t}
            </span>
          ))}
        </div>
        <h1 className="display mt-3 text-3xl font-extrabold">{p.title}</h1>
        <p className="mt-2 text-sm text-amber-800">
          {p.approval_status === "published"
            ? "Approved published problem"
            : "Historical unverified practice · no new approved mastery credit"}
        </p>
        <p className="mt-2 flex items-center gap-2 text-sm text-slate-500">
          <Clock3 size={15} />
          {p.estimated_minutes} minute preparation target
        </p>
      </header>
      <div className="mt-6 grid gap-5 lg:grid-cols-[.8fr_1.2fr]">
        <section className="rounded-3xl border bg-white p-6">
          <Markdown>{p.statement_markdown}</Markdown>
          <h3 className="mt-6 font-bold">Examples</h3>
          {p.examples.map((e, i) => (
            <div key={i} className="mt-2 rounded-xl bg-slate-50 p-3 text-sm">
              <code>{e.input}</code>
              <p>
                → <code>{e.output}</code>
              </p>
              {e.explanation && <p className="mt-1 text-slate-500">{e.explanation}</p>}
            </div>
          ))}
          <h3 className="mt-6 font-bold">Constraints</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
            {p.constraints.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          {p.track !== "sql" && (
            <div className="mt-6 space-y-2 rounded-xl bg-slate-50 p-4 text-sm">
              <p>
                <strong>Judge mode:</strong> {judgeMode === "function" ? "Function" : "Standard input / output"}
              </p>
              {p.validation.function_name && (
                <p>
                  <strong>Function:</strong> <code>{p.validation.function_name}(...)</code>
                </p>
              )}
              {p.validation.input_format && (
                <p>
                  <strong>Input:</strong> {p.validation.input_format}
                </p>
              )}
              {p.validation.output_format && (
                <p>
                  <strong>Output:</strong> {p.validation.output_format}
                </p>
              )}
            </div>
          )}
          <button onClick={hint} className="mt-6 flex items-center gap-2 text-sm font-semibold text-accent">
            <Lightbulb size={16} /> Reveal hint ({hints.length}/{p.hints_available})
          </button>
          {hints.map((h, i) => (
            <p key={i} className="mt-2 rounded-xl bg-amber-50 p-3 text-sm">
              {h}
            </p>
          ))}
        </section>
        <section className="space-y-4">
          {p.track === "sql" && sqlSchema && <SchemaExplorer schema={sqlSchema} />}
          <CodeEditor value={source} onChange={setSource} language={p.track === "sql" ? "sql" : "python"} />
          <div className="flex flex-wrap gap-2">
            <button
              disabled={busy}
              onClick={run}
              className="flex items-center gap-2 rounded-xl border px-4 py-2 font-semibold"
            >
              <Play size={16} /> {p.track === "sql" ? "Run Query" : "Run"}
            </button>
            <button
              disabled={busy}
              onClick={submit}
              className="flex items-center gap-2 rounded-xl bg-accent px-4 py-2 font-semibold text-white"
            >
              <Send size={16} /> Submit
            </button>
            <button
              disabled={busy}
              onClick={reset}
              className="flex items-center gap-2 rounded-xl border px-4 py-2 font-semibold"
            >
              <RotateCcw size={16} /> {p.track === "sql" ? "Reset Database" : "Reset"}
            </button>
            {p.track !== "sql" && (
              <button
                disabled={busy}
                onClick={() => setCustomOpen((value) => !value)}
                className="rounded-xl border px-4 py-2 font-semibold"
              >
                Custom Test
              </button>
            )}
            <button disabled={busy} onClick={giveUp} className="ml-auto text-sm text-slate-500">
              Give up
            </button>
          </div>
          {customOpen && p.track !== "sql" && (
            <div className="rounded-2xl border bg-slate-50 p-4">
              <h3 className="font-bold">Custom Test</h3>
              <p className="mt-1 text-xs text-slate-500">Runs locally and creates no mastery evidence.</p>
              {judgeMode === "function" ? (
                <textarea
                  value={customInput}
                  onChange={(event) => setCustomInput(event.target.value)}
                  rows={4}
                  className="mt-3 w-full rounded-xl border p-3 font-mono text-sm"
                  aria-label="Custom function test JSON"
                />
              ) : (
                <>
                  <label className="mt-3 block text-xs font-bold">STDIN</label>
                  <textarea
                    value={customInput}
                    onChange={(event) => setCustomInput(event.target.value)}
                    rows={4}
                    className="mt-1 w-full rounded-xl border p-3 font-mono text-sm"
                  />
                  <label className="mt-3 block text-xs font-bold">EXPECTED STDOUT</label>
                  <textarea
                    value={customOutput}
                    onChange={(event) => setCustomOutput(event.target.value)}
                    rows={3}
                    className="mt-1 w-full rounded-xl border p-3 font-mono text-sm"
                  />
                </>
              )}
              <button
                onClick={customTest}
                disabled={busy}
                className="mt-3 rounded-xl bg-ink px-4 py-2 text-sm font-semibold text-white"
              >
                Run Custom Test
              </button>
            </div>
          )}
          {message && <p className="rounded-xl bg-slate-100 p-3 font-semibold">{message}</p>}
          {pyResult && <PythonConsole result={pyResult} />}
          {p.track === "sql" && sqlResult && sqlOutcomes.length === 0 && (
            <section className="rounded-2xl border bg-white p-4">
              <h3 className="mb-3 font-bold">Your result</h3>
              <SqlActual result={sqlResult} />
            </section>
          )}
          {sqlOutcomes.map((item) => (
            <SqlComparisonView key={item.name} {...item} />
          ))}
          {solution && (
            <div className="rounded-2xl bg-emerald-50 p-5">
              <h3 className="font-bold">Forge solution</h3>
              <pre className="mt-3 overflow-x-auto rounded-xl bg-ink p-4 text-sm text-white">
                <code>{solution.solution}</code>
              </pre>
              <p className="mt-3 text-sm">{solution.explanation}</p>
              <p className="mt-2 text-sm font-semibold">{solution.complexity}</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
