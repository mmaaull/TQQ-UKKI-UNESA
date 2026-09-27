"use client";

import { ArrowRight } from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { ChartDatum } from "@/types/dashboard";

export type ValidationChartProps = {
  data: ChartDatum[];
  total: number;
  onViewDetails?: () => void;
};

type ValidationTooltipProps = {
  active?: boolean;
  payload?: Array<{ payload: ChartDatum }>;
  total: number;
};

function CustomTooltip({ active, payload, total }: ValidationTooltipProps) {
  if (active && payload && payload.length) {
    const item: ChartDatum = payload[0].payload;
    const percent = total > 0 ? ((item.value / total) * 100).toFixed(1) : "0";
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xl text-xs space-y-1 min-w-[170px]">
        <div className="flex items-center gap-2 font-bold text-slate-900 border-b border-slate-100 pb-1">
          <span className="size-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
          <span>{item.name}</span>
        </div>
        <div className="flex justify-between gap-3 pt-0.5">
          <span className="text-slate-500">Jumlah Kasus:</span>
          <span className="font-bold text-slate-800">{item.value.toLocaleString("id-ID")}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span className="text-slate-500">Porsi Masalah:</span>
          <span className="font-bold text-red-600">{percent}%</span>
        </div>
      </div>
    );
  }
  return null;
}

export function ValidationChart({ data, total, onViewDetails }: ValidationChartProps) {
  const hasData = data.length > 0;
  return (
    <article className="flex min-h-[370px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <h2 className="text-base font-semibold text-slate-900">Status Validasi</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">Ringkasan hasil validasi data</p>
      </div>

      {hasData ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-5 py-5 sm:flex-row lg:flex-col xl:flex-row">
          <div className="relative size-32 shrink-0">
            <ResponsiveContainer height="100%" width="100%">
              <PieChart>
                <Tooltip content={<CustomTooltip total={total} />} />
                <Pie data={data} dataKey="value" innerRadius={40} outerRadius={58} paddingAngle={2}>
                  {data.map((entry) => (
                    <Cell fill={entry.color} key={entry.name} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>

            <div className="pointer-events-none absolute inset-0 grid place-items-center text-center">
              <div>
                <p className="text-[10px] font-semibold text-slate-500">Total Masalah</p>
                <p className="mt-1 text-2xl font-bold text-slate-900">{total}</p>
              </div>
            </div>
          </div>

          <div className="w-full space-y-2.5">
            {data.map((item) => (
              <div className="flex items-center justify-between gap-3 text-xs" key={item.name}>
                <span className="flex items-center gap-2 text-slate-700">
                  <i className="size-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                  <span>{item.name}</span>
                </span>
                <strong className="text-slate-900">{item.value}</strong>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center py-8 text-center text-sm text-slate-500">
          Tidak ada masalah validasi pada proses ini.
        </div>
      )}

      <button
        className="mt-4 flex items-center justify-center gap-2 rounded-xl border border-slate-200 py-2.5 text-xs font-bold text-blue-700 transition hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-50"
        disabled={!hasData}
        onClick={onViewDetails}
        type="button"
      >
        <span>Lihat Detail Validasi</span>
        <ArrowRight size={15} />
      </button>
    </article>
  );
}
