"use client";

import { ChevronLeft, ChevronRight, Filter, RotateCcw, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { ApiRecord } from "@/types/dashboard";

const ITEMS_PER_PAGE = 10;

export function JilidProblemTable({ rows }: { rows: ApiRecord[] }) {
  const [search, setSearch] = useState("");
  const [jenisFilter, setJenisFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  // Ambil daftar unik Jenis Masalah beserta jumlahnya
  const jenisStats = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const r of rows) {
      const val = String(r["Jenis Masalah"] ?? r["jenis_masalah"] ?? "").trim();
      if (val) {
        counts[val] = (counts[val] ?? 0) + 1;
      }
    }
    return Object.entries(counts).sort(([a], [b]) => a.localeCompare(b));
  }, [rows]);

  // Logika filter: pencarian berdasarkan NIM dan Nama, serta filter dropdown Jenis Masalah
  const filteredRows = useMemo(() => {
    const keyword = search.trim().toLowerCase();

    return rows.filter((row) => {
      // Filter Jenis Masalah
      const rowJenis = String(row["Jenis Masalah"] ?? row["jenis_masalah"] ?? "").trim();
      if (jenisFilter && rowJenis !== jenisFilter) {
        return false;
      }

      // Filter Pencarian: khusus berdasarkan NIM dan Nama
      if (keyword) {
        const nim = String(row["NIM"] ?? row["nim"] ?? "").toLowerCase();
        const nama = String(row["Nama"] ?? row["nama"] ?? "").toLowerCase();
        const matchesNim = nim.includes(keyword);
        const matchesNama = nama.includes(keyword);
        if (!matchesNim && !matchesNama) {
          return false;
        }
      }

      return true;
    });
  }, [rows, search, jenisFilter]);

  // Reset ke halaman 1 saat filter atau pencarian berubah
  useEffect(() => {
    setCurrentPage(1);
  }, [search, jenisFilter]);

  function handleReset() {
    setSearch("");
    setJenisFilter("");
    setCurrentPage(1);
  }

  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];
  const totalPages = Math.max(1, Math.ceil(filteredRows.length / ITEMS_PER_PAGE));
  const validPage = Math.min(currentPage, totalPages);
  const startIndex = (validPage - 1) * ITEMS_PER_PAGE;
  const displayedRows = filteredRows.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  const startItem = filteredRows.length === 0 ? 0 : startIndex + 1;
  const endItem = Math.min(startIndex + ITEMS_PER_PAGE, filteredRows.length);

  return (
    <div className="space-y-3">
      {/* Controls Bar: Search & Filter */}
      <div className="flex flex-wrap items-center gap-2.5 rounded-xl border border-slate-200 bg-slate-50/70 p-2.5">
        {/* Search Input: NIM dan Nama */}
        <div className="relative min-w-[220px] flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            className="w-full rounded-lg border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-xs text-slate-800 placeholder:text-slate-400 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Cari berdasarkan NIM atau Nama..."
            type="text"
            value={search}
          />
        </div>

        {/* Dropdown Filter: Jenis Masalah */}
        {jenisStats.length > 0 && (
          <div className="flex items-center gap-1.5">
            <Filter className="text-slate-400" size={14} />
            <select
              className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
              onChange={(e) => setJenisFilter(e.target.value)}
              value={jenisFilter}
            >
              <option value="">Semua Jenis Masalah ({rows.length})</option>
              {jenisStats.map(([jenis, count]) => (
                <option key={jenis} value={jenis}>
                  {jenis} ({count})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Tombol Reset Filter */}
        {(search || jenisFilter) && (
          <button
            className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            onClick={handleReset}
            title="Reset filter dan pencarian"
            type="button"
          >
            <RotateCcw size={13} />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Info Hasil Filter */}
      {(search || jenisFilter) && (
        <p className="text-xs text-slate-500">
          Ditemukan <span className="font-semibold text-slate-700">{filteredRows.length}</span> data dari total{" "}
          <span className="font-semibold text-slate-700">{rows.length}</span> data bermasalah.
        </p>
      )}

      {/* Tabel Data */}
      {filteredRows.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-xs text-slate-500">
          Tidak ada data bermasalah yang sesuai dengan filter atau kata kunci pencarian.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full border-collapse text-left text-xs">
            <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3">No</th>
                {columns.map((column) => (
                  <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3" key={column}>
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
              {displayedRows.map((row, index) => {
                const globalIndex = startIndex + index + 1;
                return (
                  <tr className="transition-colors hover:bg-red-50/40" key={`${startIndex}-${index}`}>
                    <td className="px-4 py-3 text-slate-400 font-medium">{globalIndex}</td>
                    {columns.map((column) => {
                      const value = row[column];
                      const isJenisMasalah = column === "Jenis Masalah";
                      return (
                        <td className="px-4 py-3" key={column}>
                          {isJenisMasalah && value ? (
                            <span className="inline-flex rounded-md bg-red-50 px-2 py-0.5 text-[11px] font-semibold text-red-700 border border-red-100">
                              {String(value)}
                            </span>
                          ) : value === null || value === "" ? (
                            <span className="text-slate-300">-</span>
                          ) : (
                            String(value)
                          )}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Controls (10 data per halaman) */}
      {totalPages > 1 && (
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <p className="text-xs text-slate-500">
            Menampilkan <span className="font-semibold text-slate-700">{startItem}</span> -{" "}
            <span className="font-semibold text-slate-700">{endItem}</span> dari{" "}
            <span className="font-semibold text-slate-700">{filteredRows.length}</span> data
          </p>

          <div className="flex items-center gap-1.5">
            <button
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              disabled={validPage <= 1}
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
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
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              disabled={validPage >= totalPages}
              onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
              type="button"
            >
              <span>Selanjutnya</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
