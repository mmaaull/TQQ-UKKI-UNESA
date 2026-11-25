"""Periksa pilihan sheet rekap final dan urutan peserta di dalamnya."""

from io import BytesIO
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.services.excel_service import export_excel, export_excel_per_prodi
from backend.app.services.processing import process_rekap


class ExportGroupingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.results = {"rekap": pd.DataFrame([
            {"nim": "240003", "nama": "C", "kode_kelas_pai": "1A", "prodi": "Biologi"},
            {"nim": "240002", "nama": "B", "kode_kelas_pai": "2B", "prodi": "Biologi"},
            {"nim": "240001", "nama": "A", "kode_kelas_pai": "1A", "prodi": "Fisika"},
            {"nim": "240004", "nama": "D", "kode_kelas_pai": "2B", "prodi": "Fisika"},
        ])}

    def test_per_prodi_joins_classes_and_sorts_nim(self) -> None:
        with pd.ExcelFile(BytesIO(export_excel_per_prodi(self.results))) as book:
            self.assertEqual(book.sheet_names, ["Biologi", "Fisika"])
            biologi = pd.read_excel(book, sheet_name="Biologi", dtype=str)
            self.assertEqual(biologi["NIM"].tolist(), ["240002", "240003"])
            self.assertEqual(biologi["Kode Kelas PAI"].tolist(), ["2B", "1A"])

    def test_per_kelas_sorts_nim(self) -> None:
        with pd.ExcelFile(BytesIO(export_excel(self.results))) as book:
            self.assertEqual(book.sheet_names, ["1A", "2B"])
            kelas = pd.read_excel(book, sheet_name="1A", dtype=str)
            self.assertEqual(kelas["NIM"].tolist(), ["240001", "240003"])

    def test_per_prodi_merges_typo_but_keeps_degree_separate(self) -> None:
        results = {"rekap": pd.DataFrame([
            {"nim": "240004", "nama": "D", "kode_kelas_pai": "1A", "prodi": "D4 Analisis Peforma Olahraga"},
            {"nim": "240001", "nama": "A", "kode_kelas_pai": "2B", "prodi": "D4 Analisis Performa Olahraga"},
            {"nim": "240003", "nama": "C", "kode_kelas_pai": "1A", "prodi": "S1 ILMU KOMUNIKASI"},
            {"nim": "240002", "nama": "B", "kode_kelas_pai": "2B", "prodi": "S1 Ilmu Komunikasi1"},
            {"nim": "240005", "nama": "E", "kode_kelas_pai": "2B", "prodi": "D4 Ilmu Komunikasi"},
        ])}
        with pd.ExcelFile(BytesIO(export_excel_per_prodi(results))) as book:
            self.assertEqual(book.sheet_names, [
                "D4 Analisis Performa Olahraga", "D4 Ilmu Komunikasi", "S1 Ilmu Komunikasi",
            ])
            olahraga = pd.read_excel(book, sheet_name="D4 Analisis Performa Olahraga", dtype=str)
            komunikasi = pd.read_excel(book, sheet_name="S1 Ilmu Komunikasi", dtype=str)
            self.assertEqual(olahraga["NIM"].tolist(), ["240001", "240004"])
            self.assertEqual(olahraga["Prodi"].unique().tolist(), ["D4 Analisis Performa Olahraga"])
            self.assertEqual(komunikasi["NIM"].tolist(), ["240002", "240003"])

    def test_process_rekap_uses_canonical_prodi_for_validation(self) -> None:
        peserta = pd.DataFrame([{
            "nim": "240001", "nama": "A", "jenis_kelamin": "P",
            "kode_kelas_pai": "1A", "prodi": "S1 Ilmu Komunikasi1",
        }, {
            "nim": "240002", "nama": "B", "jenis_kelamin": "L",
            "kode_kelas_pai": "1A", "prodi": "S1 ILMU KOMUNIKASI",
        }])
        nilai = pd.DataFrame([{
            "nim": "240001", "nama_nilai": "A", "kode_kelas_pai_nilai": "1A",
            "prodi_nilai": "S1 ILMU KOMUNIKASI", "presensi": "90", "bacaan": "90",
            "hafalan": "90", "evaluasi": "90", "total_nilai": "90", "abjad": "A",
        }])
        rekap = process_rekap(peserta, nilai)["rekap"]
        self.assertEqual(rekap["prodi"].unique().tolist(), ["S1 Ilmu Komunikasi"])
        self.assertFalse(rekap["prodi_berbeda"].any())


if __name__ == "__main__":
    unittest.main()
