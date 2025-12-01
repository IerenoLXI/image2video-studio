const DEFAULT_BACKEND_URL = "https://image2video-studio.onrender.com";

export const BACKEND_URL =
  (import.meta.env?.VITE_BACKEND_URL || DEFAULT_BACKEND_URL).replace(/\/$/, "");
