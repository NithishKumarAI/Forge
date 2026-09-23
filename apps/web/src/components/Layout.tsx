import { BookOpen, Code2, Gauge, GraduationCap, Settings, Sparkles } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { DoubtChat } from "./DoubtChat";

const navigation = [
  { to: "/", label: "Dashboard", icon: Gauge },
  { to: "/curriculum", label: "Curriculum", icon: BookOpen },
  { to: "/arena", label: "Coding Arena", icon: Code2 },
  { to: "/review", label: "Review", icon: Sparkles },
  { to: "/interview", label: "Interview", icon: GraduationCap },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Layout() {
  return (
    <div className="min-h-screen bg-canvas lg:flex">
      <aside className="border-b border-slate-200 bg-ink px-5 py-4 text-white lg:fixed lg:inset-y-0 lg:w-64 lg:border-b-0 lg:px-6 lg:py-8">
        <NavLink to="/" className="display flex items-center gap-3 text-xl font-extrabold tracking-[.16em]"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent">F</span> FORGE</NavLink>
        <nav className="mt-5 flex gap-1 overflow-x-auto lg:mt-12 lg:block lg:space-y-2">
          {navigation.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => `flex shrink-0 items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition ${isActive ? "bg-white/12 text-white" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}>
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
        <div className="absolute bottom-8 hidden text-xs leading-5 text-slate-500 lg:block">Local-first learning<br />Forge V1</div>
      </aside>
      <main className="min-w-0 flex-1 px-5 py-8 sm:px-8 lg:ml-64 lg:px-12 lg:py-10"><Outlet /></main>
      <DoubtChat />
    </div>
  );
}
