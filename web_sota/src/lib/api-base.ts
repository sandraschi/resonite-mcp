/// <reference types="vite/client" />

/** Backend origin: same-origin via Vite proxy in dev; absolute localhost only
 * inside Tauri (tauri://localhost has no host to proxy from); LAN/prod browser
 * tabs stay same-origin so the backend CORS list is not bypassed. */
declare global {
	interface Window {
		__TAURI__?: unknown;
		__TAURI_INTERNALS__?: unknown;
	}
}

function isTauri(): boolean {
	if (typeof window === "undefined") return false;
	return (
		"__TAURI__" in window ||
		"__TAURI_INTERNALS__" in window ||
		window.location.protocol === "tauri:"
	);
}

const BACKEND_ORIGIN =
	import.meta.env.DEV || !isTauri() ? "" : "http://127.0.0.1:10979";

export function apiUrl(path: string): string {
	const normalized = path.startsWith("/") ? path : `/${path}`;
	return `${BACKEND_ORIGIN}${normalized}`;
}

export const API_BASE =
	import.meta.env.DEV || !isTauri() ? "/api" : "http://127.0.0.1:10979/api";
