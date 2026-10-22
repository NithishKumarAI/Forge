import ReactMarkdown from "react-markdown";

export function Markdown({ children }: { children: string }) {
  // A deliberately tiny authored disclosure syntax, rendered as React elements.
  // All other HTML remains escaped by ReactMarkdown; no raw-HTML execution plugin.
  const parts=children.split(/(<details><summary>[\s\S]*?<\/summary>[\s\S]*?<\/details>)/g);
  return (
    <div className="markdown text-sm leading-7 text-slate-700">
      {parts.map((part,index)=>{
        const disclosure=/^<details><summary>([\s\S]*?)<\/summary>([\s\S]*?)<\/details>$/.exec(part);
        return disclosure?<details key={index} className="my-3 rounded-xl border p-3"><summary className="cursor-pointer font-semibold">{disclosure[1]}</summary><div className="mt-3"><ReactMarkdown>{disclosure[2]}</ReactMarkdown></div></details>:<ReactMarkdown key={index}>{part}</ReactMarkdown>;
      })}
    </div>
  );
}
