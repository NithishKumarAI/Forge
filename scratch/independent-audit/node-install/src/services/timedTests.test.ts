import {afterEach,describe,it,expect,vi} from "vitest";
import {timedTests} from "./timedTests";
afterEach(()=>vi.unstubAllGlobals());
describe("timed test persistence API",()=>{
 it("sends the fixed blueprint selector and exact source/hash rather than client scores",async()=>{
  const fetcher=vi.fn().mockResolvedValue({ok:true,json:async()=>({id:"stable"})});vi.stubGlobal("fetch",fetcher);
  await timedTests.start("subject","python",1);
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({kind:"subject",subject:"python",level:1});
  const body={content_sha256:"exact",answer:"a",source:"def solve(x): return x+1",unit:""};
  await timedTests.draft("stable",0,body);await timedTests.answer("stable",0,body);
  expect(JSON.parse(fetcher.mock.calls[1][1].body)).toEqual({...body,position:0});
  expect(fetcher.mock.calls[2][0]).toBe("/api/timed-tests/stable/answer");
  expect(JSON.parse(fetcher.mock.calls[2][1].body)).not.toHaveProperty("score");
 });
 it("preserves the saved deadline/session route for resume and explicit completion",async()=>{
  const fetcher=vi.fn().mockResolvedValue({ok:true,json:async()=>({id:"saved",deadline_at:"2026-10-22T10:00:00Z"})});vi.stubGlobal("fetch",fetcher);
  await timedTests.read("saved");await timedTests.complete("saved");await timedTests.abandon("saved");
  expect(fetcher.mock.calls.map(call=>call[0])).toEqual(["/api/timed-tests/saved","/api/timed-tests/saved/complete","/api/timed-tests/saved/abandon"]);
 });
});
