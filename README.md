# MERCY — Dashboard Online dengan Edit PO Langsung ✿

**Ini versi BARU yang bisa langsung input / edit / hapus PO di website**, tanpa membuka Google Sheets atau mengubah kode tiap ada PO. Website di GitHub Pages, database online di **Firebase Firestore**, login admin memakai Akun Google. Setelah disimpan, angka/grafik/tabel berubah pada semua browser yang sedang membuka website. Data awal 61 baris disediakan untuk impor satu kali.

> Penting: **GitHub Pages saja tidak bisa menyimpan data**. Agar tombol **Simpan** benar-benar bekerja untuk semua perangkat, kamu perlu membuat project Firebase dan mengisi `config.js` serta memasang `firestore.rules`. Aku tidak bisa membuatkan project Firebase atau login Google milikmu dari sini.

## LANGKAH 1 — Buat Firebase (sekali saja)

1. Buka https://console.firebase.google.com dan klik **Add project / Tambahkan project**. Beri nama misalnya `mercy-po-manager`.
2. Setelah project jadi, pilih **Build → Firestore Database → Create database**. Pilih database default `(default)` dan lokasi server sesuai kebutuhan. Pilih **Production mode** (jangan Test mode terbuka).
3. Masuk **Build → Authentication → Get started → Sign-in method → Google → Enable**; pilih email support bila diminta dan simpan.
4. Buka **Authentication → Settings → Authorized domains**, tambahkan domain GitHub milikmu seperti `NAMAUSER.github.io` (hanya domain, **tanpa** `https://` dan tanpa `/mercy-dashboard`). Login popup perlu domain ini ada dalam daftar.
5. Buka **Project settings** (ikon roda gigi di Firebase Console) → **Your apps → Add app → Web `</>`**. Daftarkan app dengan nama MERCY (tidak perlu mencentang Firebase Hosting). Copy object `firebaseConfig` yang tampil. Kamu **tidak perlu** menyalin script HTML `initializeApp`.

## LANGKAH 2 — Isi config.js (sekali saja)

Buka `config.js` di paket ini, isi contohnya seperti berikut **menggunakan nilai dari project kamu sendiri**:

```js
window.MERCY_CONFIG = {
  firebase: {
    apiKey: "API_KEY_DARI_FIREBASE",
    authDomain: "nama-project.firebaseapp.com",
    projectId: "nama-project",
    appId: "1:123456:web:abcdef",
    messagingSenderId: "123456789"
  },
  adminEmail: "emailkamu@gmail.com"
};
```

`firebaseConfig` bukan password rahasia dan memang disertakan di frontend web Firebase. **JANGAN** taruh password akun, private key, service account, atau token admin di repo. `adminEmail` untuk menampilkan UI; keamanan edit yang sesungguhnya di Firestore Rules (langkah 3).

## LANGKAH 3 — Kunci izin edit (WAJIB)

1. Buka file `firestore.rules` dalam ZIP, salin seluruh isinya.
2. Ganti `EMAIL_ADMIN_GANTI@gmail.com` menjadi **alamat Gmail yang sama** dengan `adminEmail` di `config.js`.
3. Di Firebase Console pilih **Firestore Database → Rules**, paste aturan tadi dan klik **Publish**.
4. Aturan ini mengizinkan **semua orang melihat** desain & PO (public read), tetapi **hanya admin login Google dengan email itu** yang boleh tambah, edit, atau hapus. Anggap data bisa dibaca oleh siapa pun yang punya URL atau akses Firebase project publik. Jangan simpan data yang rahasia.
5. Jangan memakai aturan `allow read, write: if true` karena itu membuka pengeditan kepada siapa pun.

## LANGKAH 4 — Upload ke GitHub Pages

1. Di GitHub buat repo baru bernama `mercy-dashboard` (**Public** untuk GitHub Pages gratis).
2. Upload **isi ZIP, bukan ZIP-nya** ke root repository: `index.html`, `app.js`, `firebase-client.js`, `config.js` yang telah kamu isi, `data.js`, `data.csv`, `.nojekyll` (opsional), `firestore.rules` (referensi), `README.md`.
3. Di repo buka **Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save**.
4. Website akan ada di `https://NAMAUSER.github.io/mercy-dashboard/`.

