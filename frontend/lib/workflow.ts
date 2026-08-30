import type { WorkflowStep } from "@/types/dashboard";

// Konfigurasi langkah UI (3 Tahapan Utama)
export const workflowSteps: WorkflowStep[] = [
  { title: "Upload Data", description: "Upload file peserta & nilai" },
  { title: "Proses & Validasi", description: "Pencocokan dan validasi data" },
  { title: "Review Hasil", description: "Lihat ringkasan dan detail" },
];
