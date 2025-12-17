# Smart Market Platform — Platform Intelijen Pasar Nasional  
Versi: 0.1.0

> "Mengedepankan data pasar rakyat yang tervalidasi, real-time, dan dapat ditindaklanjuti — dari perangkat di lapangan hingga dashboard nasional."

---

Daftar Isi
- Ringkasan
- Fitur Utama
- Arsitektur & Komponen
- Persiapan & Quickstart (Pengembangan)
- Konfigurasi (.env)
- Endpoint & API Referensi
- Format Payload Contoh
- Device Client (Python) — Panduan lengkap
- Mobile Client (Flutter) — iOS & Android + Foreground Background Service
- Validasi & Anti-Manipulasi
- Impact Engine & Macro Fusion
- Forecasting & AI (overview)
- Early Warning System (EWS) & Alerts
- Blockchain Integrity
- Dashboard: Chart & Map (Realtime)
- Deployment & Produksi (best practices)
- Monitoring & Logging
- Testing & QA
- Roadmap & Pengembangan Selanjutnya
- Kontribusi
- Lisensi & Kontak
- Troubleshooting Singkat

---

Ringkasan
--------
Smart Market Platform (SMP) adalah platform modular untuk mengumpulkan, memverifikasi, menganalisis, dan memvisualisasikan data harga komoditas dari pasar rakyat Indonesia. Platform ini mendukung input dari perangkat IoT (HTTP/MQTT), validasi anti-manipulasi, engine perhitungan dampak harga (impact engine) yang terhubung dengan data makroekonomi, forecasting (AI/heuristik), sistem peringatan dini, sentiment analysis, dan opsi ledger blockchain untuk integritas.

Fitur Utama
-----------
- Input data: HTTP ingest, MQTT (TLS), dan device onboarding via QR + JWT
- Validasi & Anti-Manipulasi: Z-score, IQR, AI-stub, multi-source verification, quarantine
- Impact Engine: perhitungan impact_score, dominant_factor, faktor dengan bobot
- Macro fusion: inflasi, harga bahan bakar, nilai tukar, dampak ke score
- Forecast engine (naïve/ARIMA/Prophet/LSTM stub)
- Early Warning System (alert push; mock Telegram/WhatsApp)
- Sentiment analysis sederhana dan korelasi harga
- Blockchain ledger (hash chaining) untuk bukti integritas
- Dashboard realtime: Chart.js (impact dots) + Leaflet map (heatmap)
- Public API untuk developer dan admin
- Device client Python dan Mobile cross-platform (Flutter) dengan foreground service untuk Android

Arsitektur & Komponen
---------------------
Komponen utama:
- Backend FastAPI (modular):
  - smart_market_platform.main (entry point)
  - api/public, auth, validation_engine, supply_chain, forecast_engine, alerts, sentiment, macro_data, impact_engine, blockchain, dashboard/map
- Database: SQLModel (SQLite in dev), direkomendasikan PostgreSQL + TimescaleDB untuk produksi
- Device client:
  - Python async client (HTTP/MQTT) — local queue (SQLite), token management
  - Flutter mobile client (iOS/Android) — secure token, WebSocket, foreground service (Android)
- Frontend:
  - Static Chart.js dashboard (impact dots & tooltips)
  - Leaflet map heatmap
- Optional: MQTT broker (TLS), Redis/NATS for pub/sub, object storage untuk model artifacts

Persiapan & Quickstart (Pengembangan)
------------------------------------
Prerequisites:
- Python 3.11+
- Node/Flutter toolchain (jika menggunakan Mobile client)
- PostgreSQL (opsional, disarankan untuk produksi)
- MQTT broker (opsional; mosquitto)

1. Clone repository:
```bash
git clone <repo-url>
cd smart_market_platform
```

2. Virtual environment & instal dependensi backend:
```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
pip install --upgrade pip
pip install -r requirements.txt
```
```bash
Usage examples:
  python main.py --register --server http://localhost:8000
  python main.py --mode http --mock true --interval 2.0
```
3. Salin konfigurasi contoh:
```bash
cp .env.example .env
```
Edit `.env` sesuai kebutuhan (DATABASE_URL, JWT_SECRET, dsb).

