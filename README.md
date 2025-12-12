# Smart Market Platform — National Smart Market Intelligence
Versi: 0.1.0

---
Ringkasan singkat
-----------------
Smart Market Platform adalah platform intelijen pasar berskala nasional yang dirancang untuk mengumpulkan, memverifikasi, menganalisis, dan memvisualisasikan data harga komoditas dari pasar rakyat di Indonesia. Platform ini dibangun dengan Python 3.11+, FastAPI, WebSocket, dan arsitektur modular / clean architecture, sehingga mudah diperluas dan diintegrasikan dengan komponen produksi seperti TimescaleDB, broker MQTT TLS, sistem antrian, dan layanan AI.

Fitur utama
-----------
- Pengumpulan data IoT (sensor suhu, kelembapan, keramaian, harga komoditas) — diperluas dari Smart Market Data Stream.
- Validasi & Anti-Manipulasi: deteksi outlier (Z-score, IQR), AI anomaly stub, verifikasi multi-sumber, karantina otomatis.
- Otentikasi & Onboarding perangkat: JWT, registrasi device, QR-code onboarding, role-based access control.
- Supply Chain Intelligence: monitor stok, analisa rute & estimasi keterlambatan.
- Impact Engine: pembobotan faktor (cuaca, hama, distribusi, oversupply, musim, permintaan nasional) + integrasi makro-ekonomi.
- Forecast Engine: endpoint forecasting (naïve/ARIMA/Prophet/LSTM stubs), training utilities.
- Early Warning System: pemicu alert, mock Telegram/WhatsApp, risk scoring, push via WebSocket.
- Sentiment Analysis: pengumpulan sosial sederhana + korelasi dampak.
- Blockchain ledger (opsional): hash-chaining untuk integritas entri harga, endpoint verifikasi.
- Dashboard: Chart.js real-time, peta (Leaflet) heatmap, WebSocket streaming.
- Public API untuk developer: `/commodity/price/live`, `/commodity/price/history`, `/forecast`, `/impact`, `/alerts/live`, `/device/register`, `/market/list`.

Struktur proyek (ringkas)
-------------------------
smart_market_platform/
- api/
  - public/          ← router API yang bisa diakses developer
  - admin/           ← (placeholder untuk admin API)
- auth/              ← device/user models, JWT utils, registrasi & QR onboarding
- iot/               ← (tempat integrasi Smart Market Data Stream)
- validation_engine/ ← deteksi outlier, AI anomaly stub, multi-source verify
- supply_chain/      ← stock monitoring, route analyzer
- forecast_engine/   ← forecasting routes & trainer
- alerts/            ← EWS manager & websocket push
- sentiment/         ← social sentiment collector & simple NLP
- macro_data/        ← macro coefficients (inflation, fuel, etc.)
- impact_engine/     ← fusion impact engine (menggabungkan faktor & makro)
- blockchain/        ← simple ledger & integrity check
- dashboard/
  - map/             ← peta (Leaflet) & heatmap static assets
  - charts/          ← chart manager mock
- main.py            ← FastAPI entrypoint
- config.py          ← pengambilan env / settings
- db.py              ← inisialisasi DB (SQLModel/Async)
- requirements.txt
- .env.example
- Dockerfile
- sample_data_generator.py

Instalasi & Quick Start (pengembangan)
--------------------------------------
1. Clone repo:
   ```bash
   git clone <repo-url>
   cd smart_market_platform
   ```

2. Buat virtual environment dan instal dependensi:
   ```bash
   python -m venv .venv
   source .venv/bin/activate          # Linux / macOS
   .venv\Scripts\activate             # Windows PowerShell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Salin contoh file konfigurasi:
   ```bash
   cp .env.example .env
   # Edit .env sesuai kebutuhan (DATABASE_URL, JWT_SECRET, dsb.)
   ```

4. Inisialisasi database (pada startup, sistem akan menjalankan `init_db()` otomatis).
   Secara lokal default menggunakan SQLite (untuk pengembangan). Untuk produksi gunakan PostgreSQL/TimescaleDB:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@db:5432/smart_market
   ```

