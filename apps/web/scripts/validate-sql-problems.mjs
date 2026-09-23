import { PGlite } from "@electric-sql/pglite";
import { readdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(process.cwd(), "../../content/problem-bank/sql");
for (const file of await readdir(root)) {
  if (!file.endsWith(".json")) continue;
  const problem = JSON.parse(await readFile(resolve(root, file), "utf8"));
  const datasets = [
    { setup_sql: problem.validation.setup_sql, expected_rows: problem.validation.expected_rows },
    ...problem.validation.hidden_datasets,
  ];
  for (const dataset of datasets) {
    const db = new PGlite();
    try {
      await db.exec(dataset.setup_sql);
      const metadata = await db.query("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position");
      if (!metadata.rows.length) throw new Error(`${problem.key} schema introspection returned no columns`);
      for (const visibleTable of problem.validation.visible_tables) {
        const name = visibleTable.split("(", 1)[0].trim();
        const preview = await db.query(`SELECT * FROM "${name.replaceAll('"', '""')}" LIMIT 50`);
        if (!Array.isArray(preview.rows)) throw new Error(`${problem.key} could not preview ${name}`);
      }
      const results = await db.exec(problem.reference_solution);
      const last = results.at(-1);
      const actualColumns = (last?.fields ?? []).map((field) => field.name);
      const expectedColumns = problem.validation.expected_columns;
      if (JSON.stringify(actualColumns.map((item) => item.toLowerCase())) !== JSON.stringify(expectedColumns.map((item) => item.toLowerCase()))) {
        throw new Error(`${problem.key} columns mismatch: expected [${expectedColumns.join(", ")}], received [${actualColumns.join(", ")}]`);
      }
      const normalizeValue = (value) => typeof value === "bigint" ? Number(value) : value instanceof Date ? value.toISOString().slice(0, 10) : value;
      const actual = (last?.rows ?? []).map((row) => JSON.stringify(expectedColumns.map((column) => normalizeValue(row[column]))));
      const expected = dataset.expected_rows.map((row) => JSON.stringify(row.map(normalizeValue)));
      if (!problem.validation.order_sensitive) { actual.sort(); expected.sort(); }
      if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(`${problem.key} reference result does not match its expected rows`);
    } finally {
      await db.close();
    }
  }
  console.log(`valid: ${problem.key}`);
}