4. Jalankan backend (development):
```bash
uvicorn smart_market_platform.main:app --reload --host 0.0.0.0 --port 8000
```

5. Jalankan device client Python (opsional) untuk simulasi:
```bash
python -m device_client.main --mode http --device-id DEV-001 --market-id PASAR-001 --mock true --interval 2.0
```

6. Jalankan Flutter mobile app (opsional):
- Atur `baseUrl` di `lib/services/api_service.dart` (10.0.2.2 untuk Android emulator).
```bash
cd flutter_client
flutter pub get
flutter run
```

Konfigurasi (.env)
------------------
Contoh parameter penting (lihat `.env.example`):
```
APP_NAME=Smart Market Platform
ENV=development
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./sm_platform.db
JWT_SECRET=replace_with_strong_secret
JWT_ALGORITHM=HS256
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=pasar/data
MQTT_TLS_CERT=./certs/mqtt_cert.pem
MQTT_TLS_KEY=./certs/mqtt_key.pem
ALERT_THRESHOLD=0.6
TELEGRAM_TOKEN=...
WHATSAPP_TOKEN=...
```

Endpoint & API Referensi (Ringkasan)
-----------------------------------
- Auth
  - POST /api/auth/device/register — registrasi device (market_id, device_id, role) → token + qr
  - POST /api/auth/token — mendapatkan token untuk device terdaftar
- Validation
  - POST /api/validation/price/check — periksa apakah harga outlier/ditandai/quarantine
- Ingest
  - POST /ingest — endpoint utama untuk ingest payload MarketDataStream
- Realtime & Dashboard
  - WebSocket /ws/prices — stream price_update (termasuk impact metadata)
  - GET /dashboard/map/ — peta heatmap
- Forecast
  - GET /api/forecast/{commodity}
  - GET /api/forecast/confidence?commodity=
- Public API (developer)
  - GET /api/public/commodity/price/live?commodity=
  - GET /api/public/commodity/price/history?commodity=&market_id=
  - GET /api/public/impact?commodity=&market_id=&prev_price=&new_price=
  - GET /api/public/alerts/live
- Blockchain
  - POST /api/blockchain/append
  - GET /api/blockchain/integrity/check
- Alerts WS
  - WebSocket /api/alerts/ws

Format Payload — Contoh
-----------------------
Payload yang dikirim device (misalnya ke /ingest):
```json
{
  "timestamp": "2025-12-12T12:34:56.789Z",
  "market_id": "PASAR-001",
  "device_id": "DEV-001",
  "region": "JAKARTA",
  "temperature": 29.5,
  "humidity": 72.3,
  "crowd": 12,
  "prices": {
    "cabai": 15000,
    "bawang": 9000,
    "beras": 12000
  }
}
```

Contoh curl
```bash
# Registrasi device
curl -X POST "http://localhost:8000/api/auth/device/register" \
 -H "Content-Type: application/json" \
 -d '{"market_id":"PASAR-001","device_id":"DEV-001","role":"operator"}'

# Mengirim data
curl -X POST "http://localhost:8000/ingest" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer <TOKEN>" \
 -d @payload.json
```

Device Client (Python) — Panduan Lengkap
---------------------------------------
Fitur client Python:
- Async (asyncio + aiohttp)
- Mode: HTTP / MQTT (paho-mqtt)
- Registrasi device & simpan token lokal (~/.smart_market_client/token.json)
- Queue lokal (SQLite) saat offline
- Flush queue worker dan retry interval
- Mock sensors built-in

Contoh menjalankan:
```bash
cd device_client
python main.py --register --server http://localhost:8000 --device-id DEV-001 --market-id PASAR-001
python main.py --mode http --device-id DEV-001 --market-id PASAR-001 --mock true --interval 2.0
```

Tips:
- Gunakan token JWT sebagai Authorization header untuk HTTP. Untuk MQTT, token dapat digunakan sebagai password atau gunakan mutual TLS (direkomendasikan).
- Queue local: file `~/.smart_market_client/queue.db` (SQLite). Periksa jika payload gagal.

