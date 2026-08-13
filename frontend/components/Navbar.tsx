import { BookOpen, CalendarDays, ChevronDown, GraduationCap, Menu } from "lucide-react";

export type NavbarProps = {
  activeItem?: string;
  items?: string[];
};

const defaultItems = ["Dashboard", "Rekap Data", "Validasi", "Hasil Rekap", "Export"];

export function Navbar({ activeItem = "Dashboard", items = defaultItems }: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-20 max-w-[1440px] items-center justify-between gap-5 px-5 sm:px-8 lg:px-10">
        <div className="flex shrink-0 items-center gap-3"><div className="grid size-10 place-items-center rounded-xl bg-blue-600 text-white shadow-sm shadow-blue-600/25"><GraduationCap size={22} strokeWidth={2.3} /></div><div className="leading-tight"><p className="text-[17px] font-bold tracking-tight text-blue-700">UKKI UNESA</p><p className="mt-0.5 text-[11px] font-medium text-slate-500">TQQ Akbar</p></div></div>
        <nav className="hidden h-full items-center gap-8 lg:flex" aria-label="Navigasi utama">{items.map((item) => <button className={item === activeItem ? "h-full border-b-2 border-blue-700 text-sm font-bold text-blue-700" : "h-full text-sm font-medium text-slate-500 transition hover:text-blue-700"} key={item} type="button">{item}</button>)}</nav>
        <div className="flex items-center gap-2 sm:gap-3"><button className="hidden items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-200 sm:flex" type="button"><BookOpen size={16} /> Panduan</button><div className="hidden items-center gap-2 rounded-full border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 xl:flex"><CalendarDays size={15} /> Periode 2026</div><button className="hidden items-center gap-2 rounded-full bg-slate-100 py-1 pl-3 pr-2 text-xs font-bold text-slate-700 sm:flex" type="button">AD<span className="grid size-8 place-items-center rounded-full bg-blue-700 text-white">A</span><ChevronDown size={16} className="text-slate-500" /></button><button className="grid size-10 place-items-center rounded-lg text-slate-600 hover:bg-slate-100 lg:hidden" type="button" aria-label="Buka navigasi"><Menu size={21} /></button></div>
      </div>
    </header>
  );
}
