import type {
  ApiRecord,
  ChartDatum,
  ClassProgressDatum,
  ExportKind,
  KpiItem,
  RekapProcessResponse,
  RekapRow,
  RapikanProcessResponse,
  Summary,
} from "@/types/dashboard";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "";

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

function filenameFromDisposition(contentDisposition: string | null, fallback: string): string {
  const match = contentDisposition?.match(/filename="?([^";]+)"?/i);
  return match?.[1] ?? fallback;
}

async function triggerBrowserDownload(response: Response, fallbackFilename: string): Promise<string> {
  const filename = filenameFromDisposition(response.headers.get("content-disposition"), fallbackFilename);
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
  return filename;
}

export async function downloadExport(kind: ExportKind, sessionId?: string): Promise<string> {
  const requiresSession = kind !== "template";
  if (requiresSession && !sessionId) {
    throw new ApiError("Proses rekap harus berhasil sebelum file ini dapat diunduh.", 400);
  }

  const endpoint = kind === "template" ? "/api/export/template" : `/api/export/${sessionId}/${kind}`;
  const response = await fetch(`${apiUrl}${endpoint}`);
  if (!response.ok) {
    let message = "Unduhan export gagal. Silakan coba kembali.";
    try {
      const body: unknown = await response.json();
      if (typeof body === "object" && body !== null && "detail" in body) {
        message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // Gunakan pesan default ketika response error bukan JSON.
    }
    throw new ApiError(message, response.status);
  }

  return triggerBrowserDownload(response, `rekap-${kind}.xlsx`);
}

export async function processRapikan(rekapFile: File): Promise<RapikanProcessResponse> {
  const formData = new FormData();
  formData.append("rekap_file", rekapFile);
  const response = await fetch(`${apiUrl}/api/rapikan/process`, { method: "POST", body: formData });
  if (!response.ok) {
    let message = "Proses rapikan gagal. Silakan coba kembali.";
    try {
      const body: unknown = await response.json();
      if (typeof body === "object" && body !== null && "detail" in body) {
        message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // Gunakan pesan default jika response error bukan JSON.
    }
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<RapikanProcessResponse>;
}

export async function downloadRapikan(sessionId: string): Promise<string> {
  const response = await fetch(`${apiUrl}/api/rapikan/${sessionId}/download`);
  if (!response.ok) {
    throw new ApiError("Unduhan hasil rapikan gagal. Silakan proses ulang file.", response.status);
  }
  return triggerBrowserDownload(response, "rekap_tqq_per_kode_kelas_dan_prodi.xlsx");
}

export function makeKpiItems(summary: Summary): KpiItem[] {
  return [
    { label: "Total Peserta", value: formatNumber(summary.total_peserta), note: "100% dari total data", tone: "blue" },
    { label: "Sudah Ada Nilai", value: formatNumber(summary.sudah_ada_nilai), note: `${formatPercentage(summary.persentase_selesai)} dari total peserta`, tone: "green" },
    { label: "Belum Ada Nilai", value: formatNumber(summary.belum_ada_nilai), note: `${formatPercentage(summary.total_peserta ? summary.belum_ada_nilai / summary.total_peserta * 100 : 0)} dari total peserta`, tone: "amber" },
    { label: "Perlu Dicek", value: formatNumber(summary.perlu_dicek), note: `${formatPercentage(summary.total_peserta ? summary.perlu_dicek / summary.total_peserta * 100 : 0)} dari total peserta`, tone: "red" },
    { label: "Persentase Selesai", value: formatPercentage(summary.persentase_selesai), note: "Kelengkapan nilai peserta", tone: "blue" },
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
  return records.map((record) => {
    const total = numberOf(record, ["Total Peserta", "total_peserta"]);
    const sudah = numberOf(record, ["Sudah Ada Nilai", "sudah_ada_nilai"]);
    const belum = numberOf(record, ["Belum Ada Nilai", "belum_ada_nilai"]);
    const persentaseRaw = numberOf(record, ["Persentase Selesai (%)", "persentase_selesai"]);
    const persentase = persentaseRaw || (total > 0 ? (sudah / total) * 100 : 0);

    return {
      kelas: textOf(record, ["Kode Kelas PAI", "kode_kelas_pai", "Kelas"]),
      jumlah: belum,
      total: total,
      sudahAdaNilai: sudah,
      persentase: Math.round(persentase * 10) / 10,
    };
  });
}

const problemColors = ["#ef4444", "#f97316", "#eab308", "#8b5cf6", "#3b82f6"];

export function mapValidationItems(records: ApiRecord[]): ChartDatum[] {
  return records.map((record, index) => ({
    name: textOf(record, ["Jenis Masalah", "jenis_masalah", "Nama"]),
    value: numberOf(record, ["Jumlah", "jumlah"]),
    color: problemColors[index % problemColors.length],
  }));
}
