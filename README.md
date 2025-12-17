# Smart Market Platform — README

Versi ini mendokumentasikan pengaturan pengembangan, arsitektur ringkas, cara menjalankan aplikasi (backend & device client), dan solusi untuk masalah yang mungkin muncul selama setup. README ini ditulis untuk pengembang yang bekerja pada repository *Project Pasar Rakyat*.

Isi:
- Ikhtisar singkat
- Prasyarat
- Struktur projek (ringkas)
- Setup lingkungan pengembangan
- Mengkonfigurasi environment variables (.env)
- Menjalankan backend (FastAPI)
- Menjalankan device client
- Endpoint penting (termasuk /ingest)
- Database & migrasi (SQLModel / Async DB)
- Docker / container hints
- Troubleshooting ringkas (kasus yang sering muncul)
- Tips debugging & maintanance
- Daftar dependensi (lihat requirements.txt)

--------------------------------------------------------------------------------
Ikhtisar singkat
--------------------------------------------------------------------------------
Smart Market Platform adalah aplikasi berbasis FastAPI yang menyediakan:
- API publik & auth
- Endpoint ingest untuk device (POST /ingest)
- Modul realtime/dashboard opsional
- Penyimpanan minimal menggunakan SQLModel (async)
- Device client untuk mensimulasikan perangkat yang mengirim data

Dokumentasi ini fokus pada pengaturan dev environment dan langkah praktis menjalankan sistem end-to-end.

--------------------------------------------------------------------------------
Prasyarat
--------------------------------------------------------------------------------
- Sistem operasi: Linux / macOS (panduan diasumsikan Linux)
- Python 3.10+ (disarankan 3.11; Anda tampaknya pakai 3.13 — sesuaikan dependensi/kompatibilitas)
- pip
- Virtual environment (venv atau virtualenv)
- sqlite (opsional untuk inspect DB), sqlite3 CLI
- curl, jq (opsional, untuk testing)

--------------------------------------------------------------------------------
Struktur projek (ringkas)
--------------------------------------------------------------------------------
- smart_market_platform/     # Backend FastAPI (app utama)
  - main.py                  # Entrypoint FastAPI (lifespan + routers)
  - config.py                # Pengaturan global & default port
  - ingest/                  # Router /ingest (menerima payload device)
  - auth/, api/, alerts/, ...# Router & modul lain
  - db.py                    # Engine async & session factory (SQLModel)
- device_client/             # Client CLI untuk mensimulasikan perangkat
  - main.py                  # CLI entrypoint (interactive + args)
  - client.py                # Logic pengiriman payload & queue lokal
  - config.py                # DEFAULT PLATFORM_HTTP_BASE => http://localhost:6969
- example_server/            # (opsional) contoh server kecil bila diperlukan
- .env.example               # Contoh environment
- requirements.txt           # Dependensi Python (pada file terpisah)

--------------------------------------------------------------------------------
Setup lingkungan pengembangan (cepat)
--------------------------------------------------------------------------------
1. Clone repo & masuk folder:
   cd ~/Downloads/Project\ Pasar\ Rakyat

2. Buat virtualenv dan aktifkan:
   python -m venv .venv
   source .venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Copy .env.example ke .env dan sesuaikan:
   cp .env.example .env
   Edit .env jika perlu (mis. PORT, DATABASE_URL, JWT_SECRET).

--------------------------------------------------------------------------------
Konfigurasi .env (poin penting)
--------------------------------------------------------------------------------
- PORT (default): 6969 (kami gunakan 6969 sebagai default)
- PLATFORM_HTTP_BASE (device_client default): http://localhost:6969
- DATABASE_URL: sqlite+aiosqlite:///./sm_platform.db (dev) atau postgresql+asyncpg://user:pass@host/db (prod)
- JWT_SECRET: ganti di production

Pastikan .env berada di root project (atau sesuaikan loader path).

--------------------------------------------------------------------------------
Menjalankan backend (FastAPI)
--------------------------------------------------------------------------------
Dua cara direkomendasikan (development):

A. Menggunakan uvicorn CLI (direkomendasikan):
   uvicorn smart_market_platform.main:app --reload --host 0.0.0.0 --port 6969

B. Menjalankan via module runner (juga mendukung reload safely):
   python -m smart_market_platform.main

Setelah start, buka:
- Swagger UI: http://localhost:6969/docs
- OpenAPI JSON: http://localhost:6969/openapi.json

Verifikasi route /ingest:
  curl -s http://localhost:6969/openapi.json | python -c "import sys,json;print(list(json.load(sys.stdin)['paths'].keys()))"

--------------------------------------------------------------------------------
Menjalankan device client
--------------------------------------------------------------------------------
1. Dari root project (penting: jalankan dari parent agar modul `device_client` dapat diimport)
   python -m device_client.main --mode http --device-id DEV-001 --market-id PASAR-001 --mock true --interval 2.0

2. Alternatif interaktif:
   python -m device_client.main --interactive
   Menu memungkinkan set server, port, register, run client.

3. Memaksa server custom:
   python -m device_client.main --server http://localhost:6969 --mode http ...

Catatan: client menyimpan payload gagal ke file queue DB (default: ~/.smart_market_client/queue.db) untuk retry.

--------------------------------------------------------------------------------
Endpoint penting (ringkas)
--------------------------------------------------------------------------------
- POST /ingest
  Body JSON minimal:
  {
    "timestamp": "2025-12-13T00:00:00Z",
    "market_id": "PASAR-001",
    "prices": {"cabai": 15000, "bawang": 9000},
    "region": "JAKARTA"          # optional
  }

- /api/auth/...   (device registration, auth)
- /api/public/... (public API)
Pastikan periksa openapi.json untuk daftar lengkap.

