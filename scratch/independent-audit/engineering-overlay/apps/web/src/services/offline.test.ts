import { afterEach,it,expect,vi } from "vitest";
import { offline } from "./offline";
afterEach(()=>vi.unstubAllGlobals());
it("uses distinct static practice, transfer and recall contexts with exact content identity",async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({})});vi.stubGlobal("fetch",fetch);
 await offline.start(7,"practice");await offline.start(7,"transfer");await offline.start(7,"recall");
 await offline.assessment("same-selection");
 const body={content_sha256:"exact-revision-hash",answer:["a","c"],unit:"",source:""};
 await offline.submit("same-selection",body);
 expect(fetch.mock.calls.slice(0,3).map(c=>JSON.parse(c[1].body).purpose)).toEqual(["practice","transfer","recall"]);
 expect(fetch.mock.calls[3][0]).toBe("/api/assessment/same-selection");
 expect(JSON.parse(fetch.mock.calls[4][1].body)).toEqual(body);
 expect(fetch.mock.calls.some(c=>String(c[0]).includes("generate"))).toBe(false);
});
it("surfaces exhausted or missing pools instead of fabricating success",async()=>{
 vi.stubGlobal("fetch",vi.fn().mockResolvedValue({ok:false,json:async()=>({detail:"Transfer pool exhausted"})}));
 await expect(offline.start(7,"transfer")).rejects.toThrow("Transfer pool exhausted");
});
it("searches static corpus and keeps help and reveal as explicit backend actions",async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({})});vi.stubGlobal("fetch",fetch);
 await offline.search("null values",7);await offline.hint("attempt");await offline.reveal("attempt");
 expect(fetch.mock.calls.map(c=>c[0])).toEqual(["/api/guidance/search?q=null%20values&topic_id=7","/api/assessment/attempt/hint","/api/assessment/attempt/give-up"]);
});
