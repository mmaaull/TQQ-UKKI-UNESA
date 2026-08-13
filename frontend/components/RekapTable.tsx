"use client";

import { useMemo, useState } from "react";

import type { RekapRow } from "@/types/dashboard";

import { FilterBar } from "./FilterBar";

export type RekapTableProps = { rows: RekapRow[]; title?: string; subtitle?: string };

const columns = ["No", "NIM", "Nama", "Prodi", "Kelas PAI", "Dosen Pengampu", "Presensi", "Bacaan", "Hafalan", "Evaluasi", "Total Nilai", "Abjad", "Status Nilai", "Status Validasi"];

export function RekapTable({ rows, title = "Preview Hasil Rekap", subtitle }: RekapTableProps) {
  const [search, setSearch] = useState("");
  const [kelas, setKelas] = useState("");
  const [prodi, setProdi] = useState("");
  const [statusNilai, setStatusNilai] = useState("");
  const [statusValidasi, setStatusValidasi] = useState("");

  const kelasOptions = useMemo(() => [...new Set(rows.map((row) => row.kelas).filter((value) => value !== "-"))].sort(), [rows]);
  const prodiOptions = useMemo(() => [...new Set(rows.map((row) => row.prodi).filter((value) => value !== "-"))].sort(), [rows]);
  const filteredRows = useMemo(() => {
    const keyword = search.trim().toLocaleLowerCase("id-ID");
    return rows.filter((row) => (!keyword || row.nim.toLocaleLowerCase("id-ID").includes(keyword) || row.nama.toLocaleLowerCase("id-ID").includes(keyword)) && (!kelas || row.kelas === kelas) && (!prodi || row.prodi === prodi) && (!statusNilai || row.status === statusNilai) && (!statusValidasi || row.validasi === statusValidasi));
  }, [kelas, prodi, rows, search, statusNilai, statusValidasi]);

  function resetFilters() {
    setSearch("");
    setKelas("");
    setProdi("");
    setStatusNilai("");
    setStatusValidasi("");
  }

  return <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6"><div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center"><div><h2 className="text-base font-semibold text-slate-900">{title}</h2><p className="mt-1 text-xs text-slate-500">{filteredRows.length} dari {rows.length} hasil{subtitle ? ` • ${subtitle}` : ""}</p></div><FilterBar kelasOptions={kelasOptions} onKelasChange={setKelas} onProdiChange={setProdi} onReset={resetFilters} onSearchChange={setSearch} onStatusNilaiChange={setStatusNilai} onStatusValidasiChange={setStatusValidasi} prodiOptions={prodiOptions} search={search} selectedKelas={kelas} selectedProdi={prodi} selectedStatusNilai={statusNilai} selectedStatusValidasi={statusValidasi} /></div><div className="mt-5 overflow-x-auto rounded-xl border border-slate-200" tabIndex={0}><table className="min-w-[1300px] w-full border-collapse text-left text-xs"><caption className="caption-bottom px-3 pt-3 text-left text-[11px] text-slate-500">Geser secara horizontal untuk melihat seluruh kolom tabel.</caption><thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500"><tr>{columns.map((label) => <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3.5" key={label}>{label}</th>)}</tr></thead><tbody className="divide-y divide-slate-100 bg-white text-slate-700">{filteredRows.length === 0 ? <tr><td className="px-4 py-10 text-center text-sm text-slate-500" colSpan={columns.length}>Tidak ada data rekap yang sesuai dengan filter. Ubah atau reset filter untuk menampilkan data.</td></tr> : filteredRows.map((row, index) => <tr className="transition-colors hover:bg-blue-50/50" key={`${row.nim}-${row.kelas}`}><td className="px-4 py-3">{index + 1}</td><td className="px-4 py-3 font-medium">{row.nim}</td><td className="px-4 py-3 font-semibold text-slate-900">{row.nama}</td><td className="max-w-40 truncate px-4 py-3 text-slate-500">{row.prodi}</td><td className="px-4 py-3">{row.kelas}</td><td className="max-w-40 truncate px-4 py-3 text-slate-500">{row.dosen}</td><td className="px-4 py-3 text-right">{row.presensi || "-"}</td><td className="px-4 py-3 text-right">{row.bacaan || "-"}</td><td className="px-4 py-3 text-right">{row.hafalan || "-"}</td><td className="px-4 py-3 text-right">{row.evaluasi || "-"}</td><td className="px-4 py-3 text-right font-bold">{row.total}</td><td className="px-4 py-3 text-center font-bold">{row.abjad}</td><td className="px-4 py-3 text-center"><span className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-[10px] font-bold ${row.status === "Sudah Ada Nilai" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>{row.status}</span></td><td className="px-4 py-3 text-center"><span className={`inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 text-[10px] font-bold ${row.validasi === "Valid" ? "border-emerald-300 bg-emerald-50 text-emerald-700" : "border-red-300 bg-red-50 text-red-600"}`}>{row.validasi}</span></td></tr>)}</tbody></table></div></section>;
}
