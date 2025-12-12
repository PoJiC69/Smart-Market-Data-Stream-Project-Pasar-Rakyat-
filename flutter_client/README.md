```markdown
Tambahan: Background Foreground Service (Android)
------------------------------------------------

Ringkasan
- Implementasi menggunakan package flutter_foreground_task.
- Menjalankan Dart handler di isolate terpisah (SendTaskHandler) yang memanggil endpoint /ingest setiap interval.
- Data dikumpulkan dari SensorSimulator internal (pure Dart), sehingga tidak memerlukan plugin native di isolate.
- Konfigurasi token dan serverBase dikirim sebagai JSON ke foreground service saat memulai.
- AndroidManifest telah diperbarui untuk menambahkan permission FOREGROUND_SERVICE, WAKE_LOCK dan pendaftaran service/receiver plugin.

Langkah penggunaan
1. Pastikan dependency `flutter_foreground_task` sudah ditambahkan di pubspec.yaml.
2. Merge perubahan AndroidManifest yang disediakan.
3. Jalankan aplikasi di perangkat Android (emulator atau device nyata). Untuk emulator, fungsi foreground service bekerja tetapi beberapa behavior (doze, battery optim) berbeda.
4. Dari HomeScreen tekan "Start Background Service" setelah device sudah ter-registrasi (token tersimpan). Background service akan terus mengirim payload periodik.
5. Stop via tombol "Stop Background Service".

Catatan & batasan
- iOS: iOS tidak mengizinkan long-running background tasks kecuali beberapa kategori (audio, location, VOIP). Implementasi foreground service di iOS tidak tersedia; gunakan Background Fetch / Push notifications / native background modes sesuai kebutuhan.
- Keandalan / persistence: pada contoh ini kegagalan HTTP tidak ditangani dengan queue persisten di background isolate. Untuk produksi, perlu menambahkan mekanisme antrian persisten accessible dari background isolate (mis. sqlite + plugin yang mendukung background isolates, atau menyimpan ke file via dart:io).
- Permissions: pada Android 13+ perizinan tambahan mungkin diperlukan tergantung fitur. Pastikan optimasi baterai/Doze diatur untuk memungkinkan service berjalan jika diperlukan.
- Security: token disimpan di secure storage (flutter_secure_storage) pada UI side. Untuk background handler, token dikirim saat memulai layanan; pastikan token tidak ter-expose pada log.

Saran produksi
- Simpan payload yang gagal ke antrian persistent agar service dapat mem-flush saat jaringan kembali.
- Rotasi token berkala dan implementasikan refresh endpoint.
- Pertimbangkan penggunaan WorkManager (Android native) untuk kompatibilitas jangka panjang pada tugas periodik.