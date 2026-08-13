# Arsip UI lama

`app_streamlit.py` adalah antarmuka Streamlit sebelum migrasi ke Next.js dan
FastAPI. Aplikasi utama tidak lagi menggunakannya.

Untuk menjalankan arsip ini secara terpisah, instal dependency arsip lalu dari
folder `legacy/` jalankan aplikasi dengan root repository pada `PYTHONPATH`.

```powershell
pip install -r requirements-streamlit.txt
$env:PYTHONPATH = ".."
streamlit run app_streamlit.py
```
