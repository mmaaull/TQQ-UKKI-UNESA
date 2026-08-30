"use client";

import { ArrowRight, CheckCircle2 } from "lucide-react";

import type { ClassProgressDatum } from "@/types/dashboard";

export type ClassChartProps = { data: ClassProgressDatum[]; onViewAll?: () => void };

export function ClassChart({ data, onViewAll }: ClassChartProps) {
  const hasData = data.length > 0;

  // Prioritaskan kelas yang belum lengkap (paling banyak belum ada nilai)
  const sortedData = [...data]
    .sort((a, b) => (b.jumlah - a.jumlah) || ((a.persentase ?? 100) - (b.persentase ?? 100)))
    .slice(0, 5);

  const isAllComplete = hasData && data.every((item) => item.jumlah === 0);

  return (
    <article className="flex min-h-[370px] flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-base font-semibold text-slate-900">Kelengkapan Nilai per Kelas</h2>
          {isAllComplete && (
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold text-emerald-700">
              <CheckCircle2 size={12} /> 100% Lengkap
            </span>
          )}
        </div>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          {isAllComplete
            ? "Seluruh nilai kelas telah lengkap terinput"
            : "Ringkasan kelas yang paling memerlukan perhatian"}
        </p>

        {hasData ? (
          <div className="mt-5 space-y-3.5">
            {sortedData.map((item) => {
              const percent = item.persentase ?? 100;
              const isComplete = item.jumlah === 0;

              return (
                <div key={item.kelas} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-800">{item.kelas}</span>
                    <div className="flex items-center gap-2">
                      <span
                        className={`font-bold ${
                          isComplete ? "text-emerald-600" : "text-amber-600"
                        }`}
                      >
                        {percent}%
                      </span>
                      <span className="text-[11px] text-slate-400">
                        ({item.sudahAdaNilai ?? 0}/{item.total ?? 0})
                      </span>
                    </div>
                  </div>

                  {/* Horizontal Progress Bar */}
                  <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isComplete ? "bg-emerald-500" : "bg-amber-500"
                      }`}
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-1 items-center justify-center py-10 text-center text-sm text-slate-500">
            Belum ada ringkasan kelas dari proses ini.
          </div>
        )}
      </div>

      <button
        className="mt-6 flex items-center justify-center gap-2 rounded-xl border border-slate-200 py-2.5 text-xs font-bold text-blue-700 transition hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-50"
        disabled={!hasData}
        onClick={onViewAll}
        type="button"
      >
        <span>Lihat Semua Kelas ({data.length})</span>
        <ArrowRight size={15} />
      </button>
    </article>
  );
}
