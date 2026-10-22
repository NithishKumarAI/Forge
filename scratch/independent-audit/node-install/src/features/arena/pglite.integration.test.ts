import {afterEach,describe,expect,it} from "vitest";
import {PGlite} from "@electric-sql/pglite";

let databases:PGlite[]=[];
const fresh=()=>{const db=new PGlite();databases.push(db);return db};
afterEach(async()=>{await Promise.all(databases.map(db=>db.close()));databases=[]});

describe("PGlite Arena isolation and inspection",()=>{
  it("introspects visible columns and rows",async()=>{const db=fresh();await db.exec("CREATE TABLE teams(id integer primary key,name text); CREATE TABLE users(id integer primary key,name text,team_id integer references teams(id)); INSERT INTO teams VALUES (1,'Core'); INSERT INTO users VALUES (7,'Ada',1);");const columns=await db.query<{table_name:string;column_name:string;data_type:string}>("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position");expect(columns.rows).toEqual(expect.arrayContaining([expect.objectContaining({table_name:"users",column_name:"team_id",data_type:"integer"})]));const rows=await db.query("SELECT * FROM users");expect(rows.rows).toEqual([{id:7,name:"Ada",team_id:1}])});
  it("executes valid SQL and reports PostgreSQL syntax errors",async()=>{const db=fresh();await db.exec("CREATE TABLE values_table(value integer); INSERT INTO values_table VALUES (2),(3)");expect((await db.query<{total:number}>("SELECT SUM(value)::int AS total FROM values_table")).rows[0].total).toBe(5);await expect(db.query("SELEKT value FROM values_table")).rejects.toThrow()});
  it("uses alternate hidden fixtures to reject a hard-coded result",async()=>{const visible=fresh();await visible.exec("CREATE TABLE users(id integer); INSERT INTO users VALUES (1),(2)");const hidden=fresh();await hidden.exec("CREATE TABLE users(id integer); INSERT INTO users VALUES (8)");expect((await visible.query("SELECT 1 AS id")).rows).toEqual([{id:1}]);expect((await hidden.query("SELECT 1 AS id")).rows).not.toEqual((await hidden.query("SELECT id FROM users")).rows)}, 20000);
  it("starts every database fresh and has no Forge SQLite catalog",async()=>{const first=fresh();await first.exec("CREATE TABLE private_attempts(id integer)");const second=fresh();const tables=await second.query<{table_name:string}>("SELECT table_name FROM information_schema.tables WHERE table_schema='public'");expect(tables.rows).toEqual([]);await expect(second.query("SELECT * FROM sqlite_master")).rejects.toThrow()});
});
