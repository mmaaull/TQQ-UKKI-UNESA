"use client";

import {
  BookMarked,
  BookOpen,
  CheckCircle2,
  ClipboardCheck,
  Download,
  FileSpreadsheet,
  Filter,
  Play,
  Search,
  ShieldAlert,
  Users,
  X,
} from "lucide-react";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export type GuideModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

type GuideTabKey = "rekap-nilai" | "rekap-jilid" | "kehadiran";

type GuideStep = {
  step: string;
  title: string;
  description: string;
  icon: typeof FileSpreadsheet;
  color: string;
};

const guideTabs: Record<
  GuideTabKey,
  { label: string; intro: string; steps: GuideStep[] }
> = {
  "rekap-nilai": {
    label: "Rekap Nilai",
    intro:
      "Ikuti 5 langkah berikut untuk mengelola, memvalidasi, dan merekap nilai peserta TQQ Akbar secara akurat:",
    steps: [
      {
        step: "1",
        title: "Upload File Peserta & Nilai",
        description:
          "Pilih atau tarik file Excel Data Peserta dan File Nilai (.xlsx / .xls) sesuai dengan format kolom yang ditentukan.",
        icon: FileSpreadsheet,
        color: "bg-blue-50 text-blue-600 border-blue-100",
      },
      {
        step: "2",
        title: "Proses Rekap & Validasi",
        description:
          "Klik tombol 'Proses Rekap & Validasi'. Sistem akan mencocokkan NIM dan Nama secara otomatis serta menghitung statistik.",
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
          "Gunakan pencarian atau filter kelas/prodi. Hasil rekap menampilkan 10 data per halaman, atau klik 'Tampilkan Semua Data'.",
        icon: Filter,
        color: "bg-emerald-50 text-emerald-600 border-emerald-100",
      },
      {
        step: "5",
        title: "Export & Mode Rapikan",
        description:
          "Unduh hasil rekap Excel final, laporan validasi, arsip ZIP per kelas, atau gunakan 'Rapikan Hasil Rekap' untuk memisahkan sheet per kelas & prodi.",
        icon: Download,
        color: "bg-sky-50 text-sky-600 border-sky-100",
      },
    ],
  },
  "rekap-jilid": {
    label: "Rekap Jilid & Tentor",
    intro:
      "Gunakan halaman Rekap Jilid untuk membagi kelas Jilid 1–4 dari hasil tes tashih, mengalokasikan tentor, dan mencari mahasiswa lintas sheet:",
    steps: [
      {
        step: "1",
        title: "Upload File Master & Penilaian Tashih",
        description:
          "Unggah File Master (data keseluruhan peserta beserta Jenis Kelamin) dan File Penilaian Tashih yang berisi NIM serta Total Nilai.",
        icon: FileSpreadsheet,
        color: "bg-blue-50 text-blue-600 border-blue-100",
      },
      {
        step: "2",
        title: "Klasifikasi Kelas Jilid Otomatis",
        description:
          "Klik 'Proses Rekap Jilid'. Peserta dikelompokkan ke Jilid 1–4 berdasarkan nilai dan dipisah Laki-laki/Perempuan. Peserta kelas terkait yang belum tes otomatis masuk Jilid 1.",
        icon: BookMarked,
        color: "bg-indigo-50 text-indigo-600 border-indigo-100",
      },
      {
        step: "3",
        title: "Pembagian Tentor Proporsional",
        description:
          "Masukkan jumlah tentor Laki-laki dan Perempuan. Sistem otomatis memakai hasil Rekap Jilid di atas (atau file unggahan) dan membagi peserta serata mungkin per kelas Jilid.",
        icon: Users,
        color: "bg-emerald-50 text-emerald-600 border-emerald-100",
      },
      {
        step: "4",
        title: "Cari Mahasiswa di File Excel",
        description:
          "Unggah satu atau beberapa file Excel pembagian kelas, lalu ketik NIM atau Nama untuk menemukan posisi sheet, kelas, tentor, dan tautan grup WA secara instan.",
        icon: Search,
        color: "bg-sky-50 text-sky-600 border-sky-100",
      },
    ],
  },
  kehadiran: {
    label: "Kehadiran",
    intro:
      "Gunakan halaman Kehadiran untuk menambahkan kolom status Hadir / Tidak Hadir pada file pembagian kelas secara otomatis:",
    steps: [
      {
        step: "1",
        title: "Upload Rekap Kehadiran & Pembagian Kelas",
        description:
          "Pilih File Rekap Kehadiran (berisi NIM dan status kehadiran) serta File Pembagian Kelas (.xlsx) yang memiliki sheet per kelas.",
        icon: FileSpreadsheet,
        color: "bg-blue-50 text-blue-600 border-blue-100",
      },
      {
        step: "2",
        title: "Pencocokan NIM Otomatis",
        description:
          "Klik 'Proses Kehadiran'. Setiap peserta di sheet pembagian kelas dicocokkan berdasarkan NIM. Peserta yang tidak ada di rekap kehadiran otomatis ditandai Tidak Hadir.",
        icon: ClipboardCheck,
        color: "bg-emerald-50 text-emerald-600 border-emerald-100",
      },
      {
        step: "3",
        title: "Tinjau Ringkasan & Download Hasil",
        description:
          "Periksa statistik kehadiran per kelas serta daftar peserta yang belum tercatat di rekap, lalu klik 'Download Hasil' untuk mengunduh file Excel pembagian kelas yang sudah dilengkapi kolom kehadiran.",
        icon: Download,
        color: "bg-sky-50 text-sky-600 border-sky-100",
      },
    ],
  },
};

