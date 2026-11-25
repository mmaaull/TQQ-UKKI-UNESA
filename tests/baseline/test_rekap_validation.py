"""Kasus identitas dan nilai yang harus dibedakan dalam Data Bermasalah."""

from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.services.processing import process_rekap


def master(nim: str, nama: str = "Anisa Putri", prodi: str = "S1 Biologi", kelas: str = "1A") -> dict[str, str]:
    return {"nim": nim, "nama": nama, "jenis_kelamin": "P", "prodi": prodi, "kode_kelas_pai": kelas}


def nilai(nim: str, nama: str = "Anisa Putri", total: str = "90", abjad: str = "A", prodi: str = "S1 Biologi", kelas: str = "1A") -> dict[str, str]:
    return {
        "nim": nim, "nama_nilai": nama, "prodi_nilai": prodi, "kode_kelas_pai_nilai": kelas,
        "presensi": "90", "bacaan": "90", "hafalan": "90", "evaluasi": "90",
        "total_nilai": total, "abjad": abjad,
    }


def run_rekap(masters: list[dict[str, str]], scores: list[dict[str, str]]) -> dict[str, pd.DataFrame]:
    return process_rekap(pd.DataFrame(masters), pd.DataFrame(scores))


class RekapValidationTest(unittest.TestCase):
    def test_duplicate_score_uses_complete_matching_row(self) -> None:
        empty_last = nilai("100") | {column: "" for column in ("presensi", "bacaan", "hafalan", "evaluasi", "total_nilai", "abjad")}
        result = run_rekap([master("100")], [nilai("100"), empty_last])
        self.assertEqual(result["rekap"].iloc[0]["total_nilai"], "90")
        kinds = result["data_bermasalah"]["Jenis Masalah"].tolist()
        self.assertIn("NIM duplikat di file nilai", kinds)
        self.assertNotIn("Nilai belum diisi", kinds)
        self.assertNotIn("Total Nilai kosong", kinds)

    def test_duplicate_score_prefers_master_name_over_other_person(self) -> None:
        wrong_person = nilai("100", nama="Budi Santoso", total="98")
        matching_person = nilai("100", nama="Anisa Putri", total="80")
        result = run_rekap([master("100")], [wrong_person, matching_person])
        self.assertEqual(result["rekap"].iloc[0]["total_nilai"], "80")
        self.assertNotIn("Nama berbeda antara file peserta dan file nilai", set(result["data_bermasalah"]["Jenis Masalah"]))

    def test_wrong_nim_with_same_name_is_not_called_empty_score(self) -> None:
        result = run_rekap([master("100")], [nilai("999")])
        kinds = result["data_bermasalah"]["Jenis Masalah"].tolist()
        self.assertEqual(kinds, ["NIM berbeda antara file master dan file nilai"])
        self.assertEqual(result["data_bermasalah"].iloc[0]["Nilai Terdeteksi"], "999")
        self.assertEqual(result["rekap"].iloc[0]["status_validasi"], "Perlu Dicek")

    def test_master_identity_is_authoritative_and_all_differences_are_reported(self) -> None:
        result = run_rekap([master("100")], [nilai("100", nama="Annisa Putri", prodi="S1 Kimia", kelas="2B")])
        row = result["rekap"].iloc[0]
        self.assertEqual((row["nama"], row["prodi"], row["kode_kelas_pai"]), ("Anisa Putri", "S1 Biologi", "1A"))
        kinds = set(result["data_bermasalah"]["Jenis Masalah"])
        self.assertEqual(kinds, {
            "Nama berbeda antara file peserta dan file nilai",
            "Kode Kelas PAI berbeda antara file peserta dan file nilai",
            "Program Studi berbeda antara file peserta dan file nilai",
        })
        self.assertEqual(result["data_bermasalah"]["Prodi Master"].unique().tolist(), ["S1 Biologi"])

    def test_partial_scores_report_only_the_missing_column(self) -> None:
        result = run_rekap([master("100")], [nilai("100", total="")])
        self.assertEqual(result["rekap"].iloc[0]["status_nilai"], "Sudah Ada Nilai")
        self.assertEqual(result["data_bermasalah"]["Jenis Masalah"].tolist(), ["Total Nilai kosong"])
        self.assertEqual(result["data_bermasalah"].iloc[0]["Kolom"], "TOTAL NILAI")

    def test_unmatched_people_and_empty_identifiers_are_reported(self) -> None:
        result = run_rekap([master("100"), master("", nama="Budi")], [nilai("999", nama="Cici"), nilai("", nama="Dedi")])
        kinds = set(result["data_bermasalah"]["Jenis Masalah"])
        self.assertEqual(kinds, {
            "NIM kosong di file master", "NIM kosong di file nilai",
            "NIM di file nilai tidak ada di file peserta", "Peserta belum ada di file nilai",
        })

    def test_missing_master_and_score_identity_fields_are_reported(self) -> None:
        result = run_rekap([master("100", prodi="", kelas="")], [nilai("100", nama="", prodi="", kelas="")])
        problems = result["data_bermasalah"]
        self.assertEqual(set(problems["Jenis Masalah"]), {
            "Data identitas kosong di file master", "Data identitas kosong di file nilai",
        })
        self.assertEqual(set(problems["Kolom"]), {"Nama", "Program Studi", "Kode Kelas PAI"})

    def test_blank_master_identity_is_not_called_mismatch(self) -> None:
        result = run_rekap([master("100", nama="", prodi="", kelas="")], [nilai("100")])
        self.assertEqual(set(result["data_bermasalah"]["Jenis Masalah"]), {"Data identitas kosong di file master"})


if __name__ == "__main__":
    unittest.main()
