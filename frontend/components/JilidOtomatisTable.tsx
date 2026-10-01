"use client";

import { ChevronLeft, ChevronRight, RotateCcw, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { ApiRecord } from "@/types/dashboard";

const ITEMS_PER_PAGE = 10;

export function JilidOtomatisTable({ rows }: { rows: ApiRecord[] }) {
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const filteredRows = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    if (!keyword) return rows;

    return rows.filter((row) => {
      const nim = String(row["NIM"] ?? row["nim"] ?? "").toLowerCase();
      const nama = String(row["Nama"] ?? row["nama"] ?? "").toLowerCase();
      return nim.includes(keyword) || nama.includes(keyword);
    });
  }, [rows, search]);

  useEffect(() => {
    setCurrentPage(1);
  }, [search]);

  function handleReset() {
    setSearch("");
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
      {/* Controls Bar: Search */}
      <div className="flex flex-wrap items-center gap-2.5 rounded-xl border border-slate-200 bg-slate-50/70 p-2.5">
        <div className="relative min-w-[220px] flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            className="w-full rounded-lg border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-xs text-slate-800 placeholder:text-slate-400 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Cari berdasarkan NIM atau Nama..."
            type="text"
            value={search}
          />
        </div>

        {search && (
          <button
            className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            onClick={handleReset}
            title="Reset pencarian"
            type="button"
          >
            <RotateCcw size={13} />
            <span>Reset</span>
          </button>
        )}
      </div>

      {search && (
        <p className="text-xs text-slate-500">
          Ditemukan <span className="font-semibold text-slate-700">{filteredRows.length}</span> data dari total{" "}
          <span className="font-semibold text-slate-700">{rows.length}</span> peserta otomatis Jilid 1.
        </p>
      )}

      {/* Table */}
      {filteredRows.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-xs text-slate-500">
          Tidak ada data peserta yang sesuai dengan kata kunci pencarian.
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
                  <tr className="transition-colors hover:bg-sky-50/40" key={`${startIndex}-${index}`}>
                    <td className="px-4 py-3 text-slate-400 font-medium">{globalIndex}</td>
                    {columns.map((column) => {
                      const value = row[column];
                      const isKeterangan = column === "Keterangan";
                      return (
                        <td className="px-4 py-3" key={column}>
                          {isKeterangan && value ? (
                            <span className="inline-flex rounded-md bg-sky-50 px-2 py-0.5 text-[11px] font-semibold text-sky-700 border border-sky-100">
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

      {/* Pagination Controls */}
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
