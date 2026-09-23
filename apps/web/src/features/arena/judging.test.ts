import {describe,expect,it} from "vitest";
import {compareSql} from "./judging";
import type {SqlResult} from "./sqlRunner";

const result=(columns:string[],rows:unknown[][]):SqlResult=>({ok:true,columns,rows:rows.map(row=>Object.fromEntries(columns.map((column,index)=>[column,row[index]]))),duration_ms:2});

describe("SQL deterministic result comparison",()=>{
  it("accepts an exact result",()=>expect(compareSql(result(["name"],[["Ada"]]),["name"],[["Ada"]],true).passed).toBe(true));
  it("rejects wrong columns",()=>expect(compareSql(result(["person"],[["Ada"]]),["name"],[["Ada"]],true).columnMismatch).toBe(true));
  it("reports a wrong value",()=>expect(compareSql(result(["count"],[[3]]),["count"],[[4]],true).diffs[0]).toMatchObject({column:"count",expected:4,actual:3,kind:"value"}));
  it("reports a missing row",()=>expect(compareSql(result(["id"],[[1]]),["id"],[[1],[2]],true).diffs[0].kind).toBe("missing_row"));
  it("reports an extra row",()=>expect(compareSql(result(["id"],[[1],[2]]),["id"],[[1]],true).diffs[0].kind).toBe("extra_row"));
  it("enforces order when requested",()=>{const compared=compareSql(result(["id"],[[2],[1]]),["id"],[[1],[2]],true);expect(compared.passed).toBe(false);expect(compared.orderMismatch).toBe(true)});
  it("ignores order when permitted",()=>expect(compareSql(result(["id"],[[2],[1]]),["id"],[[1],[2]],false).passed).toBe(true));
  it("treats execution errors as failures",()=>expect(compareSql({ok:false,columns:[],rows:[],error:"syntax",duration_ms:1},["id"],[[1]],true).passed).toBe(false));
});
