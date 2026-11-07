"use client";

import {
  AlertCircle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  LoaderCircle,
  RotateCcw,
  Search,
  UploadCloud,
  X,
} from "lucide-react";
import { useId, useMemo, useState } from "react";

import { buildCariMahasiswaIndex } from "@/lib/api";
import type { CariMahasiswaIndexResponse, CariMahasiswaRow } from "@/types/dashboard";

const ITEMS_PER_PAGE = 10;

function normalizeText(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
}

function matchesQuery(row: CariMahasiswaRow, query: string, tokens: string[]): boolean {
  if (row.nim.includes(query.replace(/\s+/g, ""))) return true;
  const nama = normalizeText(row.nama);
  return tokens.length > 0 && tokens.every((token) => nama.includes(token));
}

function isUrl(value: string): boolean {
  return /^https?:\/\//i.test(value);
}

function CellValue({ value }: { value: string | undefined }) {
  if (!value) return <>-</>;
  if (!isUrl(value)) return <>{value}</>;
  return (
    <a
      className="inline-flex items-center gap-1 font-semibold text-blue-700 hover:underline"
      href={value}
      rel="noopener noreferrer"
      target="_blank"
    >
      Buka <ExternalLink size={12} />
    </a>
  );
}

export function CariMahasiswaSection() {
  const inputId = useId();
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [index, setIndex] = useState<CariMahasiswaIndexResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [inputResetKey, setInputResetKey] = useState(0);
  const hasFiles = files.length > 0;

  const trimmedQuery = query.trim();
  const results = useMemo(() => {
    if (!index || !trimmedQuery) return [];
    const tokens = normalizeText(trimmedQuery).split(" ").filter(Boolean);
    return index.mahasiswa.filter((row) => matchesQuery(row, trimmedQuery, tokens));
  }, [index, trimmedQuery]);

  // Kolom dihitung dari semua hasil (bukan per halaman) supaya tabel tidak berubah bentuk saat pindah halaman.
  const dataColumns = (index?.data_columns ?? []).filter((column) => results.some((row) => row.data[column]));
  const infoColumns = (index?.info_columns ?? []).filter((column) => results.some((row) => row.info[column]));
  const totalPages = Math.max(1, Math.ceil(results.length / ITEMS_PER_PAGE));
  const validPage = Math.min(currentPage, totalPages);
  const startIndex = (validPage - 1) * ITEMS_PER_PAGE;
  const shownRows = results.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  const showSource = (index?.summary.total_file ?? 0) > 1;

  async function handleFileChange(selected: File[]) {
    setFiles(selected);
    setIndex(null);
    setError("");
    setQuery("");
    setCurrentPage(1);
    if (selected.length === 0) return;
    setLoading(true);
    try {
      setIndex(await buildCariMahasiswaIndex(selected));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Membaca file kelas gagal.");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setFiles([]);
    setIndex(null);
    setError("");
    setQuery("");
    setInputResetKey((value) => value + 1);
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div>
        <h2 className="text-base font-semibold text-slate-900">Cari Mahasiswa di File Excel</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          Upload satu atau beberapa file Excel yang berisi data mahasiswa (boleh banyak sheet, mis.
          satu sheet per kelas) lalu cari mahasiswa yang komplain berdasarkan NIM atau Nama. Sistem
          mencari otomatis di semua sheet dan menampilkan semua kolom yang ada di file, tanpa perlu
          membuka sheet satu per satu.
        </p>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <div key={`cari-${inputResetKey}`}>
          <label
            className={`flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-5 text-center transition ${
              loading
                ? "cursor-not-allowed border-slate-200 bg-slate-50 opacity-60"
                : isDragging
                  ? "border-blue-500 bg-blue-50 ring-2 ring-blue-500/20"
                  : hasFiles
                    ? "border-emerald-300 bg-emerald-50/70 hover:border-emerald-400"
                    : "border-slate-200 bg-slate-50 hover:border-blue-400 hover:bg-blue-50"
            }`}
            htmlFor={inputId}
            onDragLeave={() => setIsDragging(false)}
            onDragOver={(event) => {
              event.preventDefault();
              if (!loading) setIsDragging(true);
            }}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragging(false);
              if (loading) return;
              const droppedFiles = Array.from(event.dataTransfer.files ?? []);
              if (droppedFiles.length > 0) handleFileChange(droppedFiles);
            }}
          >
            {loading ? (
              <LoaderCircle className="animate-spin text-blue-700" size={28} />
            ) : hasFiles ? (
              <CheckCircle2 className="text-emerald-600" size={28} />
            ) : (
              <UploadCloud className="text-blue-700" size={28} />
            )}
            <p
              className={`mt-2 max-w-full truncate px-2 text-sm font-semibold ${
                hasFiles ? "text-emerald-800" : "text-slate-700"
              }`}
              title={files.length === 1 ? files[0].name : undefined}
            >
              {files.length === 0
                ? "Upload file Excel"
                : files.length === 1
                  ? files[0].name
                  : `${files.length} file dipilih`}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {hasFiles
                ? "Indeks siap dicari • Klik atau tarik untuk mengganti"
                : "Format .xlsx/.xls, minimal ada kolom NIM atau Nama"}
            </p>
            <span
              className={`mt-3 rounded-lg px-4 py-2 text-xs font-bold text-white shadow-sm transition ${
                hasFiles ? "bg-emerald-600 hover:bg-emerald-700" : "bg-blue-700 hover:bg-blue-800"
              }`}
            >
              {loading ? "Membaca..." : hasFiles ? "Ganti File" : "Pilih File"}
            </span>
            <input
              accept=".xlsx,.xls"
              className="sr-only"
              disabled={loading}
              id={inputId}
              multiple
              onChange={(event) => handleFileChange(Array.from(event.target.files ?? []))}
              type="file"
            />
          </label>
          {files.length > 0 && (
            <button
              className="mt-2 flex items-center gap-2 px-1 py-1 text-xs font-semibold text-slate-600 hover:text-blue-700"
              onClick={handleReset}
              type="button"
            >
              <RotateCcw size={14} />
              Mulai File Baru
            </button>
          )}
        </div>

        <div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative min-w-56 flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input
                aria-label="Cari mahasiswa berdasarkan NIM atau Nama"
                className="w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-9 pr-9 text-sm text-slate-800 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-50"
                disabled={!index}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setCurrentPage(1);
                }}
                placeholder={index ? "Ketik NIM atau nama mahasiswa..." : "Upload file terlebih dahulu"}
                type="search"
                value={query}
              />
              {query && (
                <button
                  aria-label="Hapus pencarian"
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-slate-400 hover:text-slate-700"
                  onClick={() => setQuery("")}
                  type="button"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          {index && (
            <p className="mt-2 text-xs text-slate-500">
              {index.summary.total_mahasiswa.toLocaleString("id-ID")} mahasiswa dari{" "}
              {index.summary.total_sheet.toLocaleString("id-ID")} sheet siap dicari.
            </p>
          )}
        </div>
      </div>

      {error && (
        <p className="mt-4 flex items-center gap-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertCircle size={16} />
          {error}
        </p>
      )}

      {index && trimmedQuery && (
        <div className="mt-5">
          <p className="mb-2 text-sm font-semibold text-slate-800">
            {results.length === 0
              ? `Tidak ada mahasiswa yang cocok dengan "${trimmedQuery}".`
              : `${results.length.toLocaleString("id-ID")} hasil ditemukan`}
          </p>
          {results.length > 0 && (
            <div className="overflow-x-auto rounded-xl border border-slate-200">
              <table className="min-w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    {[
                      "No",
                      ...(showSource ? ["File"] : []),
                      "Sheet",
                      "NIM",
                      "Nama",
                      ...dataColumns,
                      ...infoColumns,
                    ].map((heading) => (
                      <th className="whitespace-nowrap px-3 py-2 font-semibold" key={heading}>
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {shownRows.map((row, rowIndex) => (
                    <tr className="hover:bg-blue-50/40" key={`${row.sumber}-${row.sheet}-${row.nim}-${rowIndex}`}>
                      <td className="whitespace-nowrap px-3 py-2 text-slate-500">{startIndex + rowIndex + 1}</td>
                      {showSource && <td className="px-3 py-2 text-slate-600">{row.sumber}</td>}
                      <td className="whitespace-nowrap px-3 py-2">
                        <span className="rounded-md bg-blue-100 px-2 py-0.5 font-bold text-blue-800">{row.sheet}</span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-2 font-mono text-slate-800">{row.nim || "-"}</td>
                      <td className="px-3 py-2 font-semibold text-slate-900">{row.nama || "-"}</td>
                      {dataColumns.map((column) => (
                        <td className="px-3 py-2 text-slate-700" key={`d-${column}`}>
                          <CellValue value={row.data[column]} />
                        </td>
                      ))}
                      {infoColumns.map((column) => (
                        <td className="px-3 py-2 text-slate-700" key={`i-${column}`}>
                          <CellValue value={row.info[column]} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {totalPages > 1 && (
            <div className="mt-3 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
              <p className="text-xs text-slate-500">
                Menampilkan <span className="font-semibold text-slate-700">{startIndex + 1}</span> -{" "}
                <span className="font-semibold text-slate-700">{startIndex + shownRows.length}</span> dari{" "}
                <span className="font-semibold text-slate-700">{results.length.toLocaleString("id-ID")}</span> data
              </p>
              <div className="flex items-center gap-1.5">
                <button
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                  disabled={validPage <= 1}
                  onClick={() => setCurrentPage(validPage - 1)}
                  type="button"
                >
                  <ChevronLeft size={14} />
                  <span>Sebelumnya</span>
                </button>
                <span className="px-2 text-xs font-medium text-slate-700">
                  Halaman <span className="font-bold text-slate-900">{validPage}</span> dari{" "}
                  <span className="font-bold text-slate-900">{totalPages}</span>
                </span>
                <button
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                  disabled={validPage >= totalPages}
                  onClick={() => setCurrentPage(validPage + 1)}
                  type="button"
                >
                  <span>Selanjutnya</span>
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
