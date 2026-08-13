"use client";

import { ArrowRight } from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

import type { ChartDatum } from "@/types/dashboard";

export type ValidationChartProps = { data: ChartDatum[]; total: number; onViewDetails?: () => void };

export function ValidationChart({ data, total, onViewDetails }: ValidationChartProps) {
  return <article className="flex min-h-[370px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><div><h2 className="text-base font-semibold text-slate-900">Status Validasi</h2><p className="mt-1 text-xs leading-5 text-slate-500">Ringkasan hasil validasi data</p></div><div className="flex flex-1 flex-col items-center justify-center gap-5 py-5 sm:flex-row lg:flex-col xl:flex-row"><div className="relative size-32 shrink-0"><ResponsiveContainer height="100%" width="100%"><PieChart><Pie data={data} dataKey="value" innerRadius={40} outerRadius={58} paddingAngle={2}>{data.map((entry) => <Cell fill={entry.color} key={entry.name} />)}</Pie></PieChart></ResponsiveContainer><div className="pointer-events-none absolute inset-0 grid place-items-center text-center"><div><p className="text-[10px] font-semibold text-slate-500">Total Masalah</p><p className="mt-1 text-2xl font-bold text-slate-900">{total}</p></div></div></div><div className="w-full space-y-2.5">{data.map((item) => <div className="flex items-center justify-between gap-3 text-xs" key={item.name}><span className="flex items-center gap-2 text-slate-700"><i className="size-2.5 rounded-full" style={{ backgroundColor: item.color }} />{item.name}</span><strong className="text-slate-900">{item.value}</strong></div>)}</div></div><button className="mt-4 flex items-center justify-center gap-2 rounded-lg border border-slate-200 py-2.5 text-xs font-bold text-blue-700 transition hover:bg-blue-50" onClick={onViewDetails} type="button">Lihat Detail Validasi <ArrowRight size={15} /></button></article>;
}
