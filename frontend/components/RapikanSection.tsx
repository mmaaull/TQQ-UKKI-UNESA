"use client";

import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  FileSpreadsheet,
  LoaderCircle,
  Maximize2,
  RotateCcw,
  Search,
  UploadCloud,
} from "lucide-react";
import { useEffect, useId, useMemo, useState } from "react";

import { downloadRapikan, processRapikan } from "@/lib/api";
import type { ApiRecord, ExportStatus, ProcessStatus, RapikanProcessResponse } from "@/types/dashboard";

const ITEMS_PER_PAGE = 10;

function PreviewTable({ rows, title }: { rows: ApiRecord[]; title: string }) {
  const [search, setSearch] = useState("");
  const [kelasFilter, setKelasFilter] = useState("");
  const [prodiFilter, setProdiFilter] = useState("");

  const [currentPage, setCurrentPage] = useState(1);
  const [isFullView, setIsFullView] = useState(false);

  const columns = rows[0] ? Object.keys(rows[0]) : [];

  // Helper to find a column name regardless of casing
  function findColName(candidates: string[]): string | undefined {
    return columns.find((c) => candidates.some((cand) => cand.toLowerCase() === c.toLowerCase()));
  }

  const kelasColName = useMemo(() => findColName(["Kode Kelas PAI", "Kelas PAI", "Kode PAI", "Kelas"]), [columns]);
  const prodiColName = useMemo(() => findColName(["Prodi", "Program Studi", "PRODI"]), [columns]);

  // Extract filter options dynamically
  const kelasOptions = useMemo(() => {
    if (!kelasColName || !rows) return [];
    const values = rows.map((r) => String(r[kelasColName] ?? "")).filter(Boolean);
    return [...new Set(values)].sort();
  }, [rows, kelasColName]);

  const prodiOptions = useMemo(() => {
    if (!prodiColName || !rows) return [];
    const values = rows.map((r) => String(r[prodiColName] ?? "")).filter(Boolean);
    return [...new Set(values)].sort();
  }, [rows, prodiColName]);

  // Filter rows logic
  const filteredRows = useMemo(() => {
    const keyword = search.trim().toLocaleLowerCase("id-ID");
    return rows.filter((row) => {
      const matchesSearch =
        !keyword ||
        Object.values(row).some(
          (val) => val !== null && String(val).toLocaleLowerCase("id-ID").includes(keyword)
        );

      const rowKelas = kelasColName ? String(row[kelasColName] ?? "") : "";
      const matchesKelas = !kelasFilter || rowKelas === kelasFilter;

      const rowProdi = prodiColName ? String(row[prodiColName] ?? "") : "";
      const matchesProdi = !prodiFilter || rowProdi === prodiFilter;

      return matchesSearch && matchesKelas && matchesProdi;
    });
  }, [rows, search, kelasColName, kelasFilter, prodiColName, prodiFilter]);

  // Reset page when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [search, kelasFilter, prodiFilter]);

  function resetFilters() {
    setSearch("");
    setKelasFilter("");
    setProdiFilter("");
    setCurrentPage(1);
  }

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / ITEMS_PER_PAGE));
  const validPage = Math.min(currentPage, totalPages);

  const displayedRows = useMemo(() => {
    if (isFullView) return filteredRows;
    const startIndex = (validPage - 1) * ITEMS_PER_PAGE;
    return filteredRows.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredRows, isFullView, validPage]);

  const startItem = filteredRows.length === 0 ? 0 : (validPage - 1) * ITEMS_PER_PAGE + 1;
  const endItem = isFullView ? filteredRows.length : Math.min(validPage * ITEMS_PER_PAGE, filteredRows.length);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div className="flex flex-col gap-4">
        {/* Header */}
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-800">{title}</h3>
              {isFullView && (
                <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-[10px] font-bold text-blue-700">
                  Tampilan Penuh
                </span>
              )}
            </div>
            <p className="mt-0.5 text-xs text-slate-500">
              {filteredRows.length} dari {rows.length} total data
            </p>
          </div>

          {rows.length > 0 && (
            <button
              onClick={() => setIsFullView(!isFullView)}
              className="inline-flex items-center gap-1.5 self-start rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 sm:self-center"
              type="button"
            >
              {isFullView ? (
                <>
                  <ArrowLeft size={14} />
                  <span>Kembali</span>
                </>
              ) : (
                <>
                  <Maximize2 size={14} />
                  <span>Tampilkan Semua Data</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Search & Filter Bar */}
        {rows.length > 0 && (
          <div className="flex flex-wrap items-center gap-2.5 rounded-xl bg-slate-50 p-2.5 border border-slate-200/80">
            {/* Search Input */}
            <div className="relative min-w-[200px] flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
              <input
                type="text"
                placeholder="Cari kata kunci..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-xs text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {/* Filter Kode Kelas PAI */}
            {kelasOptions.length > 0 && (
              <select
                value={kelasFilter}
                onChange={(e) => setKelasFilter(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 focus:border-blue-500 focus:outline-none"
              >
                <option value="">Semua Kelas</option>
                {kelasOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            )}

            {/* Filter Prodi */}
            {prodiOptions.length > 0 && (
              <select
                value={prodiFilter}
                onChange={(e) => setProdiFilter(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 focus:border-blue-500 focus:outline-none"
              >
                <option value="">Semua Prodi</option>
                {prodiOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            )}

            {/* Reset Filter Button */}
            {(search || kelasFilter || prodiFilter) && (
              <button
                onClick={resetFilters}
                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
                type="button"
                title="Reset Filter"
              >
                <RotateCcw size={13} />
                <span>Reset</span>
              </button>
            )}
          </div>
        )}

        {/* Content */}
        {rows.length === 0 ? (
          <p className="px-4 py-6 text-center text-sm text-slate-500">Tidak ada data untuk ditampilkan.</p>
        ) : filteredRows.length === 0 ? (
          <p className="px-4 py-6 text-center text-xs text-slate-500">
            Tidak ada data yang sesuai dengan filter atau kata kunci pencarian.
          </p>
        ) : (
          <>
            <div className="overflow-x-auto rounded-xl border border-slate-200" tabIndex={0}>
              <table className="min-w-max w-full border-collapse text-left text-xs">
                <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3">No</th>
                    {columns.map((column) => (
                      <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3" key={column}>
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
                  {displayedRows.map((row, index) => {
                    const globalIndex = isFullView ? index + 1 : (validPage - 1) * ITEMS_PER_PAGE + index + 1;
                    return (
                      <tr className="transition-colors hover:bg-blue-50/50" key={index}>
                        <td className="px-4 py-3 font-medium text-slate-500">{globalIndex}</td>
                        {columns.map((column) => (
                          <td className="max-w-72 px-4 py-3" key={column}>
                            {row[column] === null || row[column] === "" ? "-" : String(row[column])}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {!isFullView && (
              <div className="flex flex-col justify-between gap-3 border-t border-slate-100 pt-3 sm:flex-row sm:items-center">
                <p className="text-xs text-slate-500">
                  Menampilkan <span className="font-semibold text-slate-700">{startItem}</span> -{" "}
                  <span className="font-semibold text-slate-700">{endItem}</span> dari{" "}
                  <span className="font-semibold text-slate-700">{filteredRows.length}</span> data
                </p>

                <div className="flex items-center gap-1.5">
                  <button
                    disabled={validPage <= 1}
                    onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                    className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                    type="button"
                  >
                    <ChevronLeft size={14} />
                    <span>Sebelumnya</span>
                  </button>

                  <div className="flex items-center gap-1 px-2">
                    <span className="text-xs font-medium text-slate-700">
                      Halaman <span className="font-bold text-slate-900">{validPage}</span> dari{" "}
                      <span className="font-bold text-slate-900">{totalPages}</span>
                    </span>
                  </div>

                  <button
                    disabled={validPage >= totalPages}
                    onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                    className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                    type="button"
                  >
                    <span>Selanjutnya</span>
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
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
      setDownloadMessage(
        caughtError instanceof Error ? caughtError.message : "Unduhan hasil rapikan gagal."
      );
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

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div>
        <h2 className="text-base font-semibold text-slate-900">Rapikan Hasil Rekap</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          Pisahkan file berdasarkan Kode Kelas PAI dan Prodi, lalu urutkan data setiap sheet berdasarkan NIM.
        </p>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_auto]">
        <label
          className={`flex min-h-32 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-5 text-center transition ${
            isProcessing ? "cursor-not-allowed opacity-60" : "hover:border-blue-400 hover:bg-blue-50"
          }`}
          htmlFor={inputId}
        >
          <UploadCloud className="text-blue-700" size={32} />
          <p className="mt-2 text-sm font-semibold text-slate-700">
            {file?.name ?? "Upload file Excel hasil rekap"}
          </p>
          <p className="mt-1 text-xs text-slate-500">Format .xlsx atau .xls</p>
          <span className="mt-3 rounded-lg bg-blue-700 px-4 py-2 text-xs font-bold text-white">
            Pilih File
          </span>
          <input
            accept=".xlsx,.xls"
            className="sr-only"
            disabled={isProcessing}
            id={inputId}
            key={inputResetKey}
            onChange={(event) => handleFileChange(event.target.files?.[0] ?? null)}
            type="file"
          />
        </label>

        <div className="flex min-w-56 flex-col justify-center gap-2">
          <button
            className="flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            disabled={!canProcess}
            onClick={handleProcess}
            type="button"
          >
            {isProcessing ? (
              <LoaderCircle className="animate-spin" size={18} />
            ) : (
              <FileSpreadsheet size={18} />
            )}
            {isProcessing
              ? "Memproses..."
              : status === "error"
              ? "Coba Proses Lagi"
              : "Proses Rapikan"}
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
          Sedang membaca, mengelompokkan, dan merapikan data...
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
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl bg-blue-50 p-4">
              <p className="text-xs font-semibold text-blue-700">Total Data</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_data.toLocaleString("id-ID")}
              </p>
            </div>
            <div className="rounded-xl bg-emerald-50 p-4">
              <p className="text-xs font-semibold text-emerald-700">Total Sheet</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {result.summary.total_sheet.toLocaleString("id-ID")}
              </p>
            </div>
          </div>

          <PreviewTable rows={result.preview} title="Preview Data Gabungan" />
          <PreviewTable rows={result.sheet_preview} title="Preview Sheet yang Akan Dibuat" />
        </div>
      )}
    </section>
  );
}
