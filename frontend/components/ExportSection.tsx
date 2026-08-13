"use client";

import { AlertCircle, CheckCircle2, Download, FileSpreadsheet, FolderArchive, LoaderCircle, TableProperties } from "lucide-react";
import { useState } from "react";

import { downloadExport } from "@/lib/api";
import type { ExportKind, ExportStatus } from "@/types/dashboard";

type ExportItem = { kind: ExportKind; title: string; description: string; requiresSession: boolean; icon: typeof FileSpreadsheet };

const exportItems: ExportItem[] = [
  { kind: "final", title: "Download Excel Final", description: "Rekap final seluruh peserta", requiresSession: true, icon: FileSpreadsheet },
  { kind: "validasi", title: "Download Laporan Validasi", description: "Rincian status dan masalah validasi", requiresSession: true, icon: TableProperties },
  { kind: "data-bermasalah", title: "Download Data Bermasalah", description: "Data yang perlu ditindaklanjuti", requiresSession: true, icon: AlertCircle },
  { kind: "per-kelas", title: "Download Per Kelas", description: "Arsip ZIP hasil rekap per kelas", requiresSession: true, icon: FolderArchive },
  { kind: "template", title: "Download Template", description: "Template Excel untuk input data", requiresSession: false, icon: FileSpreadsheet },
];

export type ExportSectionProps = { sessionId?: string | null };

export function ExportSection({ sessionId }: ExportSectionProps) {
  const [status, setStatus] = useState<Record<ExportKind, ExportStatus>>({ final: "idle", validasi: "idle", "data-bermasalah": "idle", "per-kelas": "idle", template: "idle" });
  const [message, setMessage] = useState("");
  const downloadSucceeded = message.includes("berhasil");

  async function handleDownload(kind: ExportKind) {
    setMessage("");
    setStatus((current) => ({ ...current, [kind]: "downloading" }));
    try {
      const filename = await downloadExport(kind, sessionId ?? undefined);
      setStatus((current) => ({ ...current, [kind]: "success" }));
      setMessage(`${filename} berhasil diunduh.`);
    } catch (caughtError) {
      setStatus((current) => ({ ...current, [kind]: "error" }));
      setMessage(caughtError instanceof Error ? caughtError.message : "Unduhan export gagal.");
    }
  }

  return <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"><div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end"><div><h2 className="text-base font-semibold text-slate-900">Export Hasil</h2><p className="mt-1 text-xs text-slate-500">Unduh file Excel yang dibuat oleh sistem rekap.</p></div>{sessionId ? <span className="text-xs font-medium text-emerald-700">Sesi export siap</span> : <span className="text-xs text-slate-500">Proses rekap untuk mengaktifkan export hasil</span>}</div><div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">{exportItems.map((item) => { const currentStatus = status[item.kind]; const unavailable = item.requiresSession && !sessionId; const isDownloading = currentStatus === "downloading"; const Icon = isDownloading ? LoaderCircle : currentStatus === "success" ? CheckCircle2 : item.icon; return <article className="flex min-h-40 flex-col rounded-xl border border-slate-200 p-4" key={item.kind}><div className="flex size-9 items-center justify-center rounded-lg bg-blue-50 text-blue-700"><Icon className={isDownloading ? "animate-spin" : ""} size={19} /></div><h3 className="mt-3 text-sm font-semibold text-slate-900">{item.title}</h3><p className="mt-1 flex-1 text-xs leading-5 text-slate-500">{item.description}</p><button className="mt-4 flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-3 py-2 text-xs font-bold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400" disabled={unavailable || isDownloading} onClick={() => handleDownload(item.kind)} type="button"><Download size={14} />{isDownloading ? "Mengunduh..." : "Download"}</button></article>; })}</div>{message && <p className={`mt-4 flex items-center gap-2 rounded-lg px-3 py-2 text-xs ${downloadSucceeded ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}`}>{downloadSucceeded ? <CheckCircle2 size={15} /> : <AlertCircle size={15} />}{message}</p>}</section>;
}
