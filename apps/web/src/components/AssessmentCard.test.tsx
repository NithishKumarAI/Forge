import { Children,isValidElement,type ReactNode,type ReactElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe,it,expect,vi } from "vitest";
import { AssessmentCard } from "./AssessmentCard";
import { AssessmentInputs } from "./AssessmentInputs";
import { InterviewReportBody } from "./InterviewReportBody";
import type { StaticAssessment } from "../types/assessment";
// Rendering/input tests do not initialize browser workers; judge integration is tested separately.
vi.mock("../features/practice/pythonRunner",()=>({runPython:vi.fn()}));
vi.mock("../features/arena/sqlRunner",()=>({runSql:vi.fn()}));
vi.mock("./CodeEditor",()=>({CodeEditor:()=>null}));

function fixture(kind:StaticAssessment["kind"]="single_choice"):StaticAssessment {
  return {id:"immutable-attempt",session_id:1,topic_id:7,purpose:"practice",kind,prompt:"A published question",item_key:"item",content_sha256:"a".repeat(64),status:"open",approval:"approved",assisted:false,hints_used:0,hints_available:2,
    contract:kind==="numeric"?{unit:"m",rounding:"none",boundary:"inclusive"}:kind==="reflection"?{rubric:["Explain a limitation"]}:kind==="python"?{starter_code:"def solve(x): pass",sample_tests:[{name:"Public sample",args:[1],expected:2}]}:{choices:{a:"One",b:"Two"}},result:null,policy_version:"forge-evidence/2",judge_version:"forge-worker/1"};
}
function inputs(node:ReactNode):ReactElement<{onChange:(event?:unknown)=>void}>[]{
  return Children.toArray(node).flatMap(child=>!isValidElement<{children?:ReactNode}>(child)?[]:[...(child.type==="input"?[child as ReactElement<{onChange:(event?:unknown)=>void}>]:[]),...inputs(child.props.children)]);
}
const render=(item:StaticAssessment)=>renderToStaticMarkup(<AssessmentCard item={item} onChange={()=>{}}/>);

describe("objective inputs and feedback safety",()=>{
  it("uses immutable answer IDs for single choice and set selection",()=>{
    const onAnswer=vi.fn();const item=fixture();
    let tree=AssessmentInputs({item,answer:[],text:"",unit:"",disabled:false,onAnswer,onText:()=>{},onUnit:()=>{}});
    inputs(tree)[1].props.onChange();expect(onAnswer).toHaveBeenLastCalledWith(["b"]);
    item.kind="multi_choice";
    tree=AssessmentInputs({item,answer:["a"],text:"",unit:"",disabled:false,onAnswer,onText:()=>{},onUnit:()=>{}});
    inputs(tree)[1].props.onChange();expect(onAnswer).toHaveBeenLastCalledWith(["a","b"]);
    inputs(tree)[0].props.onChange();expect(onAnswer).toHaveBeenLastCalledWith([]);
  });
  it("keeps decimal numerals as strings and units explicit",()=>{
    const onText=vi.fn(),onUnit=vi.fn();const item=fixture("numeric");
    const tree=AssessmentInputs({item,answer:[],text:"1.250",unit:"m",disabled:false,onAnswer:()=>{},onText,onUnit});
    inputs(tree)[0].props.onChange({target:{value:"1.260"}});inputs(tree)[1].props.onChange({target:{value:"cm"}});
    expect(onText).toHaveBeenCalledWith("1.260");expect(onUnit).toHaveBeenCalledWith("cm");
    expect(render(item)).toContain('inputMode="decimal"');
  });
  it("separates public Run from Submit without including hidden fixtures",()=>{
    const html=render(fixture("python"));
    expect(html).toContain("Run public samples");expect(html).toContain("Submit");
    expect(html).not.toContain("reference_solution");expect(html).not.toContain("hidden_tests");
  });
  it("withholds help/reveal and per-question feedback throughout active interviews",()=>{
    const item=fixture();item.purpose="interview";
    let html=render(item);expect(html).not.toContain("Reveal hint");expect(html).not.toContain("Give up");
    item.status="complete";html=render(item);
    expect(html).toContain("after the full interview is complete");
    expect(html).not.toContain("View worked answer");expect(html).not.toContain("100%");
  });
  it("labels historical unverified practice and reflection without fake scores",()=>{
    const legacy=fixture();legacy.approval="legacy_unverified";expect(render(legacy)).toContain("Historical unverified exercise");
    const reflection=fixture("reflection");reflection.status="reflection";reflection.result={score:null,passed:false,explanation:"Authored reflection guidance"};
    const html=render(reflection);expect(html).toContain("Reflection only");expect(html).not.toContain("0%");
  });
  it("renders completed objective reports and preserves unknown historical report fields",()=>{
    const html=renderToStaticMarkup(<InterviewReportBody report={{overall_score:70,disclaimer:"Not hiring probability",questions:[{competency:"Queries",score:0,explanation:"Check duplicate rows"}]}}/>);
    expect(html).toContain("70%");expect(html).toContain("Check duplicate rows");
    const legacy=renderToStaticMarkup(<InterviewReportBody legacy report={{overall_score:62,unknown_legacy_mode:{old_feedback:"Keep this original report"}}}/>);
    expect(legacy).toContain("Keep this original report");expect(legacy).toContain("unknown_legacy_mode");
    const reflection=renderToStaticMarkup(<InterviewReportBody report={{overall_score:null,questions:[{competency:"STAR",score:null,explanation:"Consider your own contribution"}]}}/>);
    expect(reflection).toContain("unscored reflection");expect(reflection).not.toContain("0%");
  });
});
