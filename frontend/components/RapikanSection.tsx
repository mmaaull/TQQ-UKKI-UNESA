"use client";

import { AlertCircle, CheckCircle2, Download, FileSpreadsheet, LoaderCircle, RotateCcw, UploadCloud } from "lucide-react";
import { useId, useState } from "react";

import { downloadRapikan, processRapikan } from "@/lib/api";
import type { ApiRecord, ExportStatus, ProcessStatus, RapikanProcessResponse } from "@/types/dashboard";

function PreviewTable({ rows, title }: { rows: ApiRecord[]; title: string }) {
  const columns = rows[0] ? Object.keys(rows[0]) : [];
  return <div className="overflow-x-auto rounded-xl border border-slate-200"><h3 className="border-b border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-800">{title}</h3>{rows.length === 0 ? <p className="px-4 py-6 text-center text-sm text-slate-500">Tidak ada data untuk ditampilkan.</p> : <table className="min-w-max w-full border-collapse text-left text-xs"><thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500"><tr>{columns.map((column) => <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3" key={column}>{column}</th>)}</tr></thead><tbody className="divide-y divide-slate-100 bg-white text-slate-700">{rows.map((row, index) => <tr key={index}>{columns.map((column) => <td className="max-w-72 px-4 py-3" key={column}>{row[column] === null || row[column] === "" ? "-" : String(row[column])}</td>)}</tr>)}</tbody></table>}</div>;
}

export function RapikanSection() {
  const inputId = useId();
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<ProcessStatus>("idle");
  const [downloadStatus, setDownloadStatus] = useState<ExportStatus>("idle");
  const [error, setError] = useState("");
  const [downloadMessage, setDownloadMessage] = useState("");
  const [result, setResult] = useState<RapikanProcessResponse | null>(null);
  const [inputResetKey, setInputResetKey] = useState(0);

  const isProcessing = status === "processing";
  const canProcess = status === "ready" || status === "error";

  function handleFileChange(nextFile: File | null) {
    setFile(nextFile);
    setResult(null);
    setError("");
    setDownloadMessage("");
    setDownloadStatus("idle");
    setStatus(nextFile ? "ready" : "idle");
  }

  async function handleProcess() {
    if (!file || !canProcess) return;
    setStatus("processing");
    setError("");
    try {
      setResult(await processRapikan(file));
      setStatus("success");
    } catch (caughtError) {
      setStatus("error");
      setError(caughtError instanceof Error ? caughtError.message : "Proses rapikan gagal.");
    }
  }

  async function handleDownload() {
    if (!result) return;
    setDownloadStatus("downloading");
    setDownloadMessage("");
    try {
      setDownloadMessage(`${await downloadRapikan(result.session_id)} berhasil diunduh.`);
      setDownloadStatus("success");
    } catch (caughtError) {
      setDownloadMessage(caughtError instanceof Error ? caughtError.message : "Unduhan hasil rapikan gagal.");
      setDownloadStatus("error");
    }
  }

  function handleReset() {
    setFile(null);
    setInputResetKey((value) => value + 1);
    setStatus("idle");
    setDownloadStatus("idle");
    setError("");
    setDownloadMessage("");
    setResult(null);
  }

  return <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"><div><h2 className="text-base font-semibold text-slate-900">Rapikan Hasil Rekap</h2><p className="mt-1 text-xs leading-5 text-slate-500">Pisahkan file berdasarkan Kode Kelas PAI dan Prodi, lalu urutkan data setiap sheet berdasarkan NIM.</p></div><div className="mt-5 grid gap-4 lg:grid-cols-[1fr_auto]"><label className={`flex min-h-32 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-5 text-center transition ${isProcessing ? "cursor-not-allowed opacity-60" : "hover:border-blue-400 hover:bg-blue-50"}`} htmlFor={inputId}><UploadCloud className="text-blue-700" size={32} /><p className="mt-2 text-sm font-semibold text-slate-700">{file?.name ?? "Upload file Excel hasil rekap"}</p><p className="mt-1 text-xs text-slate-500">Format .xlsx atau .xls</p><span className="mt-3 rounded-lg bg-blue-700 px-4 py-2 text-xs font-bold text-white">Pilih File</span><input accept=".xlsx,.xls" className="sr-only" disabled={isProcessing} id={inputId} key={inputResetKey} onChange={(event) => handleFileChange(event.target.files?.[0] ?? null)} type="file" /></label><div className="flex min-w-56 flex-col justify-center gap-2"><button className="flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400" disabled={!canProcess} onClick={handleProcess} type="button">{isProcessing ? <LoaderCircle className="animate-spin" size={18} /> : <FileSpreadsheet size={18} />}{isProcessing ? "Memproses..." : status === "error" ? "Coba Proses Lagi" : "Proses Rapikan"}</button><button className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50" disabled={status !== "success" || downloadStatus === "downloading"} onClick={handleDownload} type="button">{downloadStatus === "downloading" ? <LoaderCircle className="animate-spin" size={18} /> : <Download size={18} />}{downloadStatus === "downloading" ? "Mengunduh..." : "Download Hasil"}</button><button className="flex items-center justify-center gap-2 px-4 py-2 text-xs font-semibold text-slate-600 hover:text-blue-700" onClick={handleReset} type="button"><RotateCcw size={14} />Mulai File Baru</button></div></div>{isProcessing && <p className="mt-4 flex items-center gap-2 text-sm text-blue-700"><LoaderCircle className="animate-spin" size={16} />Sedang membaca, mengelompokkan, dan merapikan data...</p>}{error && <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}{downloadMessage && <p className={`mt-4 flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${downloadStatus === "success" ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}`}>{downloadStatus === "success" ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}{downloadMessage}</p>}{result && <div className="mt-5 space-y-4"><div className="grid gap-3 sm:grid-cols-2"><div className="rounded-xl bg-blue-50 p-4"><p className="text-xs font-semibold text-blue-700">Total Data</p><p className="mt-1 text-2xl font-bold text-slate-900">{result.summary.total_data.toLocaleString("id-ID")}</p></div><div className="rounded-xl bg-emerald-50 p-4"><p className="text-xs font-semibold text-emerald-700">Total Sheet</p><p className="mt-1 text-2xl font-bold text-slate-900">{result.summary.total_sheet.toLocaleString("id-ID")}</p></div></div><PreviewTable rows={result.preview} title="Preview Data Gabungan" /><PreviewTable rows={result.sheet_preview} title="Preview Sheet yang Akan Dibuat" /></div>}</section>;
}
