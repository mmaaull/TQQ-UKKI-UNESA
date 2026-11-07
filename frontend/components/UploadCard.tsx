"use client";

import { CheckCircle2, FileSpreadsheet, UploadCloud, UsersRound } from "lucide-react";
import { useId, useState } from "react";

export type UploadCardProps = {
  kind: "peserta" | "nilai";
  title: string;
  description: string;
  disabled?: boolean;
  onFileChange?: (file: File | null) => void;
};

export function UploadCard({
  kind,
  title,
  description,
  disabled = false,
  onFileChange,
}: UploadCardProps) {
  const inputId = useId();
  const [fileName, setFileName] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const isPeserta = kind === "peserta";
  const Icon = isPeserta ? UsersRound : FileSpreadsheet;
  const hasFile = Boolean(fileName);

  const iconAccent = isPeserta ? "bg-blue-100 text-blue-700" : "bg-emerald-100 text-emerald-700";
  const hoverAccent = isPeserta
    ? "hover:border-blue-400 hover:bg-blue-50 text-blue-700"
    : "hover:border-emerald-500 hover:bg-emerald-50 text-emerald-700";
  const dragAccent = isPeserta
    ? "border-blue-500 bg-blue-50 text-blue-700 ring-2 ring-blue-500/20"
    : "border-emerald-500 bg-emerald-50 text-emerald-700 ring-2 ring-emerald-500/20";
  const button = isPeserta
    ? "bg-blue-700 hover:bg-blue-800"
    : "bg-emerald-600 hover:bg-emerald-700";

  function handleSelect(file: File | null) {
    setFileName(file?.name ?? "");
    onFileChange?.(file);
  }

  return (
    <article className="flex min-h-[292px] flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-center gap-4">
        <div className={`grid size-12 shrink-0 place-items-center rounded-full ${iconAccent}`}>
          <Icon size={23} />
        </div>
        <div>
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <p className="mt-1 text-xs leading-5 text-slate-500">{description}</p>
        </div>
      </div>

      <label
        className={`mt-5 flex flex-1 flex-col items-center justify-center rounded-xl border-2 border-dashed p-5 text-center transition ${
          disabled
            ? "cursor-not-allowed border-slate-200 bg-slate-50 opacity-60"
            : isDragging
              ? `cursor-pointer ${dragAccent}`
              : hasFile
                ? "cursor-pointer border-emerald-300 bg-emerald-50/80 text-emerald-700 hover:border-emerald-400"
                : `cursor-pointer border-slate-200 bg-slate-50 ${hoverAccent}`
        }`}
        htmlFor={inputId}
        onDragLeave={() => setIsDragging(false)}
        onDragOver={(event) => {
          event.preventDefault();
          if (!disabled) setIsDragging(true);
        }}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          if (disabled) return;
          const droppedFile = event.dataTransfer.files?.[0] ?? null;
          if (droppedFile) handleSelect(droppedFile);
        }}
      >
        {hasFile ? (
          <CheckCircle2 size={38} strokeWidth={1.7} />
        ) : (
          <UploadCloud size={38} strokeWidth={1.6} />
        )}
        <p className="mt-3 text-sm font-semibold text-slate-700">
          {hasFile ? "File siap diproses" : "Klik atau tarik file Excel ke sini"}
        </p>
        <span className="mt-1 text-xs text-slate-500">
          {hasFile ? "Klik atau tarik file baru untuk mengganti" : "Format .xlsx atau .xls"}
        </span>
        <span
          className={`mt-3 rounded-lg px-4 py-2 text-xs font-bold text-white shadow-sm transition ${
            hasFile ? "bg-emerald-600 hover:bg-emerald-700" : button
          }`}
        >
          {hasFile ? "Ganti File" : "Pilih File"}
        </span>
        <input
          accept=".xlsx,.xls"
          className="sr-only"
          disabled={disabled}
          id={inputId}
          onChange={(event) => handleSelect(event.target.files?.[0] ?? null)}
          type="file"
        />
      </label>

      <p
        className={`mt-3 truncate text-center text-xs font-medium ${
          hasFile ? "text-emerald-700 font-semibold" : "text-slate-500"
        }`}
        title={fileName || undefined}
      >
        {fileName || "Maksimum ukuran file 50MB"}
      </p>
    </article>
  );
}
