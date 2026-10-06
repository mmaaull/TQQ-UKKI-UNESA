import { ClipboardCheck } from "lucide-react";

import { KehadiranSection } from "@/components/KehadiranSection";

export default function KehadiranPage() {
  return (
    <main className="mx-auto max-w-[1440px] space-y-6 px-4 py-5 sm:px-8 sm:py-7 lg:px-10 lg:py-8">
      <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white px-5 py-6 shadow-sm sm:px-8 sm:py-8">
        <div className="relative z-10 max-w-3xl">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-[11px] font-bold text-blue-700">
            <ClipboardCheck size={13} /> Fitur Kehadiran
          </div>
          <h1 className="text-3xl font-bold tracking-[-0.035em] text-slate-900 sm:text-4xl">
            Keterangan Kehadiran Peserta
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base sm:leading-7">
            Upload rekap kehadiran dan file pembagian kelas. Setiap peserta di pembagian kelas akan
            diberi kolom Hadir / Tidak Hadir di sisi kanan, mengikuti data rekap kehadiran.
          </p>
        </div>
      </section>

      <KehadiranSection />
    </main>
  );
}
