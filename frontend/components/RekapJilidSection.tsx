"use client";

import {
  AlertCircle,
  BookMarked,
  CheckCircle2,
  Download,
  FileSpreadsheet,
  Info,
  LoaderCircle,
  RotateCcw,
  UploadCloud,
  UsersRound,
} from "lucide-react";
import { useId, useState } from "react";

import { downloadRekapJilid, processRekapJilid } from "@/lib/api";
import type { ExportStatus, ProcessStatus, RekapJilidProcessResponse } from "@/types/dashboard";

import { JilidOtomatisTable } from "./JilidOtomatisTable";
import { JilidProblemTable } from "./JilidProblemTable";
import { PaginatedTable } from "./PaginatedTable";
import { PembagianTentorSection } from "./PembagianTentorSection";

function MiniUpload({
  label,
  hint,
  file,
  disabled,
  onFileChange,
}: {
  label: string;
  hint: string;
  file: File | null;
  disabled: boolean;
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
        accept=".xlsx,.xls"
        className="sr-only"
        disabled={disabled}
        id={inputId}
        onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        type="file"
      />
    </label>
  );
}

export function RekapJilidSection() {
  const [masterFile, setMasterFile] = useState<File | null>(null);
  const [penilaianFile, setPenilaianFile] = useState<File | null>(null);
  const [status, setStatus] = useState<ProcessStatus>("idle");
  const [downloadStatus, setDownloadStatus] = useState<ExportStatus>("idle");
  const [error, setError] = useState("");
  const [downloadMessage, setDownloadMessage] = useState("");
  const [result, setResult] = useState<RekapJilidProcessResponse | null>(null);
  const [inputResetKey, setInputResetKey] = useState(0);

  const isProcessing = status === "processing";
  const canProcess = Boolean(masterFile && penilaianFile) && (status === "ready" || status === "error");

  function resetResultState() {
    setResult(null);
    setError("");
    setDownloadMessage("");
    setDownloadStatus("idle");
  }

  function handleMasterChange(file: File | null) {
    setMasterFile(file);
    resetResultState();
    setStatus(file && penilaianFile ? "ready" : "idle");
  }

  function handlePenilaianChange(file: File | null) {
    setPenilaianFile(file);
    resetResultState();
    setStatus(masterFile && file ? "ready" : "idle");
  }

  async function handleProcess() {
    if (!masterFile || !penilaianFile || !canProcess) return;
    setStatus("processing");
    setError("");
    try {
      setResult(await processRekapJilid(masterFile, penilaianFile));
      setStatus("success");
    } catch (caughtError) {
      setStatus("error");
      setError(caughtError instanceof Error ? caughtError.message : "Proses rekap jilid gagal.");
    }
  }

  async function handleDownload() {
    if (!result) return;
    setDownloadStatus("downloading");
    setDownloadMessage("");
    try {
      setDownloadMessage(`${await downloadRekapJilid(result.session_id)} berhasil diunduh.`);
      setDownloadStatus("success");
    } catch (caughtError) {
      setDownloadMessage(
        caughtError instanceof Error ? caughtError.message : "Unduhan hasil rekap jilid gagal."
      );
      setDownloadStatus("error");
    }
  }

  function handleReset() {
    setMasterFile(null);
    setPenilaianFile(null);
    setInputResetKey((value) => value + 1);
    setStatus("idle");
    resetResultState();
  }

  return (
    <div className="space-y-6">
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div>
        <h2 className="text-base font-semibold text-slate-900">Rekap Pembagian Kelas Jilid</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          Kelompokkan peserta ke Jilid 1-4 berdasarkan Total Nilai tashih, dipisah antara peserta
          laki-laki dan perempuan menggunakan data jenis kelamin dari file master.
        </p>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <div key={`master-${inputResetKey}`}>
          <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-slate-600">
            <UsersRound size={14} /> File Master (Data Keseluruhan Peserta)
          </p>
          <MiniUpload
            disabled={isProcessing}
            file={masterFile}
            hint="Kolom: Nama, Jenis Kelamin, NIM, Kelas PAI, Program Studi"
            label="Upload file master"
            onFileChange={handleMasterChange}
          />
        </div>

        <div key={`penilaian-${inputResetKey}`}>
          <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-slate-600">
            <FileSpreadsheet size={14} /> File Penilaian Tashih
          </p>
          <MiniUpload
            disabled={isProcessing}
            file={penilaianFile}
            hint="Berisi NIM dan Total Nilai hasil tes tashih"
            label="Upload file penilaian"
            onFileChange={handlePenilaianChange}
          />
        </div>

        <div className="flex flex-col justify-center gap-2">
          <button
            className="flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            disabled={!canProcess}
            onClick={handleProcess}
            type="button"
          >
            {isProcessing ? <LoaderCircle className="animate-spin" size={18} /> : <BookMarked size={18} />}
            {isProcessing ? "Memproses..." : status === "error" ? "Coba Proses Lagi" : "Proses Rekap Jilid"}
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
          Sedang mencocokkan data master dan menghitung pembagian jilid...
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
              <p
                className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700"
                title="Jumlah baris di file penilaian tashih yang kamu upload (file gelombang ini saja)."
              >
                Total Peserta Dinilai
                <Info size={12} className="shrink-0 opacity-70" />
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_dinilai.toLocaleString("id-ID")}
              </p>
            </div>
            <div className="rounded-xl bg-sky-50 p-4">
              <p
                className="inline-flex items-center gap-1 text-xs font-semibold text-sky-700"
                title="Peserta di file master yang kelasnya sudah kesentuh gelombang ini, tapi tidak ikut tes. Mereka TIDAK termasuk di 'Total Peserta Dinilai' di atas — angka ini murni tambahan, bukan pengurang."
              >
                Otomatis Jilid 1
                <Info size={12} className="shrink-0 opacity-70" />
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_otomatis_jilid1.toLocaleString("id-ID")}
              </p>
              <p className="mt-0.5 text-[11px] text-sky-700">Tidak ikut tes, di luar Total Dinilai</p>
            </div>
            <div className="rounded-xl bg-emerald-50 p-4">
              <p
                className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700"
                title="Peserta valid dari file penilaian + peserta Otomatis Jilid 1. Karena sumbernya beda file, angka ini bisa lebih besar dari 'Total Peserta Dinilai'."
              >
                Berhasil Diklasifikasikan
                <Info size={12} className="shrink-0 opacity-70" />
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_terklasifikasi.toLocaleString("id-ID")}
              </p>
            </div>
            <div className="rounded-xl bg-red-50 p-4">
              <p
                className="inline-flex items-center gap-1 text-xs font-semibold text-red-700"
                title="Baris yang tidak masuk kelas Jilid, termasuk baris NIM duplikat, NIM tidak di master, nama beda, jenis kelamin kosong, atau nilai di luar rentang."
              >
                Data Bermasalah
                <Info size={12} className="shrink-0 opacity-70" />
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_bermasalah.toLocaleString("id-ID")}
              </p>
              {Boolean(result.summary.total_duplikat_disaring && result.summary.total_duplikat_disaring > 0) && (
                <p className="mt-0.5 text-[11px] text-red-600">
                  Termasuk {result.summary.total_duplikat_disaring} baris duplikat
                </p>
              )}
            </div>
          </div>

          <p className="rounded-xl bg-slate-50 px-4 py-3 text-xs leading-5 text-slate-500">
            <span className="font-semibold text-slate-600">Alur Perhitungan:</span>{" "}
            Total Dinilai ({result.summary.total_dinilai.toLocaleString("id-ID")}){" "}
            − Data Bermasalah ({result.summary.total_bermasalah.toLocaleString("id-ID")}){" "}
            + Otomatis Jilid 1 ({result.summary.total_otomatis_jilid1.toLocaleString("id-ID")}){" "}
            = <span className="font-semibold text-emerald-700">Berhasil Diklasifikasikan ({result.summary.total_terklasifikasi.toLocaleString("id-ID")})</span>.
          </p>

          <div>
            <h3 className="mb-2 text-sm font-bold text-slate-800">Ringkasan Jumlah per Jilid</h3>
            <PaginatedTable rows={result.ringkasan_jilid} />
          </div>

          {result.data_otomatis_jilid1 && result.data_otomatis_jilid1.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-bold text-slate-800">
                Data Peserta Otomatis Jilid 1
              </h3>
              <p className="mb-2 text-xs text-slate-500">
                Daftar peserta yang otomatis dimasukkan ke Jilid 1 (karena tidak ikut tes tashih gelombang ini atau Total Nilai kosong).
              </p>
              <JilidOtomatisTable rows={result.data_otomatis_jilid1} />
            </div>
          )}

          {result.summary.total_bermasalah > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-bold text-slate-800">
                Rincian Data Bermasalah per Jenis
              </h3>
              <p className="mb-2 text-xs text-slate-500">
                Ini rincian dari {result.summary.total_bermasalah.toLocaleString("id-ID")} baris Data
                Bermasalah di atas, dikelompokkan per jenis masalahnya.
              </p>
              <PaginatedTable rows={result.ringkasan_masalah} />
            </div>
          )}

          {result.summary.total_bermasalah > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-bold text-slate-800">Data Bermasalah</h3>
              <p className="mb-2 text-xs text-slate-500">
                Data ini dikeluarkan dari sheet Jilid dan bisa dicek manual pada sheet &quot;Data Bermasalah&quot;
                di file hasil unduhan.
              </p>
              <JilidProblemTable rows={result.data_bermasalah} />
            </div>
          )}
        </div>
      )}
    </section>

    <PembagianTentorSection
      jilidSessionId={result?.session_id ?? null}
      jilidSessionLabel={
        result
          ? `${result.summary.total_terklasifikasi.toLocaleString("id-ID")} peserta terklasifikasi dari proses Rekap Jilid barusan.`
          : undefined
      }
    />
    </div>
  );
}
