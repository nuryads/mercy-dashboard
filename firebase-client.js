/* Firebase client: gunakan Firestore Rules untuk mengunci hak edit, bukan config.js. */
import { initializeApp } from 'https://www.gstatic.com/firebasejs/13.0.0/firebase-app.js';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/13.0.0/firebase-auth.js';
import { getFirestore, collection, doc, addDoc, updateDoc, deleteDoc, onSnapshot, getDocsFromServer, writeBatch, serverTimestamp } from 'https://www.gstatic.com/firebasejs/13.0.0/firebase-firestore.js';

export function startFirebase(config, callbacks) {
  const app = initializeApp(config.firebase);
  const auth = getAuth(app);
  const db = getFirestore(app);
  const orders = collection(db, 'mercy_orders');
  onAuthStateChanged(auth, user => callbacks.onAuth(user ? {email:user.email} : null), callbacks.onError);
  onSnapshot(orders, snapshot => callbacks.onRows(snapshot.docs.map(item => ({id:item.id,...item.data()})), {cache:snapshot.metadata.fromCache}), callbacks.onError);
  return {
    login: () => signInWithPopup(auth, new GoogleAuthProvider()),
    logout: () => signOut(auth),
    save: (id, fields) => id
      ? updateDoc(doc(db, 'mercy_orders', id), {...fields, updatedAt:serverTimestamp()})
      : addDoc(orders, {...fields, createdAt:serverTimestamp(), updatedAt:serverTimestamp()}),
    remove: (id) => deleteDoc(doc(db, 'mercy_orders', id)),
    importInitial: async (items) => {
      const live = await getDocsFromServer(orders);
      if (!live.empty) throw new Error('Database tidak kosong. Impor dibatalkan agar PO yang ada tidak tertimpa.');
      const batch = writeBatch(db);
      items.forEach((item, i) => {
        const {tgl,design,warna,qty,customer,kode,status} = item;
        batch.set(doc(db, 'mercy_orders', `awal-${String(i+1).padStart(4,'0')}`), {
          tgl, design, warna, qty, customer, kode, status,
          createdAt:serverTimestamp(), updatedAt:serverTimestamp()
        });
      });
      await batch.commit();
    }
  };
}
