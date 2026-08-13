"use client";

import { FileSpreadsheet, UploadCloud, UsersRound } from "lucide-react";
import { useId, useState } from "react";

export type UploadCardProps = { kind: "peserta" | "nilai"; title: string; description: string; disabled?: boolean; onFileChange?: (file: File | null) => void };

export function UploadCard({ kind, title, description, disabled = false, onFileChange }: UploadCardProps) {
  const inputId = useId(); const [fileName, setFileName] = useState(""); const isPeserta = kind === "peserta"; const Icon = isPeserta ? UsersRound : FileSpreadsheet;
  const accent = isPeserta ? "bg-blue-100 text-blue-700 hover:border-blue-400 hover:bg-blue-50" : "bg-emerald-100 text-emerald-700 hover:border-emerald-500 hover:bg-emerald-50";
  const button = isPeserta ? "bg-blue-700 hover:bg-blue-800" : "bg-emerald-600 hover:bg-emerald-700";
  return <article className="flex min-h-[310px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center gap-4"><div className={`grid size-12 place-items-center rounded-full ${accent.split(" ").slice(0, 2).join(" ")}`}><Icon size={23} /></div><div><h2 className="text-base font-semibold text-slate-900">{title}</h2><p className="mt-1 text-xs leading-5 text-slate-500">{description}</p></div></div><label className={`mt-5 flex flex-1 flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-5 text-center transition ${disabled ? "cursor-not-allowed opacity-60" : `cursor-pointer ${accent}`}`} htmlFor={inputId}><UploadCloud size={38} strokeWidth={1.6} /><p className="mt-3 text-sm font-medium text-slate-700">Drag & drop file Excel di sini</p><span className="mt-1 text-xs text-slate-500">atau</span><span className={`mt-3 rounded-lg px-4 py-2 text-xs font-bold text-white shadow-sm ${button}`}>Pilih File</span><input accept=".xlsx,.xls" className="sr-only" disabled={disabled} id={inputId} onChange={(event) => { const file = event.target.files?.[0] ?? null; setFileName(file?.name ?? ""); onFileChange?.(file); }} type="file" /></label><p className="mt-3 truncate text-center text-xs font-medium text-slate-500">{fileName || "Format: .xlsx, .xls • Maks. 50MB"}</p></article>;
}
