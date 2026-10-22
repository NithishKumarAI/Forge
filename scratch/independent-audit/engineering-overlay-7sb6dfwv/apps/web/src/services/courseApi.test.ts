import { afterEach, expect, it, vi } from "vitest";
import { api } from "./api";

afterEach(() => vi.unstubAllGlobals());

it("keeps lesson revision identity in reads and progress writes", async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) });
  vi.stubGlobal("fetch", fetch);
  await api.courseTopic(7);
  await api.courseTopic(7, 42);
  await api.viewCourseSection(7, "shared-section", 42);
  await api.completeCourseSection(7, "shared-section", 43);
  expect(fetch.mock.calls.map((call) => call[0])).toEqual([
    "/api/course/topics/7",
    "/api/course/topics/7?lesson_id=42",
    "/api/course/topics/7/sections/shared-section/view?lesson_id=42",
    "/api/course/topics/7/sections/shared-section/complete?lesson_id=43",
  ]);
  expect(fetch.mock.calls[2][1].method).toBe("POST");
});
