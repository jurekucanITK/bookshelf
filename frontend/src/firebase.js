import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

// Spletna konfiguracija Firebase ni skrivnost (je v vsakem brskalniku),
// dostop varujeta Firebase in preverjanje zetona na backendu.
// Drug Firebase projekt (npr. za namestitev) se nastavi z VITE_FIREBASE_* (.env.example).
const env = import.meta.env
const firebaseConfig = {
  apiKey: env.VITE_FIREBASE_API_KEY || 'AIzaSyDVb6-6WZmqwch4DKcyYVy02sg-b9FKI1U',
  authDomain: env.VITE_FIREBASE_AUTH_DOMAIN || 'rirs-bookshelf.firebaseapp.com',
  projectId: env.VITE_FIREBASE_PROJECT_ID || 'rirs-bookshelf',
  storageBucket: env.VITE_FIREBASE_STORAGE_BUCKET || 'rirs-bookshelf.firebasestorage.app',
  messagingSenderId: env.VITE_FIREBASE_MESSAGING_SENDER_ID || '582214925548',
  appId: env.VITE_FIREBASE_APP_ID || '1:582214925548:web:f8d552be6f92ea9b7739c9',
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)