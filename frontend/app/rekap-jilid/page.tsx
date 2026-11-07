import { BookMarked, UsersRound } from "lucide-react";

import { RekapJilidSection } from "@/components/RekapJilidSection";

export default function RekapJilidPage() {
  return (
    <main className="mx-auto max-w-[1440px] space-y-6 px-4 py-5 sm:px-8 sm:py-7 lg:px-10 lg:py-8">
      <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white px-5 py-6 shadow-sm sm:px-8 sm:py-8">
        <div className="relative z-10 max-w-3xl">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-[11px] font-bold text-blue-700">
            <BookMarked size={13} /> Fitur Rekap Jilid
          </div>
          <h1 className="text-3xl font-bold tracking-[-0.035em] text-slate-900 sm:text-4xl">
            Rekap Pembagian Kelas Jilid
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base sm:leading-7">
            Upload data master dan hasil tes tashih untuk membagi peserta ke kelas Jilid secara
            otomatis, lalu lanjutkan langsung ke pembagian tentor per kelas Jilid.
          </p>
        </div>
        <div className="pointer-events-none absolute -right-10 -top-14 hidden size-72 rounded-full border-[28px] border-blue-100/80 lg:block" />
        <div className="pointer-events-none absolute bottom-7 right-10 hidden rotate-[-8deg] rounded-2xl border border-blue-100 bg-blue-50 p-4 text-blue-600 shadow-lg shadow-blue-100/50 lg:block">
          <BookMarked size={52} strokeWidth={1.4} />
        </div>
        <div className="pointer-events-none absolute right-40 top-8 hidden rounded-xl bg-emerald-100 p-2.5 text-emerald-600 lg:block">
          <UsersRound size={23} />
        </div>
      </section>

      <RekapJilidSection />
    </main>
  );
}
