"use client";

import {
  AlertCircle,
  CheckCircle2,
  ClipboardCheck,
  Download,
  FileSpreadsheet,
  LoaderCircle,
  RotateCcw,
  UploadCloud,
  UsersRound,
} from "lucide-react";
import { useId, useState } from "react";

import { downloadKehadiran, processKehadiran } from "@/lib/api";
import type { ExportStatus, KehadiranProcessResponse, ProcessStatus } from "@/types/dashboard";

import { PaginatedTable } from "./PaginatedTable";

function MiniUpload({
  label,
  hint,
  file,
  disabled,
  accept,
  onFileChange,
}: {
  label: string;
  hint: string;
  file: File | null;
  disabled: boolean;
  accept: string;
  onFileChange: (file: File | null) => void;
}) {
  const inputId = useId();
  return (
    <label
      className={`flex min-h-32 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-5 text-center transition ${
        disabled ? "cursor-not-allowed opacity-60" : "hover:border-blue-400 hover:bg-blue-50"
      }`}
      htmlFor={inputId}
    >
      <UploadCloud className="text-blue-700" size={28} />
      <p className="mt-2 text-sm font-semibold text-slate-700">{file?.name ?? label}</p>
      <p className="mt-1 text-xs text-slate-500">{hint}</p>
      <span className="mt-3 rounded-lg bg-blue-700 px-4 py-2 text-xs font-bold text-white">
        {file ? "Ganti File" : "Pilih File"}
      </span>
      <input
        accept={accept}
        className="sr-only"
        disabled={disabled}
        id={inputId}
        onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        type="file"
      />
    </label>
  );
}

