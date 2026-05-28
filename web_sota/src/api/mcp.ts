/**
 * MCP API client for Resonite MCP webapp Agent Lab.
 * Backend: POST /api/v1/tool on port 10979 (proxied via Vite /api in dev).
 */

import { API_BASE } from "@/lib/api-base";

export async function getBackendHealth(): Promise<{ ok: boolean; error?: string }> {
  try {
    const r = await fetch(`${API_BASE}/v1/health`);
    if (!r.ok) return { ok: false, error: `HTTP ${r.status}` };
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Network error" };
  }
}

export interface MCPResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export async function callTool<T>(
  tool: string,
  params: Record<string, unknown> = {},
): Promise<MCPResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}/v1/tool`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool, params }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return (await response.json()) as MCPResponse<T>;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

export interface StagingRecord {
  id: string;
  stagingDir: string;
  fileCount: number;
  capturedAt: string;
  files: string[];
}

const STAGING_KEY = "resonite_mcp_staging_gallery";

export function loadStagingGallery(): StagingRecord[] {
  try {
    const raw = localStorage.getItem(STAGING_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as StagingRecord[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveStagingSnapshot(record: StagingRecord): void {
  const existing = loadStagingGallery();
  const next = [record, ...existing].slice(0, 16);
  localStorage.setItem(STAGING_KEY, JSON.stringify(next));
}

export function clearStagingGallery(): void {
  localStorage.removeItem(STAGING_KEY);
}