5. Jalankan aplikasi:
   ```bash
   uvicorn smart_market_platform.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Akses dokumentasi interaktif:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Dashboard (peta): http://localhost:8000/dashboard/map/
   - Dashboard chart (static Chart.js): http://localhost:8000/market_realtime_dashboard/static/index.html (jika modul dipasang)

Konfigurasi environment
-----------------------
Lihat `.env.example`. Parameter penting:
- DATABASE_URL — koneksi async ke DB (sqlite/asyncpg)
- JWT_SECRET, JWT_ALGORITHM — untuk menandatangani token perangkat
- MQTT_TLS_CERT / MQTT_TLS_KEY — path sertifikat ketika TLS MQTT digunakan
- ALERT_THRESHOLD — ambang untuk EWS
- TELEGRAM_TOKEN / WHATSAPP_TOKEN — token integrasi (mock jika kosong)

API publik (ringkasan)
---------------------
Semua endpoint public berada di prefix `/api/public`. Contoh penting:

1. Commodity & price
- GET /api/public/commodity/price/live?commodity={commodity}&region={region}
  - Latest price per pasar untuk komoditas
- GET /api/public/commodity/price/history?commodity={}&market_id={}&limit={}

2. Forecast
- GET /api/public/forecast?commodity={commodity}
  - Kembalikan forecast 7 hari dan confidence

3. Impact
- GET /api/public/impact?commodity={}&market_id={}&prev_price={}&new_price={}
  - Menghasilkan impact_score, dominant_factor, factor weights (menggunakan Macro fusion)

4. Alerts
- GET /api/public/alerts/live
  - Ambil alert terbaru

5. Device & market listing
- GET /api/public/market/list

API internal & fungsionalitas lain
---------------------------------
- Auth:
  - POST /api/auth/device/register  → registrasi device; mengembalikan token JWT & data-URL QR (PNG)
  - POST /api/auth/token            → dapatkan token untuk device terdaftar

- Validation:
  - POST /api/validation/price/check
    - Payload: {market_id, commodity, price, region?}
    - Respon: flags (zscore, iqr, ai, multi_source_ok), quarantined bool, sources mock
    - Jika dicurigai, entry akan dikarantina; otherwise ditambahkan ke window statistik

- Forecast engine:
  - GET /api/forecast/{commodity}  → forecast 7 hari (naïve model saat ini)
  - GET /api/forecast/confidence?commodity={}

- Supply chain:
  - GET /api/supply/stock/{entity_id}
  - GET /api/supply/route/analyze?route_id={}&distance_km={}

- Alerts:
  - POST /api/alerts/trigger  → memicu alert secara manual
  - WS  /api/alerts/ws         → subscribe alerts via WebSocket

- Blockchain:
  - POST /api/blockchain/append → tambahkan entri ke simple ledger
  - GET  /api/blockchain/integrity/check → verifikasi rantai hash

WebSocket endpoints (real-time)
-------------------------------
- /ws/prices         → (market_realtime_dashboard) streaming price_update yang menyertakan metadata impact
- /api/alerts/ws     → push alert real-time ke subscriber

Frontend dashboard
------------------
- Charting dashboard (Chart.js) menampilkan time-series harga dan "impact dots" ber-color-code.
  - Tooltip menunjukkan impact_score, dominant_factor, dan top factors_with_weights.
- Map dashboard (Leaflet) untuk heatmap harga per pasar.
- Frontend static assets ditempatkan di:
  - `market_realtime_dashboard/static/`
  - `smart_market_platform/dashboard/map/static/`

Architektur data & integritas
----------------------------
- Data harga masuk saat POST /ingest (atau via streamer eksternal).
- Sebelum diterima, data melewati Validation Engine (Z-score, IQR, AI stub, multi-source verify).
- Entry yang dicurigai akan dikarantina dan ditandai; operator/admin dapat mereview.
- Pilihan: setiap entri disimpan pada ledger blockchain sederhana (hash-chaining) untuk integritas audit trail.
- History time-series dapat disimpan di TimescaleDB / InfluxDB untuk produksi.

Impact Engine & Macro Fusion
----------------------------
- Impact engine menghitung price_change relatif, faktor-faktor yang berkontribusi, impact_score (0-100) dan dominant_factor.
- Macro data (inflation, fuel_coefficient, fertilizer_trend) memodifikasi score akhir.
- Output JSON menyertakan:
  - price_change
  - impact_score
  - dominant_factor
  - factors_with_weights (map faktor->persentase)

Validasi & Anti-Manipulasi (detil)
---------------------------------
- Outlier detection:
  - Z-Score dengan threshold (default 3.0)
  - IQR dengan multiplier (default 1.5)
- AI anomaly detector:
  - Stub/placeholder: relatif deviasi terhadap rolling median (layanan LSTM/Prophet dapat diganti/ditambahkan)
- Multi-source verification:
  - Mock feed (central_db, news_scrape, partner_feed) — produksi harus integrasikan real feed dan partner
- Quarantine logic:
  - Jika >= 2 validator menandai (mis. zscore & ai) atau multi-source mismatch → quarantined = true

Device onboarding & security
---------------------------
- Registrasi device menyimpan record pada DB (SQLModel)
- Token JWT dikeluarkan untuk device (sub = device_id, role)
- QR onboarding: response registrasi menyertakan data-url PNG QR berisi payload onboarding
- Role based access control: role sederhana (admin/operator/central), gunakan dependency injection FastAPI utk memeriksa role sebelum akses admin
- MQTT TLS: konfigurasi sertifikat dipersiapkan (MQTT_TLS_CERT/MQTT_TLS_KEY) — implementasi broker dan klien TLS harus dikonfigurasi selain platform ini

Forecasting & AI
----------------
- Module menyediakan:
  - route sederhana mengembalikan forecast 7 hari (naïve trend / ARIMA/Prophet/LSTM placeholders)
  - trainer utilities untuk menyimpan artifact sederhana
- Rekomendasi: gunakan Prophet atau pelatihan LSTM (TensorFlow/PyTorch) pada dataset historis (TimescaleDB) untuk akurasi produksi

Early Warning System (EWS)
--------------------------
- AlertsManager memonitor event (default: worker periodik).
- Memicu alert berdasarkan ambang (ALERT_THRESHOLD) dan rule yang Anda definisikan.
- Integrasi mock ke Telegram/WhatsApp; tambahkan token & implementasi produksi jika perlu.

Sentiment Analysis
------------------
- Simple sentiment analyzer: rule-based vocabulary bahasa Indonesia
- Mock social-data collector yang menghasilkan sample teks untuk korelasi dampak terhadap harga

Supply Chain Intelligence
-------------------------
- Route analyzer heuristik yang mengkombinasikan weather/traffic/disaster simulasi → estimasi delay
- Stock monitoring endpoint sederhana (warehouse/distributor/farmer)

Blockchain Integrity
--------------------
- Simple in-memory blockchain ledger:
  - append entry (POST /api/blockchain/append)
  - verify integrity (GET /api/blockchain/integrity/check)
- Untuk produksi pertimbangkan Hyperledger / managed ledger.

Integrasi dengan Smart Market Data Stream
----------------------------------------
- Arahkan streamer ke endpoint ingest/validation:
  - Set HTTP_ENDPOINT di `.env` ke: `http://<platform-host>:8000/ingest` (atau gunakan /api/validation/price/check)
