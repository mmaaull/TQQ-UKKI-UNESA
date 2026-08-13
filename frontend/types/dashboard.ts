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