Mobile Client (Flutter) — iOS & Android
---------------------------------------
Fitur mobile client:
- Register device & simpan token dengan `flutter_secure_storage`
- QR-code scan onboarding
- Send simulated sensor payloads periodically (HTTP/MQTT)
- WebSocket subscriber (realtime)
- Dashboard Chart (fl_chart) menampilkan impact dots
- Background/Foreground service (Android) untuk pengiriman terus menerus

Foreground / Background Service (Android)
- Implementasi menggunakan package `flutter_foreground_task`.
- Menjalankan handler `SendTaskHandler` pada isolate terpisah yang melakukan POST ke `/ingest` setiap interval (contoh 5s).
- Diperlukan permission di `AndroidManifest.xml`:
  - INTERNET, FOREGROUND_SERVICE, WAKE_LOCK, RECEIVE_BOOT_COMPLETED
- iOS: tidak ada support untuk long-running foreground service sama persis — gunakan Background Fetch, Push/VoIP, atau native background modes.

Cara pakai background service (Android):
1. Pastikan `flutter_foreground_task` ditambahkan di `pubspec.yaml`.
2. Merge perubahan `AndroidManifest.xml` sesuai instruksi.
3. Di aplikasi tekan "Start Background Service" — service akan berjalan di background meskipun aplikasi tidak aktif (subject to OEM battery optimizations).

Validasi & Anti-Manipulasi (Detail)
----------------------------------
- Z-Score (threshold default 3.0) — outlier statistik
- IQR (multiplier 1.5) — outlier berdasarkan quantiles
- AI Anomaly Detector (stub) — placeholder LSTM/Prophet; saat ini rule-based
- Multi-Source Verification — perbandingan mock terhadap sumber lain (central_db, partner_feed)
- Quarantine logic:
  - Jika >= 2 detector menandai OR multi-source mismatch → data dikarantina (quarantined=true)
  - Respon JSON berisi flags, sumber, dan status quarantined

Impact Engine & Macro Fusion
----------------------------
- Menghitung `price_change` (relatif), `impact_score` (0-100), `dominant_factor`, dan `factors_with_weights`.
- Faktor default: weather, pests, distribution, logistics, oversupply, seasonal_harvest, national_demand.
- Macro fusion (inflation, fuel, currency) menyesuaikan `impact_score`.
- Output ditambahkan ke payload yang disimpan & dikirim via WebSocket.

Forecasting & AI
----------------
- Module forecasting menyediakan endpoint sederhana:
  - Naïve linear trend (default dev)
  - Placeholder untuk Prophet, ARIMA (statsmodels), dan LSTM (TensorFlow/PyTorch)
- Endpoint:
  - GET /api/forecast/{commodity} → forecast_7d + confidence
- Training utilities sederhana tersedia (`forecast_engine/trainer.py`) — untuk produksi, gunakan dataset historis di TimescaleDB dan jalankan training di environment terpisah (GPU).

Early Warning System (EWS) & Alerts
-----------------------------------
- AlertsManager: push alert, simpan recent alerts, broadcast via WebSocket, mock-send ke Telegram/WhatsApp
- Thresholds configurable via `.env` (ALERT_THRESHOLD)
- Endpoint:
  - POST /api/alerts/trigger
  - WebSocket /api/alerts/ws

Blockchain Integrity
--------------------
- Simple in-memory blockchain ledger (hash chaining) untuk mencatat entri harga sebagai bukti integritas.
- Endpoints:
  - POST /api/blockchain/append — menambah block
  - GET /api/blockchain/integrity/check — verifikasi chain
- Produksi: pertimbangkan Hyperledger / managed ledger untuk audit dan immutability.

Dashboard: Chart & Map (Realtime)
--------------------------------
- Chart.js frontend: line chart + color-coded impact dots; tooltip menampilkan impact_score, dominant_factor, top factor weights.
- Map (Leaflet): heatmap layer untuk harga intensitas; update realtime via WebSocket.
- Frontend static assets tersedia di `market_realtime_dashboard/static` & `smart_market_platform/dashboard/map/static`.

