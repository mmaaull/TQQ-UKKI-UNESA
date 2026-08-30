"use client";

import { BookOpen, CheckCircle2, Download, FileSpreadsheet, Filter, Play, ShieldAlert, X } from "lucide-react";

export type GuideModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

const guideSteps = [
  {
    step: "1",
    title: "Upload File Peserta & Nilai",
    description:
      "Pilih file Excel Data Peserta dan File Nilai (.xlsx / .xls) sesuai dengan format kolom yang telah ditentukan.",
    icon: FileSpreadsheet,
    color: "bg-blue-50 text-blue-600 border-blue-100",
  },
  {
    step: "2",
    title: "Proses Rekap Data",
    description:
      "Klik tombol 'Proses Rekap Data'. Sistem akan mencocokkan NIM dan Nama secara otomatis serta menghitung statistik.",
    icon: Play,
    color: "bg-indigo-50 text-indigo-600 border-indigo-100",
  },
  {
    step: "3",
    title: "Tinjau Validasi & Data Bermasalah",
    description:
      "Periksa grafik kelengkapan nilai dan tabel 'Data Bermasalah' untuk mendeteksi NIM tidak ditemukan, nilai kosong, atau perbedaan nama.",
    icon: ShieldAlert,
    color: "bg-amber-50 text-amber-600 border-amber-100",
  },
  {
    step: "4",
    title: "Navigasi & Filter Hasil Rekap",
    description:
      "Gunakan pencarian atau filter kelas/prodi. Hasil rekap secara default menampilkan 10 data per halaman, atau klik 'Tampilkan Semua Data'.",
    icon: Filter,
    color: "bg-emerald-50 text-emerald-600 border-emerald-100",
  },
  {
    step: "5",
    title: "Export & Mode Rapikan",
    description:
      "Download hasil rekap Excel per kode kelas PAI, Laporan Validasi, atau gunakan 'Mode Rapikan' untuk memisahkan sheet per kelas & prodi.",
    icon: Download,
    color: "bg-sky-50 text-sky-600 border-sky-100",
  },
];

export function GuideModal({ isOpen, onClose }: GuideModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Card */}
      <div className="relative z-10 flex max-h-[90vh] w-full max-w-2xl flex-col rounded-3xl bg-white shadow-2xl overflow-hidden border border-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5 bg-gradient-to-r from-blue-50/50 to-white">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-2xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
              <BookOpen size={20} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Panduan Penggunaan</h2>
              <p className="text-xs font-medium text-slate-500">
                Sistem Rekap Nilai TQQ Akbar UNESA
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="grid size-9 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
            type="button"
            aria-label="Tutup panduan"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200/60">
            Ikuti 5 langkah sederhana berikut untuk mengelola dan merekap nilai peserta TQQ Akbar secara efisien dan akurat:
          </p>

          <div className="space-y-3">
            {guideSteps.map((item) => {
              const IconComponent = item.icon;
              return (
                <div
                  key={item.step}
                  className="flex items-start gap-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm hover:border-blue-100 transition-colors"
                >
                  <div className={`shrink-0 rounded-xl border p-2.5 ${item.color}`}>
                    <IconComponent size={20} />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex size-5 items-center justify-center rounded-full bg-slate-100 text-[10px] font-bold text-slate-600">
                        {item.step}
                      </span>
                      <h3 className="text-sm font-bold text-slate-900">{item.title}</h3>
                    </div>
                    <p className="mt-1 text-xs text-slate-500 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end border-t border-slate-100 bg-slate-50/80 px-6 py-4">
          <button
            onClick={onClose}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-bold text-white shadow-sm shadow-blue-500/20 hover:bg-blue-700 transition"
            type="button"
          >
            <CheckCircle2 size={16} />
            <span>Saya Mengerti</span>
          </button>
        </div>
      </div>
    </div>
  );
}
