import { FileSpreadsheet, ShieldCheck, Sparkles } from "lucide-react";

import { ClassChart } from "@/components/ClassChart";
import { Navbar } from "@/components/Navbar";
import { ProcessCard } from "@/components/ProcessCard";
import { ProgressChart } from "@/components/ProgressChart";
import { RekapTable } from "@/components/RekapTable";
import { StatCard } from "@/components/StatCard";
import { UploadCard } from "@/components/UploadCard";
import { ValidationChart } from "@/components/ValidationChart";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { incompleteClasses, kpiItems, rekapRows, scoreProgress, validationItems, workflowSteps } from "@/lib/mock-data";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900">
      <Navbar />
      <main className="mx-auto max-w-[1440px] space-y-5 px-5 py-6 sm:px-8 lg:px-10 lg:py-8">
        <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white px-6 py-7 shadow-sm sm:px-8 sm:py-8">
          <div className="relative z-10 max-w-3xl">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-[11px] font-bold text-blue-700">
              <Sparkles size={13} /> Sistem manajemen rekap nilai
            </div>
            <h1 className="text-3xl font-bold tracking-[-0.03em] text-slate-900 sm:text-4xl">Rekap Nilai TQQ Akbar UNESA</h1>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-500">Kelola, validasi, dan rekap nilai peserta dengan mudah dan akurat.</p>
          </div>
          <div className="pointer-events-none absolute -right-10 -top-14 hidden size-72 rounded-full border-[28px] border-blue-100/80 lg:block" />
          <div className="pointer-events-none absolute bottom-7 right-10 hidden rotate-[-8deg] rounded-2xl border border-blue-100 bg-blue-50 p-4 text-blue-600 shadow-lg shadow-blue-100/50 lg:block"><FileSpreadsheet size={52} strokeWidth={1.4} /></div>
          <div className="pointer-events-none absolute right-40 top-8 hidden rounded-xl bg-emerald-100 p-2.5 text-emerald-600 lg:block"><ShieldCheck size={23} /></div>
        </section>

        <WorkflowStepper steps={workflowSteps} />

        <section className="grid gap-4 lg:grid-cols-3">
          <UploadCard kind="peserta" title="File Peserta" description="Upload file data peserta sesuai format" />
          <UploadCard kind="nilai" title="File Nilai" description="Upload file nilai peserta sesuai format" />
          <ProcessCard />
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpiItems.map((item) => <StatCard item={item} key={item.label} />)}
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <ProgressChart completion="91,3%" data={scoreProgress} lastProcessed="12 Agustus 2026 • 15:42 WIB" needsReview={{ value: 23, percentage: "1,8" }} />
          <ClassChart data={incompleteClasses} />
          <ValidationChart data={validationItems} total={23} />
        </section>

        <RekapTable rows={rekapRows} />
      </main>
      <footer className="mt-6 border-t border-slate-200 bg-white py-6 text-xs text-slate-500">
        <div className="mx-auto flex max-w-[1440px] flex-col justify-between gap-3 px-5 sm:flex-row sm:px-8 lg:px-10"><p>© 2026 UKKI UNESA — Sistem Manajemen Akademik</p><div className="flex gap-6"><button type="button">Kebijakan Privasi</button><button type="button">Bantuan</button></div></div>
      </footer>
    </div>
  );
}
