import type { WorkflowStep } from "@/types/dashboard";

// Konfigurasi langkah UI, bukan data dashboard hasil rekap.
export const workflowSteps: WorkflowStep[] = [
  { title: "Upload Data", description: "Upload file peserta & nilai" },
  { title: "Proses & Validasi", description: "Pencocokan dan validasi data" },
  { title: "Review Hasil", description: "Lihat ringkasan dan detail" },
  { title: "Export", description: "Unduh hasil rekap" },
];
