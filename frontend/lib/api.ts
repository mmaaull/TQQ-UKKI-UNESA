import type {
  ApiRecord,
  ChartDatum,
  ClassProgressDatum,
  KpiItem,
  RekapProcessResponse,
  RekapRow,
  Summary,
} from "@/types/dashboard";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

function valueOf(record: ApiRecord, keys: string[]): string | number | boolean | null {
  for (const key of keys) {
    if (key in record) return record[key];
  }
  return null;
}

function textOf(record: ApiRecord, keys: string[]): string {
  const value = valueOf(record, keys);
  return value === null || value === undefined ? "-" : String(value);
}

function numberOf(record: ApiRecord, keys: string[]): number {
  const value = valueOf(record, keys);
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) ? number : 0;
}

function formatNumber(value: number): string {
  return value.toLocaleString("id-ID");
}

function formatPercentage(value: number): string {
  return `${value.toLocaleString("id-ID", { maximumFractionDigits: 1 })}%`;
}

export async function processRekap(pesertaFile: File, nilaiFile: File): Promise<RekapProcessResponse> {
  const formData = new FormData();
  formData.append("peserta_file", pesertaFile);
  formData.append("nilai_file", nilaiFile);

  const response = await fetch(`${apiUrl}/api/rekap/process`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let message = "Proses rekap gagal. Silakan coba kembali.";
    try {
      const body: unknown = await response.json();
      if (typeof body === "object" && body !== null && "detail" in body) {
        const detail = body.detail;
        message = typeof detail === "string" ? detail : JSON.stringify(detail);
      }
    } catch {
      // Gunakan pesan default jika response error bukan JSON.
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<RekapProcessResponse>;
}

export function makeKpiItems(summary: Summary): KpiItem[] {
  return [
    { label: "Total Peserta", value: formatNumber(summary.total_peserta), note: "100% dari total data", tone: "blue" },
    { label: "Sudah Ada Nilai", value: formatNumber(summary.sudah_ada_nilai), note: `${formatPercentage(summary.persentase_selesai)} dari total peserta`, tone: "green" },
    { label: "Belum Ada Nilai", value: formatNumber(summary.belum_ada_nilai), note: `${formatPercentage(summary.total_peserta ? summary.belum_ada_nilai / summary.total_peserta * 100 : 0)} dari total peserta`, tone: "amber" },
    { label: "Perlu Dicek", value: formatNumber(summary.perlu_dicek), note: `${formatPercentage(summary.total_peserta ? summary.perlu_dicek / summary.total_peserta * 100 : 0)} dari total peserta`, tone: "red" },
  ];
}

export function makeScoreProgress(summary: Summary): ChartDatum[] {
  const total = summary.total_peserta;
  return [
    { name: "Sudah Ada Nilai", value: summary.sudah_ada_nilai, color: "#2563eb", percentage: formatPercentage(total ? summary.sudah_ada_nilai / total * 100 : 0).replace("%", "") },
    { name: "Belum Ada Nilai", value: summary.belum_ada_nilai, color: "#f59e0b", percentage: formatPercentage(total ? summary.belum_ada_nilai / total * 100 : 0).replace("%", "") },
  ];
}

export function mapRekapRows(records: ApiRecord[]): RekapRow[] {
  return records.map((record) => ({
    nim: textOf(record, ["nim", "NIM"]),
    nama: textOf(record, ["nama", "Nama"]),
    prodi: textOf(record, ["prodi", "Prodi"]),
    kelas: textOf(record, ["kode_kelas_pai", "Kode Kelas PAI", "kelas_umum", "Kelas"]),
    dosen: textOf(record, ["dosen_pengampu", "Dosen Pengampu"]),
    presensi: numberOf(record, ["presensi", "Presensi"]),
    bacaan: numberOf(record, ["bacaan", "Bacaan"]),
    hafalan: numberOf(record, ["hafalan", "Hafalan"]),
    evaluasi: numberOf(record, ["evaluasi", "Evaluasi"]),
    total: textOf(record, ["total_nilai", "Total Nilai"]),
    abjad: textOf(record, ["abjad", "Abjad"]),
    status: textOf(record, ["status_nilai", "Status Nilai"]) === "Sudah Ada Nilai" ? "Sudah Ada Nilai" : "Belum Ada Nilai",
    validasi: textOf(record, ["status_validasi", "Status Validasi"]) === "Valid" ? "Valid" : "Perlu Dicek",
  }));
}

export function mapClassProgress(records: ApiRecord[]): ClassProgressDatum[] {
  return records.map((record) => ({
    kelas: textOf(record, ["Kode Kelas PAI", "kode_kelas_pai", "Kelas"]),
    jumlah: numberOf(record, ["Belum Ada Nilai", "belum_ada_nilai", "Jumlah"]),
  }));
}

const problemColors = ["#ef4444", "#f97316", "#eab308", "#8b5cf6", "#3b82f6"];

export function mapValidationItems(records: ApiRecord[]): ChartDatum[] {
  return records.map((record, index) => ({
    name: textOf(record, ["Jenis Masalah", "jenis_masalah", "Nama"]),
    value: numberOf(record, ["Jumlah", "jumlah"]),
    color: problemColors[index % problemColors.length],
  }));
}
