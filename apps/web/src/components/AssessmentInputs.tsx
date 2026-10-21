import type { StaticAssessment } from "../types/assessment";
export function AssessmentInputs({item,answer,text,unit,disabled,onAnswer,onText,onUnit}:{
  item:StaticAssessment;answer:string[];text:string;unit:string;disabled:boolean;
  onAnswer:(value:string[])=>void;onText:(value:string)=>void;onUnit:(value:string)=>void;
}) {
  if(item.contract.choices)return <fieldset disabled={disabled} className="mt-5 space-y-2"><legend className="mb-2 font-semibold">{item.kind==="multi_choice"?"Select all correct answers":"Choose one answer"}</legend>
    {Object.entries(item.contract.choices).map(([key,label])=><label key={key} className="flex gap-3 rounded-xl border p-3"><input type={item.kind==="multi_choice"?"checkbox":"radio"} name={item.id} value={key} checked={answer.includes(key)} onChange={()=>onAnswer(item.kind==="single_choice"?[key]:answer.includes(key)?answer.filter(x=>x!==key):[...answer,key])}/>{label}</label>)}
  </fieldset>;
  if(item.kind==="numeric")return <div className="mt-4 flex flex-wrap gap-3"><label>Decimal answer<input disabled={disabled} inputMode="decimal" value={text} onChange={e=>onText(e.target.value)} className="mt-1 block rounded-xl border p-3"/></label><label>Units<input disabled={disabled} value={unit} onChange={e=>onUnit(e.target.value)} className="mt-1 block rounded-xl border p-3"/></label></div>;
  return null;
}
