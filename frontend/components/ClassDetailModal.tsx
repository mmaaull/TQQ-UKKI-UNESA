"use client";

import { CheckCircle2, GraduationCap, Search, X } from "lucide-react";
import { useMemo, useState } from "react";

import type { ClassProgressDatum } from "@/types/dashboard";

export type ClassDetailModalProps = {
  isOpen: boolean;
  onClose: () => void;
  data: ClassProgressDatum[];
};

export function ClassDetailModal({ isOpen, onClose, data }: ClassDetailModalProps) {
  const [search, setSearch] = useState("");

  const summaryMetrics = useMemo(() => {
    const totalKelas = data.length;
    const lengkap = data.filter((d) => d.jumlah === 0).length;
    const belumLengkap = totalKelas - lengkap;
    return { totalKelas, lengkap, belumLengkap };
  }, [data]);

  const filteredData = useMemo(() => {
    const keyword = search.trim().toLocaleLowerCase("id-ID");
    if (!keyword) return data;
    return data.filter((d) => d.kelas.toLocaleLowerCase("id-ID").includes(keyword));
  }, [data, search]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Card */}
      <div className="relative z-10 flex max-h-[90vh] w-full max-w-3xl flex-col rounded-3xl bg-white shadow-2xl overflow-hidden border border-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5 bg-gradient-to-r from-blue-50/50 to-white">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-2xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
              <GraduationCap size={20} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Rincian Kelengkapan Per Kode Kelas PAI</h2>
              <p className="text-xs font-medium text-slate-500">
                Total <span className="font-semibold text-slate-700">{data.length}</span> kelas terdeteksi
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="grid size-9 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
            type="button"
            aria-label="Tutup modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Top Summary KPI Cards & Search Bar */}
        <div className="p-6 pb-2 space-y-4 border-b border-slate-100 bg-slate-50/50">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
              <p className="text-[11px] font-semibold text-slate-500">Total Kode Kelas</p>
              <p className="mt-1 text-xl font-bold text-slate-900">{summaryMetrics.totalKelas}</p>
            </div>
            <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-3 shadow-sm">
              <p className="text-[11px] font-semibold text-emerald-700">Kelas 100% Lengkap</p>
              <p className="mt-1 text-xl font-bold text-emerald-900">{summaryMetrics.lengkap}</p>
            </div>
            <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-3 shadow-sm">
              <p className="text-[11px] font-semibold text-amber-700">Kelas Belum Lengkap</p>
              <p className="mt-1 text-xl font-bold text-amber-900">{summaryMetrics.belumLengkap}</p>
            </div>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
            <input
              type="text"
              placeholder="Cari Kode Kelas PAI (misal: A1022)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white py-2 pl-9 pr-4 text-xs text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>
        </div>

        {/* Table List Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full border-collapse text-left text-xs">
              <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="border-b border-slate-200 px-4 py-3">No</th>
                  <th className="border-b border-slate-200 px-4 py-3">Kode Kelas PAI</th>
                  <th className="border-b border-slate-200 px-4 py-3 text-right">Sudah Ada Nilai</th>
                  <th className="border-b border-slate-200 px-4 py-3 text-right">Belum Ada Nilai</th>
                  <th className="border-b border-slate-200 px-4 py-3 text-right">Total Peserta</th>
                  <th className="border-b border-slate-200 px-4 py-3 text-center">Kelengkapan</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
                {filteredData.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                      Tidak ada kelas yang sesuai dengan pencarian.
                    </td>
                  </tr>
                ) : (
                  filteredData.map((row, idx) => {
                    const isComplete = row.jumlah === 0;
                    const percent = row.persentase ?? 100;
                    return (
                      <tr key={row.kelas} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-4 py-3 text-slate-400 font-medium">{idx + 1}</td>
                        <td className="px-4 py-3 font-bold text-slate-900">{row.kelas}</td>
                        <td className="px-4 py-3 text-right font-semibold text-emerald-600">
                          {row.sudahAdaNilai ?? 0}
                        </td>
                        <td className="px-4 py-3 text-right font-semibold">
                          <span
                            className={
                              row.jumlah > 0
                                ? "inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-800"
                                : "text-slate-400"
                            }
                          >
                            {row.jumlah}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-700">
                          {row.total ?? 0}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2 justify-end">
                            <div className="h-2 w-16 overflow-hidden rounded-full bg-slate-100">
                              <div
                                className={`h-full rounded-full ${
                                  isComplete ? "bg-emerald-500" : "bg-amber-500"
                                }`}
                                style={{ width: `${percent}%` }}
                              />
                            </div>
                            <span className="font-bold text-slate-800 text-[11px] min-w-9 text-right">
                              {percent}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50/80 px-6 py-4">
          <p className="text-xs text-slate-500">
            Menampilkan <span className="font-semibold text-slate-700">{filteredData.length}</span> dari{" "}
            <span className="font-semibold text-slate-700">{data.length}</span> kelas
          </p>
          <button
            onClick={onClose}
            className="inline-flex items-center gap-1.5 rounded-xl bg-slate-800 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-slate-900 transition"
            type="button"
          >
            <CheckCircle2 size={15} />
            <span>Tutup</span>
          </button>
        </div>
      </div>
    </div>
  );
}
