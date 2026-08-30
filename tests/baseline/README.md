# Baseline Test

Baseline ini merekam hasil aplikasi Streamlit lama sebagai pembanding ketika
frontend dipindahkan ke Next.js dan backend dipindahkan ke FastAPI. Script
memanggil fungsi business logic yang ada di `app.py`; UI Streamlit dan browser
tidak dijalankan.

Generate baseline:

```bash
python tests/baseline/generate_baseline.py
```

Verify baseline:

```bash
python tests/baseline/verify_baseline.py
```

Fixture input Excel berada di `tests/fixtures/input/`. Bila belum ada, script
generate akan membuat fixture terisolasi tersebut. Hasil pembanding tersimpan
di `tests/fixtures/expected/`.
