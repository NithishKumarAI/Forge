import ReactMarkdown from "react-markdown";

export function Markdown({ children }: { children: string }) {
  return (
    <div className="markdown text-sm leading-7 text-slate-700">
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  );
}