--------------------------------------------------------------------------------
Database & migrasi
--------------------------------------------------------------------------------
- Development default: SQLite Async via SQLModel (DATABASE_URL default: sqlite+aiosqlite:///./sm_platform.db)
- Inisialisasi otomatis:
  - Saat app startup, `init_db()` dijalankan (jika dipanggil), atau jalankan manual:
    python -c "from smart_market_platform.db import init_db; import asyncio; asyncio.run(init_db())"

- Jika schema berubah di dev, paling cepat hapus file DB:
  rm -f ./sm_platform.db

- Production: gunakan PostgreSQL/Timescale + alembic untuk migrasi.
  Disarankan menambahkan Alembic ke project. Contoh langkah:
  pip install alembic
  alembic init alembic
  konfigurasi env.py untuk menggunakan SQLModel metadata
  alembic revision --autogenerate -m "initial"
  alembic upgrade head

--------------------------------------------------------------------------------
Docker / Docker Compose (catatan singkat)
--------------------------------------------------------------------------------
Jika menggunakan Docker, expose port 6969 dan set env variables:
- Dockerfile: EXPOSE 6969
- docker-compose.yml: map port host:container jadi 6969:6969

Contoh service sederhana (snippet):
services:
  web:
    build: .
    ports:
      - "6969:6969"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./sm_platform.db
      - PORT=6969

--------------------------------------------------------------------------------
Troubleshooting (kasus nyata yang pernah muncul)
--------------------------------------------------------------------------------
1) Address already in use (port 8000 / 6969):
   - Cek proses yang mendengarkan:
     sudo lsof -nP -iTCP:6969 -sTCP:LISTEN
     ss -ltnp | grep :6969
   - Hentikan proses (jika aman):
     sudo kill <PID>
   - Atau jalankan server di port lain:
     uvicorn smart_market_platform.main:app --reload --port 8001

2) Response 404 untuk /ingest:
   - Pastikan Anda menjalankan aplikasi yang benar (smart_market_platform.main) yang sudah include router /ingest.
   - Cek openapi.json untuk memastikan "/ingest" ada.
   - Jika /ingest tidak ada, pastikan file `smart_market_platform/ingest/routes.py` ada dan importable.

3) ModuleNotFoundError: No module named 'device_client'
   - Jalankan client dari root project atau gunakan python -m device_client.main
   - Atau set PYTHONPATH=".." dan jalankan main.py dari dalam folder device_client

4) ModuleNotFoundError: No module named 'sqlmodel'
   - Install dependency:
     pip install sqlmodel aiosqlite

5) RuntimeError "Passing index is not supported when also passing a sa_column"
   - Solusi: jangan pakai `Field(index=True, sa_column=Column(...))`. Buat Index di __table_args__ menggunakan sqlalchemy.Index atau gunakan Column(unique=True).

6) InvalidRequestError: Attribute name 'metadata' is reserved
   - Jangan gunakan nama field `metadata` pada model SQLAlchemy/SQLModel. Ganti ke `metadata_json` atau `extra` dan sesuaikan referensi kode.

7) Uvicorn reload warning:
   - Jika menjalankan uvicorn.run(...) dari dalam modul dengan reload=True, akan muncul peringatan. Gunakan:
     uvicorn smart_market_platform.main:app --reload ...
     atau pastikan uvicorn.run menerima import string saat dipanggil via python -m (sudah diperbaiki pada main.py).

8) Payload queued di device_client:
   - Periksa file queue: ~/.smart_market_client/queue.db
   - Inspect:
     sqlite3 ~/.smart_market_client/queue.db "SELECT id, created_at, payload FROM queue ORDER BY id DESC LIMIT 5;"
   - Hapus entri jika perlu:
     sqlite3 ~/.smart_market_client/queue.db "DELETE FROM queue; VACUUM;"

--------------------------------------------------------------------------------
Debugging tips
--------------------------------------------------------------------------------
- Aktifkan log DEBUG:
  LOG_LEVEL=DEBUG python -m device_client.main ...
- Cek server logs (uvicorn) di terminal untuk stacktraces.
- Gunakan curl -v untuk melihat response detail:
  curl -v -H "Content-Type: application/json" http://localhost:6969/ingest -d '{"market_id":"PASAR-001","prices":{"cabai":15000}}'

--------------------------------------------------------------------------------
Maintenance & rekomendasi produksi
--------------------------------------------------------------------------------
- Gunakan PostgreSQL/TimescaleDB untuk time-series & analytic workloads.
- Gunakan Redis/Kafka untuk pub/sub & WebSocket broadcast scaling.
- Tambahkan Alembic untuk migrasi skema.
- Simpan secrets (JWT_SECRET, DB credentials) di Secret Manager / environment, jangan di repo.
- Gunakan supervisord/systemd atau container orchestration untuk manajemen proses.

--------------------------------------------------------------------------------
Daftar dependensi & cara install
--------------------------------------------------------------------------------
Instal semua paket:
  pip install -r requirements.txt

(Lihat file `requirements.txt` di root repo untuk daftar lengkap dan komentar paket opsional.)

--------------------------------------------------------------------------------
Kontak / kontribusi
--------------------------------------------------------------------------------
- Jika Anda menemukan bug atau ingin menambah fitur, buat issue di tracker repo atau kirim PR.
- Sertakan langkah reproduksi dan log error yang relevan.

Terima kasih — jika Anda mau, saya bisa:
- Membuat patch git (diff) yang mengubah semua hard-coded port 8000 -> 6969
- Menambahkan Alembic skeleton & contoh migration
- Membuat docker-compose.yml contoh (Postgres + Redis + app)
