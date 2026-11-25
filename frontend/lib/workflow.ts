import type { WorkflowStep } from "@/types/dashboard";

// Konfigurasi langkah UI (3 Tahapan Utama)
export const workflowSteps: WorkflowStep[] = [
  { title: "Upload Data", description: "Upload file master & nilai" },
  { title: "Proses & Validasi", description: "Pilih Prodi atau Kode Kelas PAI" },
  { title: "Review Hasil", description: "Lihat ringkasan dan detail" },
];
