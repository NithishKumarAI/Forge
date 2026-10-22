import {renderToStaticMarkup} from "react-dom/server";
import {MemoryRouter} from "react-router-dom";
import {describe,it,expect,vi} from "vitest";
import {StudyPlanPanel} from "./StudyPlanPanel";
import {TimedReportBody} from "../pages/TimedTestPage";
import {AssessmentCard} from "./AssessmentCard";
import {Markdown} from "./Markdown";
import type {StaticAssessment} from "../types/assessment";
vi.mock("../features/practice/pythonRunner",()=>({runPython:vi.fn()}));
vi.mock("../features/arena/sqlRunner",()=>({runSql:vi.fn()}));
vi.mock("./CodeEditor",()=>({CodeEditor:()=>null}));

describe("planner, timed test and persisted draft presentation",()=>{
 it("renders authored worked-answer disclosures without enabling arbitrary HTML",()=>{
  const html=renderToStaticMarkup(<Markdown>{'<details><summary>Check the solution</summary>The result is **17**.</details><script>alert(1)</script>'}</Markdown>);
  expect(html).toContain('<details');expect(html).toContain('<summary');expect(html).toContain('<strong>17</strong>');
  expect(html).not.toContain('<script>');
 });
 it("shows net presets and honest unallocated minutes without invented tasks",()=>{
  const html=renderToStaticMarkup(<MemoryRouter><StudyPlanPanel initial={{date:"2026-10-22",timezone:"Asia/Kolkata",target_minutes:300,planned_minutes:0,unallocated_minutes:300,items:[]}}/></MemoryRouter>);
  for(const minutes of [300,360,480])expect(html).toContain(`${minutes} min`);
  expect(html).toContain("No approved activities are scheduled");expect(html).toContain("breaks are separate");
  expect(html).toContain('href="/curriculum"');expect(html).not.toContain("100%");
 });
 it("restores an exact numeric draft and hides timed help/answers",()=>{
  const item:StaticAssessment={id:"saved",session_id:1,topic_id:1,purpose:"timed",kind:"numeric",prompt:"A saved exact numeric question",item_key:"one",content_sha256:"a".repeat(64),status:"open",approval:"approved",assisted:false,hints_used:0,hints_available:1,contract:{unit:"m"},result:null,policy_version:"forge-evidence/2",judge_version:"forge-worker/1",draft:{content_sha256:"a".repeat(64),answer:"1.250",source:"",unit:"m"}};
  const html=renderToStaticMarkup(<AssessmentCard item={item} onChange={()=>{}} onDraft={async()=>{}}/>);
  expect(html).toContain('value="1.250"');expect(html).toContain("Save draft");
  expect(html).not.toContain("Reveal hint");expect(html).not.toContain("Give up");expect(html).not.toContain("worked answer");
 });
 it("renders completed score, unanswered analysis and post-test worked answers",()=>{
  const html=renderToStaticMarkup(<TimedReportBody report={{label:"Forge practice",overall_score:50,earned_points:1,maximum_points:2,completion_reason:"timeout",disclaimer:"Not an official exam or hiring probability",questions:[{position:0,subject:"python",item_key:"one",score:0,points:0,unanswered:true,explanation:"Read the frozen contract",worked_answer:"return value + 1",submitted_answer:"return 0",mistake_analysis:"Unanswered"}]}}/>);
  expect(html).toContain("50%");expect(html).toContain("Unanswered");expect(html).toContain("return value + 1");expect(html).toContain("Not an official exam");
 });
});
