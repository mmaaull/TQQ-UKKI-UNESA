import { CheckCircle2, LoaderCircle, LockKeyhole, Play, TriangleAlert } from "lucide-react";

import type { ProcessStatus } from "@/types/dashboard";

export type ProcessCardProps = { disabled?: boolean; error?: string; onProcess?: () => void; status?: ProcessStatus };

const statusLabel: Record<ProcessStatus, string> = { idle: "Proses Rekap & Validasi", uploading: "Mengunggah file...", processing: "Memproses rekap...", success: "Proses Rekap & Validasi", error: "Coba Proses Kembali" };

export function ProcessCard({ disabled = true, error, onProcess, status = "idle" }: ProcessCardProps) {
  const inProgress = status === "uploading" || status === "processing";
  const Icon = inProgress ? LoaderCircle : status === "success" ? CheckCircle2 : status === "error" ? TriangleAlert : Play;
  return <article className="flex min-h-[310px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><div><h2 className="text-base font-semibold text-slate-900">Mulai Proses</h2><p className="mt-1 text-xs leading-5 text-slate-500">Upload kedua file untuk melanjutkan proses rekap</p></div><div className="flex flex-1 flex-col items-center justify-center"><button className={`flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold ${disabled || inProgress ? "cursor-not-allowed bg-slate-200 text-slate-400" : "bg-blue-700 text-white hover:bg-blue-800"}`} disabled={disabled || inProgress} onClick={onProcess} type="button"><Icon className={inProgress ? "animate-spin" : ""} fill={inProgress ? "none" : "currentColor"} size={19} /> {statusLabel[status]}</button>{error ? <p className="mt-4 flex items-start gap-2 rounded-lg bg-red-50 px-3 py-2 text-xs leading-5 text-red-700"><TriangleAlert className="mt-0.5 shrink-0" size={15} />{error}</p> : status === "success" ? <p className="mt-4 flex items-start gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-xs leading-5 text-emerald-700"><CheckCircle2 className="mt-0.5 shrink-0" size={15} />Rekap berhasil diproses.</p> : <p className="mt-4 flex items-start gap-2 text-center text-xs leading-5 text-slate-500"><LockKeyhole className="mt-0.5 shrink-0" size={15} />Tombol akan aktif setelah kedua file berhasil diupload</p>}</div></article>;
}
