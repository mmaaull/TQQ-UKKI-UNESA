"use client";

import { ArrowLeft, ChevronLeft, ChevronRight, Maximize2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { RekapRow } from "@/types/dashboard";

import { FilterBar } from "./FilterBar";

export type RekapTableProps = { rows: RekapRow[]; title?: string; subtitle?: string };

const columns = [
  "No",
  "NIM",
  "Nama",
  "Prodi",
  "Kelas PAI",
  "Dosen Pengampu",
  "Presensi",
  "Bacaan",
  "Hafalan",
  "Evaluasi",
  "Total Nilai",
  "Abjad",
  "Status Nilai",
  "Status Validasi",
];

const ITEMS_PER_PAGE = 10;

export function RekapTable({ rows, title = "Preview Hasil Rekap", subtitle }: RekapTableProps) {
  const [search, setSearch] = useState("");
  const [kelas, setKelas] = useState("");
  const [prodi, setProdi] = useState("");
  const [statusNilai, setStatusNilai] = useState("");
  const [statusValidasi, setStatusValidasi] = useState("");

  const [currentPage, setCurrentPage] = useState(1);
  const [isFullView, setIsFullView] = useState(false);

  const kelasOptions = useMemo(
    () => [...new Set(rows.map((row) => row.kelas).filter((value) => value !== "-"))].sort(),
    [rows]
  );
  const prodiOptions = useMemo(
    () => [...new Set(rows.map((row) => row.prodi).filter((value) => value !== "-"))].sort(),
    [rows]
  );

  const filteredRows = useMemo(() => {
    const keyword = search.trim().toLocaleLowerCase("id-ID");
    return rows.filter(
      (row) =>
        (!keyword ||
          row.nim.toLocaleLowerCase("id-ID").includes(keyword) ||
          row.nama.toLocaleLowerCase("id-ID").includes(keyword)) &&
        (!kelas || row.kelas === kelas) &&
        (!prodi || row.prodi === prodi) &&
        (!statusNilai || row.status === statusNilai) &&
        (!statusValidasi || row.validasi === statusValidasi)
    );
  }, [kelas, prodi, rows, search, statusNilai, statusValidasi]);

  // Reset ke halaman 1 saat filter/pencarian berubah
  useEffect(() => {
    setCurrentPage(1);
  }, [search, kelas, prodi, statusNilai, statusValidasi]);

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / ITEMS_PER_PAGE));
  const validPage = Math.min(currentPage, totalPages);

  const displayedRows = useMemo(() => {
    if (isFullView) return filteredRows;
    const startIndex = (validPage - 1) * ITEMS_PER_PAGE;
    return filteredRows.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredRows, isFullView, validPage]);

  function resetFilters() {
    setSearch("");
    setKelas("");
    setProdi("");
    setStatusNilai("");
    setStatusValidasi("");
    setCurrentPage(1);
  }

  const startItem = filteredRows.length === 0 ? 0 : (validPage - 1) * ITEMS_PER_PAGE + 1;
  const endItem = isFullView ? filteredRows.length : Math.min(validPage * ITEMS_PER_PAGE, filteredRows.length);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
      <div className="flex flex-col gap-4">
        {/* Top Header & Actions */}
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900">{title}</h2>
              {isFullView && (
                <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-[11px] font-medium text-blue-800">
                  Tampilan Penuh
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-slate-500">
              {filteredRows.length} dari {rows.length} hasil{subtitle ? ` • ${subtitle}` : ""}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <FilterBar
              kelasOptions={kelasOptions}
              onKelasChange={setKelas}
              onProdiChange={setProdi}
              onReset={resetFilters}
              onSearchChange={setSearch}
              onStatusNilaiChange={setStatusNilai}
              onStatusValidasiChange={setStatusValidasi}
              prodiOptions={prodiOptions}
              search={search}
              selectedKelas={kelas}
              selectedProdi={prodi}
              selectedStatusNilai={statusNilai}
              selectedStatusValidasi={statusValidasi}
            />

            <button
              onClick={() => setIsFullView(!isFullView)}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              type="button"
            >
              {isFullView ? (
                <>
                  <ArrowLeft size={14} />
                  <span>Kembali</span>
                </>
              ) : (
                <>
                  <Maximize2 size={14} />
                  <span>Tampilkan Semua Data</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto rounded-xl border border-slate-200" tabIndex={0}>
          <table className="min-w-[1300px] w-full border-collapse text-left text-xs">
            <caption className="caption-bottom px-3 pt-3 text-left text-[11px] text-slate-500">
              Geser secara horizontal untuk melihat seluruh kolom tabel.
            </caption>
            <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              <tr>
                {columns.map((label) => (
                  <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3.5" key={label}>
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
              {filteredRows.length === 0 ? (
                <tr>
                  <td className="px-4 py-10 text-center text-sm text-slate-500" colSpan={columns.length}>
                    Tidak ada data rekap yang sesuai dengan filter. Ubah atau reset filter untuk menampilkan data.
                  </td>
                </tr>
              ) : (
                displayedRows.map((row, index) => {
                  const globalIndex = isFullView ? index + 1 : (validPage - 1) * ITEMS_PER_PAGE + index + 1;
                  return (
                    <tr className="transition-colors hover:bg-blue-50/50" key={`${row.nim}-${row.kelas}-${globalIndex}`}>
                      <td className="px-4 py-3 text-slate-500">{globalIndex}</td>
                      <td className="px-4 py-3 font-medium">{row.nim}</td>
                      <td className="px-4 py-3 font-semibold text-slate-900">{row.nama}</td>
                      <td className="max-w-40 truncate px-4 py-3 text-slate-500">{row.prodi}</td>
                      <td className="px-4 py-3">{row.kelas}</td>
                      <td className="max-w-40 truncate px-4 py-3 text-slate-500">{row.dosen}</td>
                      <td className="px-4 py-3 text-right">{row.presensi || "-"}</td>
                      <td className="px-4 py-3 text-right">{row.bacaan || "-"}</td>
                      <td className="px-4 py-3 text-right">{row.hafalan || "-"}</td>
                      <td className="px-4 py-3 text-right">{row.evaluasi || "-"}</td>
                      <td className="px-4 py-3 text-right font-bold">{row.total}</td>
                      <td className="px-4 py-3 text-center font-bold">{row.abjad}</td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-[10px] font-bold ${
                            row.status === "Sudah Ada Nilai"
                              ? "bg-emerald-100 text-emerald-700"
                              : "bg-amber-100 text-amber-700"
                          }`}
                        >
                          {row.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 text-[10px] font-bold ${
                            row.validasi === "Valid"
                              ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                              : "border-red-300 bg-red-50 text-red-600"
                          }`}
                        >
                          {row.validasi}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer Controls */}
        {!isFullView && filteredRows.length > 0 && (
          <div className="flex flex-col justify-between gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center">
            <p className="text-xs text-slate-500">
              Menampilkan <span className="font-semibold text-slate-700">{startItem}</span> -{" "}
              <span className="font-semibold text-slate-700">{endItem}</span> dari{" "}
              <span className="font-semibold text-slate-700">{filteredRows.length}</span> data
            </p>

            <div className="flex items-center gap-1.5">
              <button
                disabled={validPage <= 1}
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                type="button"
              >
                <ChevronLeft size={14} />
                <span>Sebelumnya</span>
              </button>

              <div className="flex items-center gap-1 px-2">
                <span className="text-xs font-medium text-slate-700">
                  Halaman <span className="font-bold text-slate-900">{validPage}</span> dari{" "}
                  <span className="font-bold text-slate-900">{totalPages}</span>
                </span>
              </div>

              <button
                disabled={validPage >= totalPages}
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                type="button"
              >
                <span>Selanjutnya</span>
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
