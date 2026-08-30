"use client";

import { ArrowLeft, ChevronLeft, ChevronRight, Maximize2, RotateCcw, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { ApiRecord } from "@/types/dashboard";

export type ProblemTableProps = { rows: ApiRecord[] };

const ITEMS_PER_PAGE = 10;

export function ProblemTable({ rows }: ProblemTableProps) {
  const [search, setSearch] = useState("");
  const [jenisFilter, setJenisFilter] = useState("");
  const [kelasFilter, setKelasFilter] = useState("");

  const [currentPage, setCurrentPage] = useState(1);
  const [isFullView, setIsFullView] = useState(false);

  const columns = rows[0] ? Object.keys(rows[0]) : [];

  // Extract filter options dynamically
  const jenisOptions = useMemo(() => {
    const values = rows
      ? rows.map((r) => String(r["Jenis Masalah"] ?? r["jenis_masalah"] ?? "")).filter(Boolean)
      : [];
    return [...new Set(values)].sort();
  }, [rows]);

  const kelasOptions = useMemo(() => {
    const values = rows
      ? rows.map((r) => String(r["Kode Kelas PAI"] ?? r["kode_kelas_pai"] ?? "")).filter(Boolean)
      : [];
    return [...new Set(values)].sort();
  }, [rows]);

  // Filtering logic
  const filteredRows = useMemo(() => {
    const keyword = search.trim().toLocaleLowerCase("id-ID");
    return rows.filter((row) => {
      // Keyword search matches any value in the row
      const matchesSearch =
        !keyword ||
        Object.values(row).some(
          (val) => val !== null && String(val).toLocaleLowerCase("id-ID").includes(keyword)
        );

      const rowJenis = String(row["Jenis Masalah"] ?? row["jenis_masalah"] ?? "");
      const matchesJenis = !jenisFilter || rowJenis === jenisFilter;

      const rowKelas = String(row["Kode Kelas PAI"] ?? row["kode_kelas_pai"] ?? "");
      const matchesKelas = !kelasFilter || rowKelas === kelasFilter;

      return matchesSearch && matchesJenis && matchesKelas;
    });
  }, [rows, search, jenisFilter, kelasFilter]);

  // Reset page when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [search, jenisFilter, kelasFilter]);

  function resetFilters() {
    setSearch("");
    setJenisFilter("");
    setKelasFilter("");
    setCurrentPage(1);
  }

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / ITEMS_PER_PAGE));
  const validPage = Math.min(currentPage, totalPages);

  const displayedRows = useMemo(() => {
    if (isFullView) return filteredRows;
    const startIndex = (validPage - 1) * ITEMS_PER_PAGE;
    return filteredRows.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredRows, isFullView, validPage]);

  const startItem = filteredRows.length === 0 ? 0 : (validPage - 1) * ITEMS_PER_PAGE + 1;
  const endItem = isFullView ? filteredRows.length : Math.min(validPage * ITEMS_PER_PAGE, filteredRows.length);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
      <div className="flex flex-col gap-4">
        {/* Top Header & Action */}
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900">Data Bermasalah</h2>
              {isFullView && (
                <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-[11px] font-medium text-red-800">
                  Tampilan Penuh
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-slate-500">
              {filteredRows.length} dari {rows.length} data bermasalah yang memerlukan pengecekan
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {rows.length > 0 && (
              <button
                onClick={() => setIsFullView(!isFullView)}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-red-500/20"
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
            )}
          </div>
        </div>

        {/* Filter Controls Bar */}
        {rows.length > 0 && (
          <div className="flex flex-wrap items-center gap-2.5 rounded-xl bg-slate-50 p-2.5 border border-slate-200/80">
            {/* Search Input */}
            <div className="relative min-w-[200px] flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
              <input
                type="text"
                placeholder="Cari NIM, Nama, Keterangan..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-xs text-slate-800 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
              />
            </div>

            {/* Filter Jenis Masalah */}
            {jenisOptions.length > 0 && (
              <select
                value={jenisFilter}
                onChange={(e) => setJenisFilter(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 focus:border-red-500 focus:outline-none"
              >
                <option value="">Semua Jenis Masalah</option>
                {jenisOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            )}

            {/* Filter Kode Kelas PAI */}
            {kelasOptions.length > 0 && (
              <select
                value={kelasFilter}
                onChange={(e) => setKelasFilter(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 focus:border-red-500 focus:outline-none"
              >
                <option value="">Semua Kode Kelas</option>
                {kelasOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            )}

            {/* Reset Filter Button */}
            {(search || jenisFilter || kelasFilter) && (
              <button
                onClick={resetFilters}
                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
                type="button"
                title="Reset Filter"
              >
                <RotateCcw size={13} />
                <span>Reset</span>
              </button>
            )}
          </div>
        )}

        {/* Content */}
        {rows.length === 0 ? (
          <p className="mt-2 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-4 text-sm font-medium text-emerald-700">
            Tidak ada data bermasalah dari proses terakhir.
          </p>
        ) : filteredRows.length === 0 ? (
          <p className="px-4 py-8 text-center text-xs text-slate-500">
            Tidak ada data bermasalah yang sesuai dengan filter atau kata kunci pencarian.
          </p>
        ) : (
          <>
            {/* Table */}
            <div className="overflow-x-auto rounded-xl border border-slate-200" tabIndex={0}>
              <table className="min-w-max w-full border-collapse text-left text-xs">
                <caption className="caption-bottom px-3 pt-3 text-left text-[11px] text-slate-500">
                  Geser secara horizontal untuk melihat detail masalah.
                </caption>
                <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3.5">No</th>
                    {columns.map((column) => (
                      <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3.5" key={column}>
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {displayedRows.map((row, index) => {
                    const globalIndex = isFullView ? index + 1 : (validPage - 1) * ITEMS_PER_PAGE + index + 1;
                    return (
                      <tr
                        className="transition-colors hover:bg-red-50/40"
                        key={`${String(row.NIM ?? row.nim ?? "masalah")}-${globalIndex}`}
                      >
                        <td className="px-4 py-3 text-slate-500">{globalIndex}</td>
                        {columns.map((column) => (
                          <td className="max-w-72 px-4 py-3 align-top" key={column}>
                            {row[column] === null || row[column] === "" ? "-" : String(row[column])}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {!isFullView && (
              <div className="flex flex-col justify-between gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center">
                <p className="text-xs text-slate-500">
                  Menampilkan <span className="font-semibold text-slate-700">{startItem}</span> -{" "}
                  <span className="font-semibold text-slate-700">{endItem}</span> dari{" "}
                  <span className="font-semibold text-slate-700">{filteredRows.length}</span> data bermasalah
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
          </>
        )}
      </div>
    </section>
  );
}