export function KehadiranSection() {
  const [kehadiranFile, setKehadiranFile] = useState<File | null>(null);
  const [kelasFile, setKelasFile] = useState<File | null>(null);
  const [status, setStatus] = useState<ProcessStatus>("idle");
  const [downloadStatus, setDownloadStatus] = useState<ExportStatus>("idle");
  const [error, setError] = useState("");
  const [downloadMessage, setDownloadMessage] = useState("");
  const [result, setResult] = useState<KehadiranProcessResponse | null>(null);
  const [inputResetKey, setInputResetKey] = useState(0);

  const isProcessing = status === "processing";
  const canProcess = Boolean(kehadiranFile && kelasFile) && (status === "ready" || status === "error");

  function resetResultState() {
    setResult(null);
    setError("");
    setDownloadMessage("");
    setDownloadStatus("idle");
  }

  function handleKehadiranChange(file: File | null) {
    setKehadiranFile(file);
    resetResultState();
    setStatus(file && kelasFile ? "ready" : "idle");
  }

  function handleKelasChange(file: File | null) {
    setKelasFile(file);
    resetResultState();
    setStatus(kehadiranFile && file ? "ready" : "idle");
  }

  async function handleProcess() {
    if (!kehadiranFile || !kelasFile || !canProcess) return;
    setStatus("processing");
    setError("");
    try {
      setResult(await processKehadiran(kehadiranFile, kelasFile));
      setStatus("success");
    } catch (caughtError) {
      setStatus("error");
      setError(caughtError instanceof Error ? caughtError.message : "Proses kehadiran gagal.");
    }
  }

  async function handleDownload() {
    if (!result) return;
    setDownloadStatus("downloading");
    setDownloadMessage("");
    try {
      setDownloadMessage(`${await downloadKehadiran(result.session_id)} berhasil diunduh.`);
      setDownloadStatus("success");
    } catch (caughtError) {
      setDownloadMessage(caughtError instanceof Error ? caughtError.message : "Unduhan hasil kehadiran gagal.");
      setDownloadStatus("error");
    }
  }

  function handleReset() {
    setKehadiranFile(null);
    setKelasFile(null);
    setInputResetKey((value) => value + 1);
    setStatus("idle");
    resetResultState();
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div>
        <h2 className="text-base font-semibold text-slate-900">Tambah Keterangan Kehadiran</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          Pencocokan memakai NIM. Peserta di pembagian kelas yang tidak ditemukan di rekap kehadiran
          otomatis dihitung Tidak Hadir. Peserta yang hanya ada di rekap (mis. gelombang lain) diabaikan.
        </p>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <div key={`kehadiran-${inputResetKey}`}>
          <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-slate-600">
            <FileSpreadsheet size={14} /> File Rekap Kehadiran
          </p>
          <MiniUpload
            accept=".xlsx,.xls"
            disabled={isProcessing}
            file={kehadiranFile}
            hint="Kolom: NIM dan Status (Hadir / Tidak Hadir), bisa banyak sheet"
            label="Upload rekap kehadiran"
            onFileChange={handleKehadiranChange}
          />
        </div>

        <div key={`kelas-${inputResetKey}`}>
          <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-slate-600">
            <UsersRound size={14} /> File Pembagian Kelas
          </p>
          <MiniUpload
            accept=".xlsx"
            disabled={isProcessing}
            file={kelasFile}
            hint="Format .xlsx, kolom NIM wajib ada di tiap sheet kelas"
            label="Upload pembagian kelas"
            onFileChange={handleKelasChange}
          />
        </div>

        <div className="flex flex-col justify-center gap-2">
          <button
            className="flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            disabled={!canProcess}
            onClick={handleProcess}
            type="button"
          >
            {isProcessing ? <LoaderCircle className="animate-spin" size={18} /> : <ClipboardCheck size={18} />}
            {isProcessing ? "Memproses..." : status === "error" ? "Coba Proses Lagi" : "Proses Kehadiran"}
          </button>

          <button
            className={`flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-bold transition-all shadow-sm ${
              status === "success"
                ? "bg-emerald-600 text-white hover:bg-emerald-700 hover:shadow-md shadow-emerald-600/20 cursor-pointer active:scale-[0.98]"
                : "bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed opacity-60"
            }`}
            disabled={status !== "success" || downloadStatus === "downloading"}
            onClick={handleDownload}
            type="button"
          >
            {downloadStatus === "downloading" ? (
              <LoaderCircle className="animate-spin" size={18} />
            ) : (
              <Download size={18} />
            )}
            {downloadStatus === "downloading" ? "Mengunduh..." : "Download Hasil"}
          </button>

          <button
            className="flex items-center justify-center gap-2 px-4 py-2 text-xs font-semibold text-slate-600 hover:text-blue-700"
            onClick={handleReset}
            type="button"
          >
            <RotateCcw size={14} />
            Mulai File Baru
          </button>
        </div>
      </div>

      {isProcessing && (
        <p className="mt-4 flex items-center gap-2 text-sm text-blue-700">
          <LoaderCircle className="animate-spin" size={16} />
          Sedang mencocokkan NIM dengan rekap kehadiran...
        </p>
      )}

      {error && <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      {downloadMessage && (
        <p
          className={`mt-4 flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
            downloadStatus === "success" ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"
          }`}
        >
          {downloadStatus === "success" ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          {downloadMessage}
        </p>
      )}

      {result && (
        <div className="mt-5 space-y-4">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl bg-blue-50 p-4">
              <p className="text-xs font-semibold text-blue-700">Total Peserta</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_mahasiswa.toLocaleString("id-ID")}
              </p>
              <p className="mt-0.5 text-[11px] text-blue-700">
                di {result.summary.total_kelas.toLocaleString("id-ID")} kelas
              </p>
            </div>
            <div className="rounded-xl bg-emerald-50 p-4">
              <p className="text-xs font-semibold text-emerald-700">Hadir</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_hadir.toLocaleString("id-ID")}
              </p>
              <p className="mt-0.5 text-[11px] text-emerald-700">
                {result.summary.persentase_hadir.toLocaleString("id-ID")}% dari total
              </p>
            </div>
            <div className="rounded-xl bg-red-50 p-4">
              <p className="text-xs font-semibold text-red-700">Tidak Hadir</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_tidak_hadir.toLocaleString("id-ID")}
              </p>
              <p className="mt-0.5 text-[11px] text-red-600">Termasuk yang tidak ada di rekap</p>
            </div>
            <div className="rounded-xl bg-amber-50 p-4">
              <p className="text-xs font-semibold text-amber-700">Tidak Ada di Rekap</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_tidak_ada_di_rekap.toLocaleString("id-ID")}
              </p>
              <p className="mt-0.5 text-[11px] text-amber-700">Otomatis dihitung Tidak Hadir</p>
            </div>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-bold text-slate-800">Ringkasan Kehadiran per Kelas</h3>
            <PaginatedTable rows={result.ringkasan_kelas} />
          </div>

          {result.tidak_ada_di_rekap.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-bold text-slate-800">Peserta yang Tidak Ada di Rekap Kehadiran</h3>
              <p className="mb-2 text-xs text-slate-500">
                NIM berikut ada di pembagian kelas tetapi tidak ditemukan di rekap kehadiran, sehingga
                diberi keterangan Tidak Hadir.
              </p>
              <PaginatedTable rows={result.tidak_ada_di_rekap} />
            </div>
          )}
        </div>
      )}
    </section>
  );
}
