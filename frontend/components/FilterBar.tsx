import { ChevronDown, Filter, Search } from "lucide-react";

export type FilterBarProps = { searchPlaceholder?: string; statusLabel?: string; classLabel?: string };

export function FilterBar({ searchPlaceholder = "Cari NIM atau Nama...", statusLabel = "Semua Status", classLabel = "Semua Kelas" }: FilterBarProps) {
  return <div className="flex flex-wrap items-center gap-2"><label className="flex h-10 min-w-56 flex-1 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 text-slate-500 sm:flex-none"><Search size={17} /><input className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400" placeholder={searchPlaceholder} type="search" /></label>{[statusLabel, classLabel].map((label) => <button className="flex h-10 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-slate-700 hover:bg-slate-50" key={label} type="button">{label}<ChevronDown className="text-slate-500" size={15} /></button>)}<button className="flex h-10 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-slate-700 hover:bg-slate-50" type="button"><Filter size={16} />Filter</button></div>;
}
