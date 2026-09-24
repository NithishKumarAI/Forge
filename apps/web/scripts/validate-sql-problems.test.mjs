import { describe, expect, it } from "vitest";
import { validateSqlProblem } from "./validate-sql-problems.mjs";

const setup = "CREATE TABLE users(id integer primary key,name text,active boolean); INSERT INTO users VALUES (1,'Ada',true),(2,'Bo',false);";
const hidden = "CREATE TABLE users(id integer primary key,name text,active boolean); INSERT INTO users VALUES (7,'Cy',false),(8,'Dee',true);";
const valid = () => ({
  key: "fixture-sql", reference_solution: "SELECT id,name FROM users WHERE active ORDER BY id",
  validation: { setup_sql: setup, visible_tables: ["users"], expected_columns: ["id","name"], expected_rows: [[1,"Ada"]], order_sensitive: true, hidden_datasets: [{ setup_sql: hidden, expected_rows: [[8,"Dee"]] }] },
});

describe("canonical PGlite problem validation", () => {
  it("accepts a correct problem with alternate hidden data", async () => expect((await validateSqlProblem(valid())).datasets).toBe(2));
  it("rejects wrong expected columns", async () => { const p=valid();p.validation.expected_columns=["result_col","result_col"];await expect(validateSqlProblem(p)).rejects.toThrow(/placeholder expected column/) });
  it("rejects invalid setup SQL", async () => { const p=valid();p.validation.setup_sql="CREATE TABL broken";await expect(validateSqlProblem(p)).rejects.toThrow(/setup_sql failed/) });
  it("rejects an invalid reference query", async () => { const p=valid();p.reference_solution="SELEKT id FROM users";await expect(validateSqlProblem(p)).rejects.toThrow(/reference_solution failed/) });
  it("rejects wrong expected rows", async () => { const p=valid();p.validation.expected_rows=[[2,"Bo"]];await expect(validateSqlProblem(p)).rejects.toThrow(/returned rows do not match/) });
  it("rejects comma-delimited visible table entries", async () => { const p=valid();p.validation.visible_tables=["users, orders"];await expect(validateSqlProblem(p)).rejects.toThrow(/one table per array entry/) });
  it("rejects an identical hidden dataset", async () => { const p=valid();p.validation.hidden_datasets=[{setup_sql:setup,expected_rows:[[1,"Ada"]]}];await expect(validateSqlProblem(p)).rejects.toThrow(/identical to visible/) });
  it("reports missing visible tables", async () => { const p=valid();p.validation.visible_tables=["users","orders"];await expect(validateSqlProblem(p)).rejects.toThrow(/visible table is absent/) });
});
