"use client";

import { Clock3 } from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { ChartDatum } from "@/types/dashboard";

export type ProgressChartProps = {
  data: ChartDatum[];
  completion: string;
  needsReview?: { value: number; percentage: string };
  lastProcessed: string;
};

type ChartTooltipProps = {
  active?: boolean;
  payload?: Array<{ payload: ChartDatum }>;
};

function CustomTooltip({ active, payload }: ChartTooltipProps) {
  if (active && payload && payload.length) {
    const item: ChartDatum = payload[0].payload;
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xl text-xs space-y-1 min-w-[150px]">
        <div className="flex items-center gap-2 font-bold text-slate-900 border-b border-slate-100 pb-1">
          <span className="size-2.5 rounded-full" style={{ backgroundColor: item.color }} />
          <span>{item.name}</span>
        </div>
        <div className="flex justify-between gap-3 pt-0.5">
          <span className="text-slate-500">Jumlah:</span>
          <span className="font-bold text-slate-800">{item.value.toLocaleString("id-ID")}</span>
        </div>
        {item.percentage && (
          <div className="flex justify-between gap-3">
            <span className="text-slate-500">Persentase:</span>
            <span className="font-bold text-blue-700">{item.percentage}%</span>
          </div>
        )}
      </div>
    );
  }
  return null;
}

export function ProgressChart({ data, completion, needsReview, lastProcessed }: ProgressChartProps) {
  const hasData = data.some((item) => item.value > 0);
  return (
    <article className="flex min-h-[370px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <h2 className="text-base font-semibold text-slate-900">Progress Rekap</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">Persentase kelengkapan nilai keseluruhan</p>
      </div>

      {!hasData ? (
        <div className="flex flex-1 items-center justify-center py-8 text-center text-sm text-slate-500">
          Belum ada data nilai untuk ditampilkan.
        </div>
      ) : (
        <div className="flex flex-1 flex-col items-center justify-center gap-6 py-5 sm:flex-row">
          <div className="relative size-40">
            <ResponsiveContainer height="100%" width="100%">
              <PieChart>
                <Tooltip content={<CustomTooltip />} />
                <Pie
                  data={data}
                  dataKey="value"
                  innerRadius={52}
                  outerRadius={70}
                  paddingAngle={2}
                  startAngle={90}
                  endAngle={-270}
                >
                  {data.map((entry) => (
                    <Cell fill={entry.color} key={entry.name} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>

            <div className="pointer-events-none absolute inset-0 grid place-items-center text-center">
              <div>
                <p className="text-3xl font-bold tracking-tight text-slate-900">{completion}</p>
                <p className="mt-1 text-[11px] font-semibold text-slate-500">Selesai</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {data.map((item) => (
              <div className="flex items-start gap-2.5" key={item.name}>
                <span className="mt-1 size-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                <div>
                  <p className="text-xs font-semibold text-slate-700">{item.name}</p>
                  <p className="mt-0.5 text-[11px] text-slate-500">
                    {item.value.toLocaleString("id-ID")}
                    {item.percentage ? ` (${item.percentage}%)` : ""}
                  </p>
                </div>
              </div>
            ))}
            {needsReview && (
              <div className="flex items-start gap-2.5">
                <span className="mt-1 size-3 rounded-full bg-red-500 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-slate-700">Perlu Dicek</p>
                  <p className="mt-0.5 text-[11px] text-slate-500">
                    {needsReview.value} ({needsReview.percentage}%)
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <p className="flex items-center gap-1.5 border-t border-slate-100 pt-3 text-[11px] font-medium text-slate-500">
        <Clock3 size={14} /> Terakhir diproses: {lastProcessed}
      </p>
    </article>
  );
}
