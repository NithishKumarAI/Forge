import { PGlite } from "@electric-sql/pglite";
import { readdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = resolve(fileURLToPath(new URL(".", import.meta.url)));
export const sqlProblemRoot = resolve(scriptDirectory, "../../../content/problem-bank/sql");
const normalizeValue = (value) => typeof value === "bigint" ? Number(value) : value instanceof Date ? value.toISOString().slice(0, 10) : value;
const normalizeSql = (sql) => sql.replace(/\s+/g, " ").trim().toLowerCase();
const encoded = (rows) => rows.map((row) => JSON.stringify(row.map(normalizeValue)));

function failure(problem, dataset, message, details = {}) {
  const lines = [`${problem.key} · ${dataset}: ${message}`];
  for (const [label, value] of Object.entries(details)) lines.push(`${label}: ${JSON.stringify(value)}`);
  throw new Error(lines.join("\n"));
}

export async function validateSqlProblem(problem) {
  const validation = problem.validation ?? {};
  for (const key of ["setup_sql", "expected_columns", "expected_rows", "visible_tables", "hidden_datasets", "order_sensitive"]) {
    if (!(key in validation)) failure(problem, "contract", `missing ${key}`);
  }
  if (!validation.hidden_datasets.length) failure(problem, "contract", "at least one alternate hidden dataset is required");
  if (validation.expected_columns.some((column) => /^result_col(?:umn)?$/i.test(column))) failure(problem, "contract", "placeholder expected column name remains", { expected_columns: validation.expected_columns });
  for (const entry of validation.visible_tables) {
    const tableName = entry.split("(", 1)[0].trim();
    if (tableName.includes(",")) failure(problem, "contract", "visible_tables must contain one table per array entry", { entry });
  }
  const visibleSetup = normalizeSql(validation.setup_sql);
  validation.hidden_datasets.forEach((dataset, index) => {
    if (normalizeSql(dataset.setup_sql) === visibleSetup) failure(problem, `hidden dataset ${index + 1}`, "setup_sql is identical to visible data");
  });
  const datasets = [
    { name: "visible dataset", setup_sql: validation.setup_sql, expected_rows: validation.expected_rows },
    ...validation.hidden_datasets.map((item, index) => ({ ...item, name: item.name ?? `hidden dataset ${index + 1}` })),
  ];
  for (const dataset of datasets) {
    const db = new PGlite();
    try {
      try { await db.exec(dataset.setup_sql); }
      catch (error) { failure(problem, dataset.name, "setup_sql failed", { error: error instanceof Error ? error.message : String(error) }); }
      let metadata;
      try { metadata = await db.query("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position"); }
      catch (error) { failure(problem, dataset.name, "schema introspection failed", { error: error instanceof Error ? error.message : String(error) }); }
      const actualTables = [...new Set(metadata.rows.map((row) => String(row.table_name)))];
      const expectedTables = validation.visible_tables.map((entry) => entry.split("(", 1)[0].trim());
      const missingTables = expectedTables.filter((table) => !actualTables.includes(table));
      if (missingTables.length) failure(problem, dataset.name, "visible table is absent", { expected_tables: expectedTables, actual_tables: actualTables, missing_tables: missingTables });
      let queryResult;
      try { queryResult = (await db.exec(problem.reference_solution)).at(-1); }
      catch (error) { failure(problem, dataset.name, "reference_solution failed", { error: error instanceof Error ? error.message : String(error) }); }
      const actualColumns = (queryResult?.fields ?? []).map((field) => field.name);
      const expectedColumns = validation.expected_columns;
      if (JSON.stringify(actualColumns.map((item) => item.toLowerCase())) !== JSON.stringify(expectedColumns.map((item) => item.toLowerCase()))) {
        failure(problem, dataset.name, "returned columns do not match", { expected_columns: expectedColumns, actual_columns: actualColumns });
      }
      const actualRows = (queryResult?.rows ?? []).map((row) => actualColumns.map((column) => normalizeValue(row[column])));
      const expectedRows = dataset.expected_rows.map((row) => row.map(normalizeValue));
      const actualEncoded = encoded(actualRows), expectedEncoded = encoded(expectedRows);
      if (!validation.order_sensitive) { actualEncoded.sort(); expectedEncoded.sort(); }
      if (JSON.stringify(actualEncoded) !== JSON.stringify(expectedEncoded)) {
        failure(problem, dataset.name, "returned rows do not match", { expected_rows: expectedRows, actual_rows: actualRows });
      }
    } finally { await db.close(); }
  }
  return { key: problem.key, datasets: datasets.length };
}

export async function validateSqlFile(path) {
  return validateSqlProblem(JSON.parse(await readFile(path, "utf8")));
}

async function main() {
  const args = process.argv.slice(2);
  const problemIndex = args.indexOf("--problem"), trackIndex = args.indexOf("--track");
  if (trackIndex >= 0 && args[trackIndex + 1] !== "sql") throw new Error("SQL validator only supports --track sql");
  const requested = problemIndex >= 0 ? args[problemIndex + 1] : undefined;
  if (problemIndex >= 0 && !requested) throw new Error("--problem requires a problem key");
  const files = (await readdir(sqlProblemRoot)).filter((file) => file.endsWith(".json") && (!requested || file === `${requested}.json`)).sort();
  if (!files.length) throw new Error(requested ? `SQL problem not found: ${requested}` : "No SQL problems found");
  let datasets = 0;
  for (const file of files) {
    const result = await validateSqlFile(resolve(sqlProblemRoot, file));
    datasets += result.datasets;
    console.log(`valid: ${result.key} (${result.datasets} datasets)`);
  }
  console.log(`SQL PGlite validation: ${files.length} passed, 0 failed, ${datasets} datasets`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => { console.error(error instanceof Error ? error.message : String(error)); process.exitCode = 1; });
}
