"use client";

import { FileSpreadsheet, ShieldCheck, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";

import { ClassChart } from "@/components/ClassChart";
import { ClassDetailModal } from "@/components/ClassDetailModal";
import { ExportSection } from "@/components/ExportSection";
import { ProblemTable } from "@/components/ProblemTable";
import { ProcessCard } from "@/components/ProcessCard";
import { ProgressChart } from "@/components/ProgressChart";
import { RapikanSection } from "@/components/RapikanSection";
import { RekapTable } from "@/components/RekapTable";
import { StatCard } from "@/components/StatCard";
import { UploadCard } from "@/components/UploadCard";
import { ValidationChart } from "@/components/ValidationChart";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import {
  makeKpiItems,
  makeScoreProgress,
  mapClassProgress,
  mapRekapRows,
  mapValidationItems,
  processRekap,
} from "@/lib/api";
import { workflowSteps } from "@/lib/workflow";
import type { ProcessStatus, RekapProcessResponse, Summary } from "@/types/dashboard";

const emptySummary: Summary = {
  total_peserta: 0,
  sudah_ada_nilai: 0,
  belum_ada_nilai: 0,
  perlu_dicek: 0,
  persentase_selesai: 0,
};

function formatProcessedAt(): string {
  return new Intl.DateTimeFormat("id-ID", {
    dateStyle: "long",
    timeStyle: "short",
  }).format(new Date());
}

export default function RekapNilaiPage() {
  const [pesertaFile, setPesertaFile] = useState<File | null>(null);
  const [nilaiFile, setNilaiFile] = useState<File | null>(null);
  const [status, setStatus] = useState<ProcessStatus>("idle");
  const [error, setError] = useState("");
  const [result, setResult] = useState<RekapProcessResponse | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [processedAt, setProcessedAt] = useState("");
  const [uploadResetKey, setUploadResetKey] = useState(0);

  const [isClassDetailOpen, setIsClassDetailOpen] = useState(false);

  const summary = result?.summary ?? emptySummary;
  const kpiItems = useMemo(() => makeKpiItems(summary), [summary]);
  const scoreProgress = useMemo(() => makeScoreProgress(summary), [summary]);
  const rekapRows = useMemo(() => mapRekapRows(result?.rekap ?? []), [result]);
  const classProgress = useMemo(() => mapClassProgress(result?.ringkasan_kelas ?? []), [result]);
  const validationItems = useMemo(() => mapValidationItems(result?.ringkasan_masalah ?? []), [result]);
  const isProcessing = status === "processing";
  const hasDashboard = status === "success" && result !== null;

  const currentStep = useMemo(() => {
    if (status === "processing") return 2;
    if (status === "success" && result !== null) return 3;
    return 1;
  }, [status, result]);

  function resetResultState() {
    setError("");
    setResult(null);
    setSessionId(null);
    setProcessedAt("");
  }

  function setSelectedFile(kind: "peserta" | "nilai", file: File | null) {
    const nextPesertaFile = kind === "peserta" ? file : pesertaFile;
    const nextNilaiFile = kind === "nilai" ? file : nilaiFile;
    setPesertaFile(nextPesertaFile);
    setNilaiFile(nextNilaiFile);
    resetResultState();
    setStatus(nextPesertaFile && nextNilaiFile ? "ready" : "idle");
  }

  function handleReset() {
    setPesertaFile(null);
    setNilaiFile(null);
    setUploadResetKey((value) => value + 1);
    resetResultState();
    setStatus("idle");
  }

  function handleRetry() {
    setError("");
    setStatus(pesertaFile && nilaiFile ? "ready" : "idle");
  }

  async function handleProcess() {
    if (!pesertaFile || !nilaiFile || status !== "ready") return;

    setError("");
    setStatus("processing");

    try {
      const response = await processRekap(pesertaFile, nilaiFile);
      setResult(response);
      setSessionId(response.session_id);
      setProcessedAt(formatProcessedAt());
      setStatus("success");
    } catch (caughtError) {
      setStatus("error");
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Terjadi kesalahan saat memproses rekap."
      );
    }
  }

  return (
    <>
      <ClassDetailModal
        isOpen={isClassDetailOpen}
        onClose={() => setIsClassDetailOpen(false)}
        data={classProgress}
      />

      <main className="mx-auto max-w-[1440px] space-y-6 px-4 py-5 sm:px-8 sm:py-7 lg:px-10 lg:py-8">
        <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white px-5 py-6 shadow-sm sm:px-8 sm:py-8">
          <div className="relative z-10 max-w-3xl">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-[11px] font-bold text-blue-700">
              <Sparkles size={13} /> Fitur Rekap Nilai
            </div>
            <h1 className="text-3xl font-bold tracking-[-0.035em] text-slate-900 sm:text-4xl">
              Rekap Nilai TQQ Akbar UNESA
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base sm:leading-7">
              Kelola, validasi, dan rekap nilai peserta dengan mudah dan akurat.
            </p>
          </div>
          <div className="pointer-events-none absolute -right-10 -top-14 hidden size-72 rounded-full border-[28px] border-blue-100/80 lg:block" />
          <div className="pointer-events-none absolute bottom-7 right-10 hidden rotate-[-8deg] rounded-2xl border border-blue-100 bg-blue-50 p-4 text-blue-600 shadow-lg shadow-blue-100/50 lg:block">
            <FileSpreadsheet size={52} strokeWidth={1.4} />
          </div>
          <div className="pointer-events-none absolute right-40 top-8 hidden rounded-xl bg-emerald-100 p-2.5 text-emerald-600 lg:block">
            <ShieldCheck size={23} />
          </div>
        </section>

        <WorkflowStepper steps={workflowSteps} activeStep={currentStep} />

        <section className="grid gap-4 lg:grid-cols-3">
          <UploadCard
            disabled={isProcessing}
            key={`peserta-${uploadResetKey}`}
            kind="peserta"
            title="File Peserta"
            description="Kolom: Nama, Jenis Kelamin, NIM, Kelas PAI, Program Studi"
            onFileChange={(file) => setSelectedFile("peserta", file)}
          />
          <UploadCard
            disabled={isProcessing}
            key={`nilai-${uploadResetKey}`}
            kind="nilai"
            title="File Nilai"
            description="Upload file nilai peserta sesuai format"
            onFileChange={(file) => setSelectedFile("nilai", file)}
          />
          <ProcessCard
            error={error}
            onProcess={handleProcess}
            onReset={handleReset}
            onRetry={handleRetry}
            status={status}
          />
        </section>

        {sessionId && (
          <p className="break-all rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 shadow-sm">
            Rekap berhasil disimpan dalam sesi:{" "}
            <span className="font-mono text-xs font-semibold">{sessionId}</span>
          </p>
        )}

        {hasDashboard ? (
          <>
            <section className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
                {kpiItems.map((item) => (
                  <StatCard item={item} key={item.label} />
                ))}
              </div>

              <div className="grid gap-4 lg:grid-cols-3">
                <ProgressChart
                  completion={`${summary.persentase_selesai.toLocaleString("id-ID", {
                    maximumFractionDigits: 1,
                  })}%`}
                  data={scoreProgress}
                  lastProcessed={processedAt}
                  needsReview={{
                    value: summary.perlu_dicek,
                    percentage: (summary.total_peserta
                      ? (summary.perlu_dicek / summary.total_peserta) * 100
                      : 0
                    ).toLocaleString("id-ID", { maximumFractionDigits: 1 }),
                  }}
                />
                <ClassChart
                  data={classProgress}
                  onViewAll={() => setIsClassDetailOpen(true)}
                />
                <ValidationChart
                  data={validationItems}
                  total={summary.perlu_dicek}
                  onViewDetails={() => {
                    const element = document.getElementById("validasi-section");
                    if (element) {
                      element.scrollIntoView({ behavior: "smooth" });
                    }
                  }}
                />
              </div>
            </section>

            <RekapTable
              rows={rekapRows}
              subtitle={`Menampilkan ${rekapRows.length} data hasil rekap`}
            />

            <div id="validasi-section">
              <ProblemTable rows={result.data_bermasalah} />
            </div>
          </>
        ) : (
          <section className="rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-10 text-center shadow-sm">
            <FileSpreadsheet className="mx-auto text-slate-400" size={28} />
            <p className="mt-3 text-sm font-semibold text-slate-700">Dashboard belum tersedia</p>
            <p className="mx-auto mt-1 max-w-md text-sm leading-6 text-slate-500">
              Pilih kedua file Excel lalu proses rekap untuk menampilkan ringkasan, grafik, dan hasil validasi.
            </p>
          </section>
        )}

        <ExportSection sessionId={sessionId} />

        <RapikanSection />
      </main>
    </>
  );
}
