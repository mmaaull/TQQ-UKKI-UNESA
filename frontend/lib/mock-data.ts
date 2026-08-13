import type { ChartDatum, ClassProgressDatum, KpiItem, RekapRow, WorkflowStep } from "@/types/dashboard";

export const workflowSteps: WorkflowStep[] = [
  { title: "Upload Data", description: "Upload file peserta & nilai" },
  { title: "Proses & Validasi", description: "Pencocokan dan validasi data" },
  { title: "Review Hasil", description: "Lihat ringkasan dan detail" },
  { title: "Export", description: "Unduh hasil rekap" },
];

export const kpiItems: KpiItem[] = [
  { label: "Total Peserta", value: "1.284", note: "100% dari total data", tone: "blue" },
  { label: "Sudah Ada Nilai", value: "1.172", note: "91,3% dari total peserta", tone: "green" },
  { label: "Belum Ada Nilai", value: "112", note: "8,7% dari total peserta", tone: "amber" },
  { label: "Perlu Dicek", value: "23", note: "1,8% dari total peserta", tone: "red" },
];

export const scoreProgress: ChartDatum[] = [
  { name: "Sudah Ada Nilai", value: 1172, color: "#2563eb", percentage: "91,3" },
  { name: "Belum Ada Nilai", value: 112, color: "#f59e0b", percentage: "8,7" },
];

export const incompleteClasses: ClassProgressDatum[] = [
  { kelas: "2026A-013", jumlah: 17 },
  { kelas: "2026A-021", jumlah: 12 },
  { kelas: "2026A-007", jumlah: 9 },
  { kelas: "2026A-019", jumlah: 7 },
  { kelas: "2026A-002", jumlah: 6 },
];

export const validationItems: ChartDatum[] = [
  { name: "NIM tidak ditemukan", value: 4, color: "#ef4444" },
  { name: "Nama berbeda", value: 7, color: "#f97316" },
  { name: "Nilai kosong", value: 5, color: "#eab308" },
  { name: "NIM duplikat", value: 2, color: "#8b5cf6" },
  { name: "Nilai tidak valid", value: 5, color: "#3b82f6" },
];

export const rekapRows: RekapRow[] = [
  {
    nim: "23010123001", nama: "Ahmad Fadly", prodi: "Pendidikan Agama Islam", kelas: "2026A-013",
    dosen: "Dr. H. Muhammad, M.Ag.", presensi: 95, bacaan: 90, hafalan: 88,
    evaluasi: 92, total: "91,25", abjad: "A", status: "Sudah Ada Nilai", validasi: "Valid",
  },
  {
    nim: "23010123002", nama: "Aisyah Rahma", prodi: "Pendidikan Bahasa Inggris", kelas: "2026A-021",
    dosen: "Dr. Hj. Nur Aini, M.Pd.", presensi: 92, bacaan: 86, hafalan: 85,
    evaluasi: 90, total: "88,25", abjad: "A", status: "Sudah Ada Nilai", validasi: "Valid",
  },
  {
    nim: "23010123003", nama: "Bagas Pratama", prodi: "Teknik Informatika", kelas: "2026A-007",
    dosen: "Ust. Ahmad Syarif, M.A.", presensi: 0, bacaan: 0, hafalan: 0,
    evaluasi: 0, total: "-", abjad: "-", status: "Belum Ada Nilai", validasi: "Perlu Dicek",
  },
  {
    nim: "23010123004", nama: "Citra Lestari", prodi: "Manajemen", kelas: "2026A-019",
    dosen: "Dr. H. Muhammad, M.Ag.", presensi: 98, bacaan: 94, hafalan: 90,
    evaluasi: 93, total: "93,75", abjad: "A", status: "Sudah Ada Nilai", validasi: "Valid",
  },
  {
    nim: "23010123005", nama: "Dimas Saputra", prodi: "Ilmu Komunikasi", kelas: "2026A-002",
    dosen: "Dr. Hj. Nur Aini, M.Pd.", presensi: 88, bacaan: 0, hafalan: 0,
    evaluasi: 0, total: "-", abjad: "-", status: "Belum Ada Nilai", validasi: "Perlu Dicek",
  },
];
