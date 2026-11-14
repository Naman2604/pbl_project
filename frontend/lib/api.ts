// Where the Flask backend lives.
// Set NEXT_PUBLIC_API_URL in Vercel (or in .env.local) to point at your own backend;
// if it isn't set we fall back to the original Render URL.
export const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "https://pbl-project-s2qp.onrender.com"
).replace(/\/+$/, "");
