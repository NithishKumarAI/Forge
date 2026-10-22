import type { SqlResult } from "./sqlRunner";

export type SqlCellDiff = { row: number; column: string; expected: unknown; actual: unknown; kind: "value" | "missing_row" | "extra_row" };
export type SqlComparison = {
  passed: boolean;
  expectedColumns: string[];
  actualColumns: string[];
  expectedRows: unknown[][];
  actualRows: unknown[][];
  columnMismatch: boolean;
  orderMismatch: boolean;
  diffs: SqlCellDiff[];
};

export function normalizeSqlValue(value: unknown): unknown {
  if (typeof value === "bigint") return Number(value);
  if (value instanceof Date) return value.toISOString().replace("T00:00:00.000Z", "");
  return value;
}

const encodedRow = (row: unknown[]) => JSON.stringify(row.map(normalizeSqlValue));

export function compareSql(result: SqlResult, expectedColumns: string[], expectedRows: unknown[][], orderSensitive: boolean): SqlComparison {
  const actualColumns = result.columns ?? [];
  const loweredActual = actualColumns.map((item) => item.toLowerCase());
  const loweredExpected = expectedColumns.map((item) => item.toLowerCase());
  const columnMismatch = !result.ok || JSON.stringify(loweredActual) !== JSON.stringify(loweredExpected);
  const actualRows = result.ok ? result.rows.map((row) => actualColumns.map((column) => normalizeSqlValue(row[column]))) : [];
  const normalizedExpected = expectedRows.map((row) => row.map(normalizeSqlValue));
  let comparedActual = actualRows;
  let comparedExpected = normalizedExpected;
  let orderMismatch = false;
  if (!orderSensitive) {
    comparedActual = [...actualRows].sort((a, b) => encodedRow(a).localeCompare(encodedRow(b)));
    comparedExpected = [...normalizedExpected].sort((a, b) => encodedRow(a).localeCompare(encodedRow(b)));
  } else if (actualRows.length === normalizedExpected.length) {
    const orderedEqual = JSON.stringify(actualRows.map(encodedRow)) === JSON.stringify(normalizedExpected.map(encodedRow));
    const unorderedEqual = JSON.stringify([...actualRows].map(encodedRow).sort()) === JSON.stringify([...normalizedExpected].map(encodedRow).sort());
    orderMismatch = !orderedEqual && unorderedEqual;
  }
  const diffs: SqlCellDiff[] = [];
  const rowCount = Math.max(comparedActual.length, comparedExpected.length);
  for (let rowIndex = 0; rowIndex < rowCount; rowIndex += 1) {
    const actual = comparedActual[rowIndex];
    const expected = comparedExpected[rowIndex];
    if (!expected) {
      diffs.push({ row: rowIndex + 1, column: "*", expected: undefined, actual, kind: "extra_row" });
      continue;
    }
    if (!actual) {
      diffs.push({ row: rowIndex + 1, column: "*", expected, actual: undefined, kind: "missing_row" });
      continue;
    }
    for (let columnIndex = 0; columnIndex < Math.max(expected.length, actual.length); columnIndex += 1) {
      if (encodedRow([expected[columnIndex]]) !== encodedRow([actual[columnIndex]])) {
        diffs.push({ row: rowIndex + 1, column: expectedColumns[columnIndex] ?? actualColumns[columnIndex] ?? `column ${columnIndex + 1}`, expected: expected[columnIndex], actual: actual[columnIndex], kind: "value" });
      }
    }
  }
  return { passed: result.ok && !columnMismatch && !orderMismatch && diffs.length === 0, expectedColumns, actualColumns, expectedRows: normalizedExpected, actualRows, columnMismatch, orderMismatch, diffs };
}