export function GuideModal({ isOpen, onClose }: GuideModalProps) {
  const pathname = usePathname();
  const [activeTab, setActiveTab] = useState<GuideTabKey>("rekap-nilai");

  useEffect(() => {
    if (!isOpen) return;
    if (pathname?.startsWith("/rekap-jilid")) {
      setActiveTab("rekap-jilid");
    } else if (pathname?.startsWith("/kehadiran")) {
      setActiveTab("kehadiran");
    } else {
      setActiveTab("rekap-nilai");
    }
  }, [isOpen, pathname]);

  if (!isOpen) return null;

  const currentGuide = guideTabs[activeTab];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Card */}
      <div className="relative z-10 flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 bg-gradient-to-r from-blue-50/50 to-white px-6 py-5">
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
            aria-label="Tutup panduan"
            className="grid size-9 place-items-center rounded-full text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            onClick={onClose}
            type="button"
          >
            <X size={18} />
          </button>
        </div>

        {/* Feature Tabs */}
        <div className="flex gap-1.5 border-b border-slate-100 bg-slate-50/70 px-6 py-2.5">
          {(Object.keys(guideTabs) as GuideTabKey[]).map((key) => {
            const isSelected = activeTab === key;
            return (
              <button
                className={`rounded-xl px-3.5 py-2 text-xs font-bold transition ${
                  isSelected
                    ? "bg-blue-600 text-white shadow-sm shadow-blue-500/20"
                    : "text-slate-600 hover:bg-slate-200/60 hover:text-slate-900"
                }`}
                key={key}
                onClick={() => setActiveTab(key)}
                type="button"
              >
                {guideTabs[key].label}
              </button>
            );
          })}
        </div>

        {/* Body Content */}
        <div className="flex-1 space-y-4 overflow-y-auto p-6">
          <p className="rounded-xl border border-slate-200/60 bg-slate-50 p-3.5 text-xs leading-relaxed text-slate-600">
            {currentGuide.intro}
          </p>

          <div className="space-y-3">
            {currentGuide.steps.map((item) => {
              const IconComponent = item.icon;
              return (
                <div
                  className="flex items-start gap-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm transition-colors hover:border-blue-100"
                  key={item.step}
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
                    <p className="mt-1 text-xs leading-relaxed text-slate-500">
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
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-bold text-white shadow-sm shadow-blue-500/20 transition hover:bg-blue-700"
            onClick={onClose}
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
