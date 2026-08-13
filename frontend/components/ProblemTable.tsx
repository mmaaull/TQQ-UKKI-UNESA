import type { ApiRecord } from "@/types/dashboard";

export type ProblemTableProps = { rows: ApiRecord[] };

export function ProblemTable({ rows }: ProblemTableProps) {
  const columns = rows[0] ? Object.keys(rows[0]) : [];
  return <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"><div><h2 className="text-base font-semibold text-slate-900">Data Bermasalah</h2><p className="mt-1 text-xs text-slate-500">Data yang memerlukan pengecekan lebih lanjut</p></div>{rows.length === 0 ? <p className="mt-5 rounded-xl bg-emerald-50 px-4 py-4 text-sm font-medium text-emerald-700">Tidak ada data bermasalah dari proses terakhir.</p> : <div className="mt-5 overflow-x-auto rounded-xl border border-slate-200"><table className="min-w-max w-full border-collapse text-left text-xs"><thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500"><tr>{columns.map((column) => <th className="whitespace-nowrap border-b border-slate-200 px-4 py-3.5" key={column}>{column}</th>)}</tr></thead><tbody className="divide-y divide-slate-100 text-slate-700">{rows.map((row, index) => <tr className="hover:bg-slate-50" key={`${String(row.NIM ?? row.nim ?? "masalah")}-${index}`}>{columns.map((column) => <td className="max-w-72 px-4 py-3 align-top" key={column}>{row[column] === null || row[column] === "" ? "-" : String(row[column])}</td>)}</tr>)}</tbody></table></div>}</section>;
}
