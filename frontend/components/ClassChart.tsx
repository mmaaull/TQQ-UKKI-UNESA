"use client";

import { ArrowRight } from "lucide-react";
import { Bar, BarChart, ResponsiveContainer, Tooltip } from "recharts";

import type { ClassProgressDatum } from "@/types/dashboard";

export type ClassChartProps = { data: ClassProgressDatum[]; onViewAll?: () => void };

export function ClassChart({ data, onViewAll }: ClassChartProps) {
  const hasData = data.length > 0;
  return <article className="flex min-h-[370px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><div><h2 className="text-base font-semibold text-slate-900">Kelengkapan Nilai per Kelas</h2><p className="mt-1 text-xs leading-5 text-slate-500">Kelas dengan nilai belum lengkap terbanyak</p></div>{hasData ? <><div className="mt-5 h-52 flex-1"><ResponsiveContainer height="100%" width="100%"><BarChart data={data} layout="vertical" margin={{ top: 0, left: 8, right: 12, bottom: 0 }}><Tooltip cursor={{ fill: "#f8fafc" }} formatter={(value) => [value, "Belum ada nilai"]} /><Bar dataKey="jumlah" fill="#fb7185" maxBarSize={16} radius={[0, 6, 6, 0]} /></BarChart></ResponsiveContainer></div><div className="space-y-2 text-xs text-slate-500">{data.slice(0, 3).map((item) => <div className="flex justify-between" key={item.kelas}><span>{item.kelas}</span><span className="font-semibold text-slate-700">{item.jumlah}</span></div>)}</div></> : <div className="flex flex-1 items-center justify-center py-8 text-center text-sm text-slate-500">Belum ada ringkasan kelas dari proses ini.</div>}<button className="mt-4 flex items-center justify-center gap-2 rounded-lg border border-slate-200 py-2.5 text-xs font-bold text-blue-700 transition hover:bg-blue-50" disabled={!hasData} onClick={onViewAll} type="button">Lihat Semua Kelas <ArrowRight size={15} /></button></article>;
}
