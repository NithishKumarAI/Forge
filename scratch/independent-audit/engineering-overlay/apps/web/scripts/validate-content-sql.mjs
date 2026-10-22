// Exact candidate fixture on stdin, fresh isolated in-memory PostgreSQL database per dataset.
import { PGlite } from "@electric-sql/pglite";
import { validateSqlProblem } from "./validate-sql-problems.mjs";
let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
  if (input.length > 524288) throw new Error("SQL fixture exceeds limit");
}
const fixtures = JSON.parse(input);
const normalize = (v) => typeof v === "bigint" ? Number(v) : v instanceof Date ? v.toISOString().slice(0,10) : v;
try {
 for (const fixture of (Array.isArray(fixtures) ? fixtures : [fixtures])) {
  if (fixture.arena_problem) { await validateSqlProblem(fixture.arena_problem); continue; }
  for (const dataset of [fixture, ...(fixture.alternate_datasets ?? [])]) {
    const db = new PGlite();
    try {
      await db.exec(dataset.setup_sql);
      const result = await db.query(fixture.query);
      const columns = result.fields.map(f => f.name);
      if (JSON.stringify(columns) !== JSON.stringify(fixture.expected_columns)) throw new Error("columns mismatch");
      const encode = rows => rows.map(row => JSON.stringify(row.map(normalize)));
      const actual = encode(result.rows.map(row => columns.map(c => row[c])));
      const expected = encode(dataset.expected_rows);
      if (!fixture.order_sensitive) { actual.sort(); expected.sort(); }
      if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error("rows mismatch (including duplicates/NULL/order)");
    } finally { await db.close(); }
  }
 }
  console.log("valid SQL examples");
} catch (error) { console.error(String(error)); process.exitCode = 1; }
