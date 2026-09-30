"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";

import type { ApiRecord } from "@/types/dashboard";

const ITEMS_PER_PAGE = 10;

export function PaginatedTable({ rows }: { rows: ApiRecord[] }) {
  const [currentPage, setCurrentPage] = useState(1);

  // Kalau data ganti (mis. proses ulang), balik ke halaman 1.
  useEffect(() => {
    setCurrentPage(1);
  }, [rows]);

  if (rows.length === 0) {
    return <p className="px-4 py-6 text-center text-sm text-slate-500">Tidak ada data untuk ditampilkan.</p>;
  }

  const columns = Object.keys(rows[0]);
  const totalPages = Math.max(1, Math.ceil(rows.length / ITEMS_PER_PAGE));
  const validPage = Math.min(currentPage, totalPages);
  const startIndex = (validPage - 1) * ITEMS_PER_PAGE;
  const displayedRows = rows.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  const startItem = startIndex + 1;
  const endItem = Math.min(startIndex + ITEMS_PER_PAGE, rows.length);

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full border-collapse text-left text-xs">
          <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            <tr>
              {columns.map((column) => (
                <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3" key={column}>
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
            {displayedRows.map((row, index) => (
              <tr className="transition-colors hover:bg-blue-50/50" key={startIndex + index}>
                {columns.map((column) => (
                  <td className="px-4 py-3" key={column}>
                    {row[column] === null || row[column] === "" ? "-" : String(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <p className="text-xs text-slate-500">
            Menampilkan <span className="font-semibold text-slate-700">{startItem}</span> -{" "}
            <span className="font-semibold text-slate-700">{endItem}</span> dari{" "}
            <span className="font-semibold text-slate-700">{rows.length}</span> data
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
