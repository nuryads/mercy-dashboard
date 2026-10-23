# V4 — perbaikan berdasarkan masukan

- Menggunakan `index.html` sebagai satu website utama, bukan `world.html` baru.
- GLB utama lebih detail: robot produksi, papan pabrik dengan tekstur, conveyor/packing, interior cutaway kantor-gudang yang terlihat dari kamera isometrik.
- Model pekerja diekspor dengan node `Arm_Left`, `Arm_Right`, `Leg_Left`, `Leg_Right`, sehingga lengan dan kaki bisa berayun ketika berjalan.
- Animasi barang datang: truk lewat jalur logistik, berhenti, forklift mengambil pallet lalu **mundur dengan orientasi tetap**, bukan memutar badan mendadak.
- Memperbaiki teleport pegawai saat pabrik diganti dari Tridaya ke Inna/KBI.
- Kamera mengikuti titik aksi saat truk masuk, forklift membongkar, dan staf masuk kantor.
- Aktivitas conveyor tetap bergerak walau tidak ada menu diklik.
- Panel data muncul **setelah adegan**; tersedia tombol **Lewati**.
- Cetak laporan setelah pratinjau tidak lagi memulai adegan kedua.
- Model pekerja, truk, forklift, gedung tersedia sebagai file GLB terpisah; skrip Blender berisi keyframe kendaraan dan pegawai.

Batasan: real-time collision engine/navmesh dan asset `.blend` jadi tidak termasuk; model dan animasi dinyatakan teruji sebatas pemeriksaan geometri dan UI simulasi sebelum deployment.
