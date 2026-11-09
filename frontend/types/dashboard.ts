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
  total?: number;
  sudahAdaNilai?: number;
  persentase?: number;
};

export type RekapRow = {
  nim: string;
  nama: string;
  prodi: string;
  kelas: string;
  jenisKelamin: string;
  presensi: string;
  bacaan: string;
  hafalan: string;
  evaluasi: string;
  total: string;
  abjad: string;
  catatanValidasi?: string;
  status: "Sudah Ada Nilai" | "Belum Ada Nilai";
  validasi: "Valid" | "Perlu Dicek";
};

export type ProcessStatus = "idle" | "ready" | "processing" | "success" | "error";

export type ExportStatus = "idle" | "downloading" | "success" | "error";
export type ExportKind = "final" | "validasi" | "data-bermasalah" | "per-kelas" | "template";

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

export type RapikanProcessResponse = {
  session_id: string;
  summary: { total_data: number; total_sheet: number };
  preview: ApiRecord[];
  sheet_preview: ApiRecord[];
};

export type RekapJilidProcessResponse = {
  session_id: string;
  summary: {
    total_dinilai: number;
    total_duplikat_disaring?: number;
    total_otomatis_jilid1: number;
    total_terklasifikasi: number;
    total_bermasalah: number;
  };
  ringkasan_jilid: ApiRecord[];
  ringkasan_masalah: ApiRecord[];
  data_bermasalah: ApiRecord[];
  data_otomatis_jilid1: ApiRecord[];
};

export type KehadiranProcessResponse = {
  session_id: string;
  summary: {
    total_mahasiswa: number;
    total_hadir: number;
    total_tidak_hadir: number;
    total_tidak_ada_di_rekap: number;
    total_kelas: number;
    persentase_hadir: number;
  };
  ringkasan_kelas: ApiRecord[];
  tidak_ada_di_rekap: ApiRecord[];
};

export type TentorProcessResponse = {
  session_id: string;
  summary: {
    total_peserta: number;
    total_tentor: number;
    total_tentor_laki_laki: number;
    total_tentor_perempuan: number;
  };
  ringkasan_tentor: ApiRecord[];
};

export type CariMahasiswaRow = {
  sumber: string;
  sheet: string;
  nim: string;
  nama: string;
  /** Kolom lain di tabel sumber (nama kolom mengikuti file asli). */
  data: Record<string, string>;
  /** Info di atas tabel sheet, mis. Tentor dan Link Grup WA. */
  info: Record<string, string>;
};

export type CariMahasiswaIndexResponse = {
  summary: { total_mahasiswa: number; total_sheet: number; total_file: number };
  data_columns: string[];
  info_columns: string[];
  mahasiswa: CariMahasiswaRow[];
};
