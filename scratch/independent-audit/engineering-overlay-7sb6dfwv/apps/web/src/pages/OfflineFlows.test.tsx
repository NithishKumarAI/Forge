import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe,it,expect,vi } from "vitest";
import { PracticePage } from "./PracticePage";
import { ReviewPage } from "./ReviewPage";
import { TutorPage } from "./TutorPage";

vi.mock("../components/AssessmentCard",()=>({AssessmentCard:()=>null}));

describe("offline study entry points",()=>{
  it("starts practice explicitly without pretending a result exists",()=>{
    const html=renderToStaticMarkup(<MemoryRouter><PracticePage/></MemoryRouter>);
    expect(html).toContain("Static practice");expect(html).toContain(">Start</button>");
    expect(html).not.toContain("100%");expect(html).not.toContain("Generate");
  });
  it("explains independent transfer and tracks help without showing a solution",()=>{
    const html=renderToStaticMarkup(<MemoryRouter><PracticePage purpose="transfer"/></MemoryRouter>);
    expect(html).toContain("Independent transfer");expect(html).toContain("Help is recorded");
    expect(html).not.toContain("reference_solution");
  });
  it("keeps manual topic access available when no recall is due",()=>{
    const html=renderToStaticMarkup(<MemoryRouter><ReviewPage/></MemoryRouter>);
    expect(html).toContain("24 elapsed hours");expect(html).toContain("No reviews are due");
    expect(html).toContain('href="/curriculum"');
  });
  it("provides local search and preserved history instead of chat generation",()=>{
    const html=renderToStaticMarkup(<MemoryRouter><TutorPage/></MemoryRouter>);
    expect(html).toContain("Search local lessons");expect(html).toContain("Read legacy conversation history");
    expect(html).not.toContain("Ask AI");expect(html).not.toContain("model selector");
  });
});
