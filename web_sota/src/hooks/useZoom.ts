import { useCallback, useEffect, useState } from "react";

/**
 * Mandatory fleet standard (nsis-build skill, Phase 1 "Frontend zoom hook").
 * Tauri windows have no native browser zoom -- without this, the app is
 * literally unusable at high-DPI or for anyone who wants larger text.
 *
 * Ctrl+Scroll cycles through ZOOM_LEVELS, Ctrl+0 resets to 1.0. Falls back
 * to CSS `zoom` (works in a dev browser too, where no Tauri window-scale
 * API is available). Persists to localStorage and re-applies on mount.
 */

const ZOOM_LEVELS = [0.5, 0.6, 0.7, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0] as const;
const STORAGE_KEY = "tauri-zoom";
const DEFAULT_ZOOM = 1.0;

function readStoredZoom(): number {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? Number.parseFloat(raw) : DEFAULT_ZOOM;
    return ZOOM_LEVELS.includes(parsed as (typeof ZOOM_LEVELS)[number])
      ? parsed
      : DEFAULT_ZOOM;
  } catch {
    return DEFAULT_ZOOM;
  }
}

function applyZoom(level: number) {
  // CSS zoom -- works both in Tauri's WebView and a plain dev browser.
  // (There's no cross-platform Tauri window-scale API as of 2.x; CSS
  // zoom on the root element is the fleet-standard approach.)
  document.documentElement.style.zoom = String(level);
}

export function useZoom() {
  const [zoom, setZoom] = useState<number>(() => readStoredZoom());

  useEffect(() => {
    applyZoom(zoom);
    try {
      localStorage.setItem(STORAGE_KEY, String(zoom));
    } catch {
      // localStorage unavailable (e.g. private browsing) -- zoom still
      // applies for this session, just doesn't persist. Not fatal.
    }
  }, [zoom]);

  const stepZoom = useCallback((direction: 1 | -1) => {
    setZoom((current) => {
      const idx = ZOOM_LEVELS.indexOf(current as (typeof ZOOM_LEVELS)[number]);
      const safeIdx = idx === -1 ? ZOOM_LEVELS.indexOf(DEFAULT_ZOOM) : idx;
      const nextIdx = Math.min(
        Math.max(safeIdx + direction, 0),
        ZOOM_LEVELS.length - 1,
      );
      return ZOOM_LEVELS[nextIdx];
    });
  }, []);

  const resetZoom = useCallback(() => setZoom(DEFAULT_ZOOM), []);

  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      if (!e.ctrlKey) return;
      e.preventDefault();
      stepZoom(e.deltaY < 0 ? 1 : -1);
    };
    const handleKeydown = (e: KeyboardEvent) => {
      if (!e.ctrlKey) return;
      if (e.key === "0") {
        e.preventDefault();
        resetZoom();
      }
    };
    // { passive: false } is required so preventDefault() on the wheel
    // event actually stops the browser's own Ctrl+Scroll page-zoom.
    window.addEventListener("wheel", handleWheel, { passive: false });
    window.addEventListener("keydown", handleKeydown);
    return () => {
      window.removeEventListener("wheel", handleWheel);
      window.removeEventListener("keydown", handleKeydown);
    };
  }, [stepZoom, resetZoom]);

  return { zoom, stepZoom, resetZoom };
}
