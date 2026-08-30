"use client";

import { RotateCcw, Search } from "lucide-react";

export type FilterBarProps = {
  kelasOptions: string[];
  prodiOptions: string[];
  search: string;
  selectedKelas: string;
  selectedProdi: string;
  selectedStatusNilai: string;
  selectedStatusValidasi: string;
  onSearchChange: (value: string) => void;
  onKelasChange: (value: string) => void;
  onProdiChange: (value: string) => void;
  onStatusNilaiChange: (value: string) => void;
  onStatusValidasiChange: (value: string) => void;
  onReset: () => void;
};

function SelectFilter({ label, options, value, onChange }: { label: string; options: string[]; value: string; onChange: (value: string) => void }) {
  return <select aria-label={label} className="h-10 min-w-36 flex-1 rounded-lg border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 focus:border-blue-500 sm:max-w-48 sm:flex-none" onChange={(event) => onChange(event.target.value)} value={value}><option value="">{label}</option>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select>;
}

export function FilterBar({ kelasOptions, prodiOptions, search, selectedKelas, selectedProdi, selectedStatusNilai, selectedStatusValidasi, onSearchChange, onKelasChange, onProdiChange, onStatusNilaiChange, onStatusValidasiChange, onReset }: FilterBarProps) {
  return <div className="flex flex-wrap items-center gap-2"><label className="flex h-10 min-w-full flex-1 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 text-slate-500 shadow-sm transition hover:border-slate-300 sm:min-w-56 sm:flex-none"><Search size={17} /><input className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400" onChange={(event) => onSearchChange(event.target.value)} placeholder="Cari NIM atau Nama..." type="search" value={search} /></label><SelectFilter label="Semua Kelas" onChange={onKelasChange} options={kelasOptions} value={selectedKelas} /><SelectFilter label="Semua Prodi" onChange={onProdiChange} options={prodiOptions} value={selectedProdi} /><SelectFilter label="Semua Status Nilai" onChange={onStatusNilaiChange} options={["Sudah Ada Nilai", "Belum Ada Nilai"]} value={selectedStatusNilai} /><SelectFilter label="Semua Status Validasi" onChange={onStatusValidasiChange} options={["Valid", "Perlu Dicek"]} value={selectedStatusValidasi} /><button className="flex h-10 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700" onClick={onReset} type="button"><RotateCcw size={15} />Reset</button></div>;
}
