"""Periksa pilihan sheet rekap final dan urutan peserta di dalamnya."""

from io import BytesIO
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.services.excel_service import export_excel, export_excel_per_prodi


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


if __name__ == "__main__":
    unittest.main()
