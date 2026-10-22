// Fresh isolated PostgreSQL/WASM database per fixture. No Forge database access.
import { PGlite } from "../../../web/node_modules/@electric-sql/pglite/dist/index.js";
let input="";
for await(const chunk of process.stdin){input+=chunk;if(input.length>524288)throw Error("Input too large");}
const {source,contract}=JSON.parse(input);
let passed=0;
const normal=v=>typeof v==="bigint"?String(v):v instanceof Date?v.toISOString():v;
const encode=rows=>rows.map(row=>JSON.stringify(row.map(normal)));
try {
 for(const dataset of contract.datasets){
  const db=new PGlite();
  try{
   await db.exec(dataset.setup_sql);
   await db.exec("SET statement_timeout='3000ms'; SET timezone='UTC'; BEGIN READ ONLY;");
   let result;
   try { result=await db.query(source); }
   catch { console.log(JSON.stringify({passed:0,total:contract.datasets.length,status:"verified",error:"Query failed or exceeded its allowed contract"})); process.exit(0); }
   const columns=result.fields.map(f=>f.name);
   const actual=encode(result.rows.map(row=>columns.map(c=>row[c]))),expected=encode(dataset.expected_rows);
   if(!contract.ordered){actual.sort();expected.sort();}
   if(JSON.stringify(columns)===JSON.stringify(contract.columns)&&JSON.stringify(actual)===JSON.stringify(expected))passed++;
  }finally{await db.close();}
 }
 console.log(JSON.stringify({passed,total:contract.datasets.length,status:"verified"}));
}catch(error){console.log(JSON.stringify({status:"unverified",reason:"SQL fixture/runtime unavailable; no mastery credit"}));}