- Setelah menerima payload, platform akan:
  - Validasi data
  - Hitung impact & macrodatas
  - Simpan/stream ke WebSocket
  - Kirim alert jika perlu
  - Simpan ke history & ledger (opsional)

Contoh penggunaan (curl)
------------------------
- Validasi harga:
  ```bash
  curl -X POST "http://localhost:8000/api/validation/price/check" \
    -H "Content-Type: application/json" \
    -d '{"market_id":"PASAR-001","commodity":"cabai","price":15000}'
  ```

- Register device:
  ```bash
  curl -X POST "http://localhost:8000/api/auth/device/register" \
    -H "Content-Type: application/json" \
    -d '{"market_id":"PASAR-001","device_id":"DEV-123","role":"operator"}'
  ```

- Append ledger:
  ```bash
  curl -X POST "http://localhost:8000/api/blockchain/append" -H "Content-Type: application/json" \
    -d '{"market_id":"PASAR-001","commodity":"cabai","price":15000}'
  ```

- Forecast:
  ```bash
  curl "http://localhost:8000/api/forecast/cabai"
  ```

Deployment & Docker
-------------------
Terdapat Dockerfile (development). Untuk production:
- Gunakan image yang memadai dan build dengan requirements terpasang.
- Gunakan PostgreSQL/TimescaleDB (DATABASE_URL ke asyncpg).
- Siapkan broker MQTT TLS (mosquitto/dedicated) dan konfigurasi sertifikat.
- Gunakan proses worker (Celery/Async background tasks) untuk training model & alerting skala besar.
- Gunakan reverse proxy (NGINX) dan TLS untuk endpoint HTTP.

Skalabilitas & Arsitektur Produksi
---------------------------------
- Pub/Sub real-time: gunakan Redis/NGINX + websocket broker (uvicorn + gunicorn dengan workers) atau dedicated pub/sub seperti NATS.
- Multi-instance: simpan state (history & ledger) di database/timeseries agar worker terdistribusi.
- Model training: jalankan di cluster terpisah (GPU) dan tarik model artifact via object storage.
- Keamanan: aktifkan RBAC, audit logging, rate limiting, TLS di semua layanan, validasi payload ketat.

Testing
-------
- Unit tests untuk komponen kritis (validation_engine, impact_engine, auth).
- Integration tests: runner yang men-simulasikan device posting dan mengecek aliran (validation → impact → alert).
- Gunakan test DB (SQLite in-memory) untuk CI.

Pengembangan lanjutan (roadmap singkat)
--------------------------------------
- Gantikan AI stub anomaly detector dengan model LSTM atau Prophet yang dilatih.
- Integrasi TimescaleDB/InfluxDB untuk historical retention & queries.
- Integrasi Pub/Sub (Redis/ Kafka) untuk scale out WebSocket broadcast.
- Implementasi role-based access & policy enforcement untuk endpoint admin/operator.
- Integrasi nyata ke Telegram/WhatsApp (via Bot API / official business API).
- Dashboard profesional (auth, multiple charts, user management).
- Docker Compose / Kubernetes manifests + Helm chart.

Kontribusi
----------
Silakan buka issue & pull request. Ikuti pedoman:
- Gunakan Python 3.11+
- Sertakan test & dokumentasi perubahan
- Format kode: black/isort/ruff

Lisensi
-------
MIT License — lihat file LICENSE untuk detail.

Kontak & Dukungan
-----------------
Jika perlu bantuan pengaturan atau integrasi, Anda dapat menambahkan issue di repository atau menghubungi tim pengembang yang mengelola solution ini.

---

Dokumentasi lebih lanjut, diagram arsitektur, dan contoh integrasi dapat disediakan sesuai permintaan (diagram deployment, ERD DB, sequence diagram aliran data).