Deployment & Produksi (Best Practices)
-------------------------------------
Rekomendasi arsitektur produksi:
- Backend: containerized FastAPI (uvicorn/gunicorn) + NGINX reverse proxy + TLS
- DB: PostgreSQL + TimescaleDB untuk time-series data
- Message broker: MQTT (mosquitto/emqx/vernemq) dengan TLS & mutual-auth; Redis/NATS/Kafka untuk pub/sub & scaling WebSocket
- Model serving: dedicated model server (TF Serving, TorchServe) atau batch jobs
- Secrets: simpan JWT secret, broker certs di secret manager (Vault/Kubernetes secrets)
- Logging & Observability: centralized logging (ELK/Opensearch), metrics (Prometheus + Grafana)
- Orchestration: Kubernetes + HPA, StatefulSets untuk TSDB
- CI/CD: lint/test/build pipelines, container image scanning

Contoh Docker (dev)
- Terdapat Dockerfile sederhana di repo; sesuaikan untuk production dengan multi-stage builds dan non-root user.

Monitoring & Logging
--------------------
- Logging menggunakan Python logging + rotating file handler (configurable).
- Telemetry: tambahkan metrics endpoints dan instrumentasi Prometheus.
- Alerting: integrasi dengan EWS & external notification channels (Telegram, WhatsApp, SMS).

Testing & QA
-----------
- Unit tests untuk components: validation_engine, impact_engine, auth
- Integration tests: simulate device posts, check validation->impact->alert flow
- Use test DB (SQLite in-memory) for CI
- Implement contract tests for public API

Roadmap & Pengembangan Selanjutnya
----------------------------------
Prioritas jangka pendek:
- Integrasi TimescaleDB / InfluxDB untuk storage
- Ganti AI anomaly stub dengan LSTM/Prophet terlatih
- Replace in-memory WebSocket broker with Redis pub/sub for scale-out
- Add RBAC enforcement & audit logging

Prioritas jangka menengah:
- Production-grade MQTT + certificate management
- Persistent queue & encryption at rest for device clients
- Mobile app improvements: background encrypted queue, OTA firmware update
- Docker Compose / Kubernetes manifests & Helm charts

Kontribusi
----------
Semua kontribusi dipersilakan melalui Pull Request:
- Gunakan Python 3.11+
- Sertakan unit tests untuk fitur baru
- Format code: black / isort / ruff
- Ikuti model branching git-flow

Lisensi
-------
MIT License — lihat file LICENSE.

Kontak & Dukungan
-----------------
Untuk dukungan, integrasi, atau pengembangan fitur berbayar:
- Buka Issue di repository
- Atau hubungi tim maintainers (tambahkan detail kontak internal di sini jika diperlukan)

Troubleshooting Singkat
-----------------------
- Server tidak merespon:
  - Pastikan uvicorn berjalan: `uvicorn smart_market_platform.main:app --reload`
  - Periksa `DATABASE_URL` dan konektivitas DB
- Device client enqueued items:
  - Periksa `~/.smart_market_client/queue.db` (sqlite)
  - Pastikan token valid dan server reachable
- WebSocket tidak menerima update:
  - Pastikan WS endpoint path benar (`/ws/prices`) dan klien menyertakan query params yang sesuai
- Mobile background service tidak jalan di Android:
  - Periksa permission (FOREGROUND_SERVICE, WAKE_LOCK)
  - Periksa baterai optimization/Doze — tambahkan pengecualian pada device testing

---

Terima kasih telah menggunakan Smart Market Platform.  
Jika Anda ingin, saya bisa:
- Menyediakan diagram sequence/data flow (SVG/Markdown)
- Menghasilkan contoh Docker Compose untuk stack (backend + Postgres + MQTT + Redis)
- Menyusun playbook migrasi ke TimescaleDB dan integrasi model LSTM lengkap

Silakan beri tahu langkah mana yang ingin Anda prioritaskan.

<img width="1366" height="768" alt="Screenshot_2025-12-17_21_52_13" src="https://github.com/user-attachments/assets/9e9c54df-db12-47b5-a35e-faf6a14f013e" />

