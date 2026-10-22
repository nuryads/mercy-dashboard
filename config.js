// KONFIGURASI FIREBASE (bukan password/secret). Salin persis dari Firebase Console > Project settings > Your apps > Web app.
// Setelah diisi, GitHub Pages bisa mengambil data Firestore secara real-time.
// adminEmail harus sama dengan email Google untuk login dan juga EMAIL_ADMIN_GANTI di firestore.rules.
window.MERCY_CONFIG = {
  firebase: {
    apiKey: "",
    authDomain: "",
    projectId: "",
    appId: "",
    messagingSenderId: ""
  },
  adminEmail: ""
};
