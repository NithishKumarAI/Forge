import { afterEach, expect, it, vi } from "vitest";
import { api } from "./api";
afterEach(()=>vi.unstubAllGlobals());
it("keeps preview, preference, draft, review, confirmation and activation as separate requests",async()=>{
  const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({})});vi.stubGlobal("fetch",fetch);
  await api.edition();await api.selectEdition("placement-foundations");await api.createPlacementDraft();await api.editionReview(8);
  expect(fetch.mock.calls.some(c=>String(c[0]).endsWith("/activate"))).toBe(false);
  const review={graph_sha256:"exact-graph",scope_sha256:"exact-scope",reviewer:"Human reviewer",scope_reviewed:true,missing_content_acknowledged:true};
  await api.confirmEdition(8,review);
  expect(JSON.parse(fetch.mock.calls[4][1].body)).toEqual(review);
  expect(fetch.mock.calls.some(c=>String(c[0]).endsWith("/activate"))).toBe(false);
  await api.activateEdition(8);await api.topicEditionMetadata(42);
  expect(fetch.mock.calls.map(c=>c[0])).toEqual(["/api/editions/placement-foundations","/api/editions/placement-foundations/select","/api/editions/placement-foundations/draft","/api/editions/curricula/8/review","/api/editions/curricula/8/confirm","/api/editions/curricula/8/activate","/api/editions/topics/42"]);
});
