import { CheckCircle2, LoaderCircle, LockKeyhole, Play, RotateCcw, TriangleAlert } from "lucide-react";

import type { ProcessStatus, RekapGroupBy } from "@/types/dashboard";

export type ProcessCardProps = {
  error?: string;
  onProcess?: () => void;
  onReset?: () => void;
  onRetry?: () => void;
  groupBy: RekapGroupBy | null;
  onGroupByChange: (value: RekapGroupBy) => void;
  status?: ProcessStatus;
};

const statusLabel: Record<ProcessStatus, string> = {
  idle: "Pilih Kedua File",
  ready: "Proses Rekap & Validasi",
  processing: "Memproses Rekap...",
  success: "Rekap Berhasil Diproses",
  error: "Perbaiki atau Coba Lagi",
};

export function ProcessCard({ error, groupBy, onGroupByChange, onProcess, onReset, onRetry, status = "idle" }: ProcessCardProps) {
  const inProgress = status === "processing";
  const canProcess = status === "ready" && groupBy !== null;
  const canChooseGroup = status === "ready" || status === "success" || status === "error";
  const isPlayIcon = status === "idle" || status === "ready";
  const Icon = inProgress
    ? LoaderCircle
    : status === "success"
      ? CheckCircle2
      : status === "error"
        ? TriangleAlert
        : Play;

  return (
    <article className="flex min-h-[292px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div>
        <h2 className="text-base font-semibold text-slate-900">Pilih Jenis Rekap</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          Upload kedua file, lalu pilih pengelompokan hasil Excel.
        </p>
      </div>

      <div className="flex flex-1 flex-col justify-center">
        <fieldset className="mb-4 space-y-2" disabled={!canChooseGroup}>
          <legend className="mb-2 text-xs font-semibold text-slate-700">Sheet Excel berdasarkan</legend>
          {([
            { value: "prodi", label: "Prodi" },
            { value: "kode_kelas_pai", label: "Kode Kelas PAI" },
          ] as const).map((option) => (
            <label
              className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition ${
                groupBy === option.value
                  ? "border-blue-600 bg-blue-50 text-blue-800"
                  : "border-slate-200 text-slate-700 hover:border-blue-300"
              } ${!canChooseGroup ? "cursor-not-allowed opacity-50" : ""}`}
              key={option.value}
            >
              <input
                checked={groupBy === option.value}
                className="accent-blue-700"
                name="rekap-group-by"
                onChange={() => onGroupByChange(option.value)}
                type="radio"
                value={option.value}
              />
              Rekap berdasarkan {option.label}
            </label>
          ))}
        </fieldset>
        <button
          className={`flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold shadow-sm transition ${
            canProcess
              ? "bg-blue-700 text-white hover:bg-blue-800 hover:shadow-blue-200"
              : "cursor-not-allowed bg-slate-200 text-slate-400"
          }`}
          disabled={!canProcess}
          onClick={onProcess}
          type="button"
        >
          <Icon
            className={inProgress ? "animate-spin" : ""}
            fill={isPlayIcon ? "currentColor" : "none"}
            size={19}
          />
          {statusLabel[status]}
        </button>

        {error ? (
          <div className="mt-4 space-y-2">
            <p className="flex items-start gap-2 rounded-lg bg-red-50 px-3 py-2 text-xs leading-5 text-red-700">
              <TriangleAlert className="mt-0.5 shrink-0" size={15} />
              {error}
            </p>
            <button
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-red-200 py-2 text-xs font-bold text-red-700 transition hover:bg-red-50"
              onClick={onRetry}
              type="button"
            >
              <RotateCcw size={14} />
              Coba Lagi
            </button>
          </div>
        ) : status === "success" ? (
          <div className="mt-4 space-y-2">
            <p className="flex items-start gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-xs leading-5 text-emerald-700">
              <CheckCircle2 className="mt-0.5 shrink-0" size={15} />
              Rekap berhasil diproses.
            </p>
            <button
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 py-2 text-xs font-bold text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
              onClick={onReset}
              type="button"
            >
              <RotateCcw size={14} />
              Ganti File & Proses Baru
            </button>
          </div>
        ) : inProgress ? (
          <p className="mt-4 flex items-start gap-2 rounded-lg bg-blue-50 px-3 py-2 text-xs leading-5 text-blue-700">
            <LoaderCircle className="mt-0.5 shrink-0 animate-spin" size={15} />
            Mohon tunggu, data sedang diproses.
          </p>
        ) : (
          <p className="mt-4 flex items-start gap-2 text-xs leading-5 text-slate-500">
            <LockKeyhole className="mt-0.5 shrink-0" size={15} />
            {status === "ready"
              ? groupBy
                ? "Jenis rekap sudah dipilih. Klik tombol untuk memproses kedua file."
                : "Pilih jenis rekap untuk mengaktifkan tombol proses."
              : "Tombol akan aktif setelah kedua file diunggah dan jenis rekap dipilih."}
          </p>
        )}
      </div>
    </article>
  );
}
