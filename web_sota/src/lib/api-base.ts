/** Backend origin for Tauri / production builds (Vite dev uses proxy). */
const BACKEND_ORIGIN = import.meta.env.DEV ? "" : "http://127.0.0.1:10979";

export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BACKEND_ORIGIN}${normalized}`;
}

export const API_BASE = import.meta.env.DEV ? "/api" : "http://127.0.0.1:10979/api";