> Cek `Authentication → Settings → Authorized domains`: tambahkan `NAMAUSER.github.io`, jangan nama repo atau subfolder. Jika login ditolak `auth/unauthorized-domain`, periksa langkah ini.

## LANGKAH 5 — Impor 61 PO lama sekali saja

1. Buka web yang sudah online (GitHub Pages); pada koneksi awal Firebase, database memang kosong.
2. Klik **Masuk Admin**, login menggunakan Gmail yang kamu tetapkan di `config.js` dan `firestore.rules`.
3. Saat indikator bertuliskan **Firebase terhubung · database kosong**, klik tombol **⇧ Impor 61 data awal** lalu konfirmasi.
4. Semua 61 desain lama sekarang tersimpan di Firebase dan langsung muncul pada dashboard. Jangan klik impor ulang (tombol otomatis hilang saat sudah ada data).
5. Setelah itu **gunakan hanya dashboard online untuk tambah/edit/hapus PO**. Jangan lagi menggunakan `data.csv` untuk mengupdate data harian; file itu hanya cadangan data pertama.

## Cara tambah / edit / hapus PO setiap hari

- **Tambah PO:** klik **Masuk Admin → ＋ Tambah PO**, isi tanggal, desain, customer, warna, QTY, kode, dan status → **Simpan PO**.
- **Edit PO:** di tabel cari desain → klik **Edit** pada barisnya → ubah status / QTY / kode → **Simpan Perubahan**.
- **Hapus PO:** klik **Hapus** pada barisnya, konfirmasi. Penghapusan permanen; buat backup CSV rutin.
- Semua orang yang membuka web bisa melihat perubahan **real-time** tanpa refresh manual, selama internet dan Firebase tersambung.
- **Export ke Excel:** klik **Export Excel (CSV)**, buka file .csv di Excel atau impor ke Google Sheets. **Excel lama tidak otomatis tersinkron**, karena Firestore sekarang sumber utama. Jika ingin Google Sheets selalu terupdate secara otomatis juga, perlu integrasi tambahan, bukan fitur bawaan paket ini.

## Keamanan / catatan data

- Simpan API key Firebase biasa (`firebaseConfig`) di GitHub boleh; **jangan simpan service-account/private key**. Firestore Rules wajib untuk membatasi hak edit.
- Semua data MERCY yang diunggah ke repo dan Firestore dalam paket ini **dapat dibaca publik**. Jika data internal harus rahasia, kita perlu ubah Firestore Rules menjadi hanya user tertentu yang bisa membaca, serta menghapus `data.js` dan `data.csv` dari repo publik.
- Kalau ada anggota tim yang juga perlu mengedit, jangan sementara mengubah rules jadi terbuka. Tambah emailnya secara eksplisit ke kondisi `isAdmin()` (dan update tampilan admin kalau perlu).
- Firestore ada kuota penggunaan; untuk pemakaian normal yang kecil mungkin masuk dalam kuota gratis, tetapi bergantung pada kebijakan/limit Firebase. Lihat halaman pricing di Firebase.
- Tabel awal 61 baris; total QTY terisi dari baris 48.500, bukan total manual 40.000 pada dokumen asal.
- Ini bukan sinkronisasi dua arah dengan Excel / Google Sheets. Website menggunakan **Firestore**; CSV hanya untuk ekspor.

Referensi dokumentasi resmi:
- Firebase Web setup: https://firebase.google.com/docs/web/setup
- Login Google: https://firebase.google.com/docs/auth/web/google-signin
- Firestore rules: https://firebase.google.com/docs/firestore/security/rules-conditions
- Realtime listeners: https://firebase.google.com/docs/firestore/query-data/listen
- GitHub Pages: https://docs.github.com/en/pages/quickstart
