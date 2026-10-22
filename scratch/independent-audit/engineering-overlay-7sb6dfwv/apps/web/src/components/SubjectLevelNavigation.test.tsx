import { Children, isValidElement, type ReactNode, type ReactElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { SubjectLevelNavigation } from "./SubjectLevelNavigation";
import type { EditionOverview, EditionTopic } from "../types/editions";

const keys = ["quantitative-aptitude","logical-reasoning","verbal-english","python","sql-postgresql","dsa","system-design","ai-fundamentals","interview-communication"];
function topic(subject: string, level: number): EditionTopic {
  return {id:level,key:`${subject}-${level}`,subject_key:subject,title:`${subject} topic ${level}`,description:"A practical topic",level,
    prerequisites:level===2 ? [`${subject}-1`] : [],estimated_minutes:30,priority:100,learning_outcomes:["Explain the concept"],coverage_requirements:["Worked example"],assessment_route:"coding",content_key:`forge/placement-foundations/${subject}/${subject}-${level}`,
    availability:{lesson_status:"planned",lesson_count:0,approved_lesson_count:0,legacy_lesson_count:0,practice_available:false,approved_practice_available:false,course_exercise_count:0,arena_count:0,completed_sections:0,total_sections:0,reading_percent:0}};
}
function overview(confirmed=false): EditionOverview {
  return {edition:{key:"placement-foundations",label:"Forge V1",name:"Placement Foundations",description:"",levels:[1,2,3],status:"preparing",subjects:keys},active_curriculum_id:99,
    binding:confirmed ? {curriculum_id:7,name:"Foundations",version:1,status:"confirmed",graph_sha256:"hash",reviewed_by:"Reviewer",is_active:false} : null,
    subjects:keys.map(key=>({key,name:key,description:"Subject description",priority:100,icon:"code",topics:[1,2,3].map(level=>topic(key,level))}))};
}
function markup(data: EditionOverview, subjectKey="python",level=1) {
  return renderToStaticMarkup(<MemoryRouter><SubjectLevelNavigation overview={data} subjectKey={subjectKey} level={level} onSubjectChange={()=>{}} onLevelChange={()=>{}}/></MemoryRouter>);
}
function buttons(node: ReactNode): ReactElement<{onClick:()=>void;children:ReactNode}>[] {
  return Children.toArray(node).flatMap(child=>!isValidElement<{children?:ReactNode}>(child) ? [] :
    [...(child.type==="button" ? [child as ReactElement<{onClick:()=>void;children:ReactNode}>] : []),...buttons(child.props.children)]);
}

describe("subject and numeric level navigation",()=>{
  it("offers all nine subjects and filters the chosen subject to Level 2",()=>{
    const html=markup(overview(),"sql-postgresql",2);
    for(const key of keys) expect(html).toContain(key);
    expect(html).toContain("sql-postgresql topic 2</h3>");
    expect(html).not.toContain("sql-postgresql topic 1</h3>");
    expect(html).not.toContain("python topic 2</h3>");
    expect(html).toContain('aria-label="Learning level"');
    expect(html).toContain("recommendations, not access locks");
  });
  it("dispatches subject and level choices to the controlling route",()=>{
    const subject=vi.fn(),level=vi.fn();
    const tree=SubjectLevelNavigation({overview:overview(),subjectKey:"python",level:1,onSubjectChange:subject,onLevelChange:level});
    const choices=buttons(tree);
    expect(choices).toHaveLength(12);
    choices[4].props.onClick(); choices[10].props.onClick();
    expect(subject).toHaveBeenCalledWith("sql-postgresql");
    expect(level).toHaveBeenCalledWith(2);
    expect(markup(overview(),subject.mock.calls[0][0],level.mock.calls[0][0])).toContain("sql-postgresql topic 2</h3>");
  });
  it("shows an honest preview without inventing lesson or practice links",()=>{
    const html=markup(overview());
    expect(html).toContain("Planned · content not published");
    expect(html).toContain("No approved practice available");
    expect(html).toContain("Scope preview");
    expect(html).not.toContain('href="/topics/');
  });
  it("keeps planned confirmed topics manually accessible without level locks",()=>{
    const html=markup(overview(true),"python",3);
    expect(html).toContain('href="/topics/3"');
    expect(html).not.toContain('href="/topics/3/learn"');
    expect(html).not.toContain('href="/topics/3/practice"');
  });
  it("displays revision-scoped reading and legacy availability without approval claims",()=>{
    const data=overview(true),available=data.subjects[3].topics[0].availability;
    Object.assign(available,{lesson_status:"legacy",lesson_count:1,legacy_lesson_count:1,practice_available:true,course_exercise_count:2,completed_sections:1,total_sections:4,reading_percent:25});
    const html=markup(data);
    expect(html).toContain("Legacy lesson · not fully verified");
    expect(html).toContain("Legacy practice available");
    expect(html).toContain('value="25" max="100"');
    expect(html).toContain('href="/topics/1/learn"');
    expect(html).toContain('href="/topics/1/practice"');
    expect(html).not.toContain("Approved lesson available");
    available.lesson_status="approved";available.approved_lesson_count=1;available.approved_practice_available=true;
    expect(markup(data)).toContain("Approved lesson available");
    expect(markup(data)).toContain("Approved practice available");
  });
  it("does not present a future edition as a functioning topic catalogue",()=>{
    const data=overview();data.subjects=[];data.edition.key="advanced-engineering";data.edition.status="future";
    expect(markup(data)).toContain("No subject scope is available yet");
    expect(markup(data)).not.toContain('href="/topics/');
  });
});
