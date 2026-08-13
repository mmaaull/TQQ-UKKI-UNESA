export type KpiItem = {
  label: string;
  value: string;
  note: string;
  tone: "blue" | "green" | "amber" | "red";
};

export type WorkflowStep = {
  title: string;
  description: string;
};

export type ChartDatum = {
  name: string;
  value: number;
  color: string;
  percentage?: string;
};

export type ClassProgressDatum = {
  kelas: string;
  jumlah: number;
};

export type RekapRow = {
  nim: string;
  nama: string;
  prodi: string;
  kelas: string;
  dosen: string;
  presensi: number;
  bacaan: number;
  hafalan: number;
  evaluasi: number;
  total: string;
  abjad: string;
  status: "Sudah Ada Nilai" | "Belum Ada Nilai";
  validasi: "Valid" | "Perlu Dicek";
};

export type ProcessStatus = "idle" | "uploading" | "processing" | "success" | "error";

export type Summary = {
  total_peserta: number;
  sudah_ada_nilai: number;
  belum_ada_nilai: number;
  perlu_dicek: number;
  persentase_selesai: number;
};

export type ApiRecord = Record<string, string | number | boolean | null>;

export type RekapProcessResponse = {
  session_id: string;
  summary: Summary;
  rekap: ApiRecord[];
  ringkasan_kelas: ApiRecord[];
  ringkasan_masalah: ApiRecord[];
  data_bermasalah: ApiRecord[];
};
