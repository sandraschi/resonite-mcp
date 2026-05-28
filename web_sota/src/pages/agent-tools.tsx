import {
  Bot,
  FlaskConical,
  GitPullRequest,
  Layers,
  Package,
  Server,
  User,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  callTool,
  clearStagingGallery,
  getBackendHealth,
  loadStagingGallery,
  saveStagingSnapshot,
  type StagingRecord,
} from "@/api/mcp";

type TabId = "runtime" | "fleet" | "staging" | "vrm" | "pipeline";

function ResultBox({ text }: { text: string | null }) {
  if (!text) return null;
  return (
    <pre className="mt-3 p-3 text-xs bg-slate-900 rounded-lg overflow-x-auto whitespace-pre-wrap border border-slate-800 text-slate-300">
      {text}
    </pre>
  );
}

export function AgentTools() {
  const [tab, setTab] = useState<TabId>("runtime");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [gallery, setGallery] = useState<StagingRecord[]>([]);

  const [inputDir, setInputDir] = useState(
    "D:/Temp/fleet_pipeline/inkscape_sim_art/resonite_ui",
  );
  const [stagingDir, setStagingDir] = useState("D:/Temp/fleet_pipeline/resonite_fleet");
  const [objectName, setObjectName] = useState("Cube");
  const [texturePath, setTexturePath] = useState("D:/Temp/fleet_pipeline/textures/albedo.png");
  const [skipBlender, setSkipBlender] = useState(true);
  const [skipGimp, setSkipGimp] = useState(true);
  const [skipVrm, setSkipVrm] = useState(true);
  const [vrmDir, setVrmDir] = useState("D:/Temp/fleet_pipeline/resonite_fleet/models");
  const [avatarUrl, setAvatarUrl] = useState("http://127.0.0.1:10793");
  const [exportFormat, setExportFormat] = useState("vrm");
  const [protofluxPreset, setProtofluxPreset] = useState("vrm_blink");

  const tabs: { id: TabId; label: string; icon: typeof Bot }[] = [
    { id: "runtime", label: "Runtime", icon: Server },
    { id: "fleet", label: "Fleet", icon: GitPullRequest },
    { id: "staging", label: "Staging", icon: Layers },
    { id: "vrm", label: "VRM", icon: User },
    { id: "pipeline", label: "Pipeline", icon: Package },
  ];

  useEffect(() => {
    setGallery(loadStagingGallery());
  }, []);

  const run = async (tool: string, params: Record<string, unknown>) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await callTool(tool, params);
      setResult(JSON.stringify(res, null, 2));

      if (tool === "resonite_fleet" && params.operation === "list_staging" && res.success && res.data) {
        const data = res.data as Record<string, unknown>;
        const files = Array.isArray(data.files) ? (data.files as string[]) : [];
        const record: StagingRecord = {
          id: crypto.randomUUID(),
          stagingDir: String(params.input_dir ?? inputDir),
          fileCount: files.length,
          capturedAt: new Date().toISOString(),
          files: files.slice(0, 12),
        };
        saveStagingSnapshot(record);
        setGallery(loadStagingGallery());
      }
    } catch (e) {
      setResult(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  const checkBackend = async () => {
    const r = await getBackendHealth();
    setBackendOk(r.ok);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <FlaskConical className="h-6 w-6 text-indigo-400" aria-hidden="true" />
            Agent Lab
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Phase 1–3: execution mode, fleet handoff, VRM/avatar pipeline, ProtoFlux presets.
          </p>
        </div>
        <button
          type="button"
          onClick={checkBackend}
          className="px-3 py-1.5 text-sm bg-slate-800 text-slate-200 rounded-md hover:bg-slate-700"
        >
          Check backend
        </button>
      </div>

      {backendOk !== null && (
        <p className={`text-sm ${backendOk ? "text-emerald-400" : "text-red-400"}`}>
          Backend {backendOk ? "online" : "offline"} — run web_sota\start.ps1 if needed.
        </p>
      )}

      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm ${
              tab === id
                ? "bg-indigo-500/20 text-indigo-200 border border-indigo-500/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {label}
          </button>
        ))}
      </div>

      <div className="glass-card p-6 space-y-4">
        {tab === "runtime" && (
          <>
            <h3 className="font-semibold text-white">Runtime &amp; execution mode</h3>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm"
                onClick={() => run("resonite_fleet", { operation: "list_presets" })}
              >
                Fleet presets
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() => run("resonite_fleet", { operation: "execution_mode" })}
              >
                Execution mode
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() => run("health_check", {})}
              >
                Health check
              </button>
            </div>
          </>
        )}

        {tab === "fleet" && (
          <>
            <h3 className="font-semibold text-white">Fleet handoff</h3>
            <label className="block text-sm text-slate-300">
              Inkscape UI staging dir
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={inputDir}
                onChange={(e) => setInputDir(e.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-300">
              Resonite fleet staging dir
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={stagingDir}
                onChange={(e) => setStagingDir(e.target.value)}
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "list_staging",
                    input_dir: inputDir,
                    staging_dir: stagingDir,
                  })
                }
              >
                List staging
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "import_staged_assets",
                    input_dir: inputDir,
                    staging_dir: stagingDir,
                  })
                }
              >
                Import staged
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "pull_inkscape_ui",
                    input_dir: inputDir,
                    staging_dir: stagingDir,
                  })
                }
              >
                Pull inkscape UI
              </button>
            </div>
          </>
        )}

        {tab === "staging" && (
          <>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white">Staging gallery</h3>
              <button
                type="button"
                className="text-sm text-slate-400 hover:text-white"
                onClick={() => {
                  clearStagingGallery();
                  setGallery([]);
                }}
              >
                Clear
              </button>
            </div>
            {gallery.length === 0 ? (
              <p className="text-sm text-slate-500">No snapshots yet. Run list_staging first.</p>
            ) : (
              <ul className="space-y-2 text-sm text-slate-300">
                {gallery.map((entry) => (
                  <li
                    key={entry.id}
                    className="rounded-md border border-slate-800 bg-slate-900/50 p-3"
                  >
                    <div className="font-medium text-white">{entry.stagingDir}</div>
                    <div className="text-xs text-slate-500 mt-1">
                      {entry.fileCount} file(s) · {new Date(entry.capturedAt).toLocaleString()}
                    </div>
                    {entry.files.length > 0 && (
                      <ul className="mt-2 text-xs text-slate-500 list-disc pl-4">
                        {entry.files.map((f) => (
                          <li key={f} className="truncate">
                            {f}
                          </li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        {tab === "vrm" && (
          <>
            <h3 className="font-semibold text-white">VRM &amp; avatar pipeline</h3>
            <label className="block text-sm text-slate-300">
              VRM staging dir
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={vrmDir}
                onChange={(e) => setVrmDir(e.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-300">
              Avatar-mcp URL
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={avatarUrl}
                onChange={(e) => setAvatarUrl(e.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-300">
              Blender object (VRM export)
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={objectName}
                onChange={(e) => setObjectName(e.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-300">
              Export format
              <select
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
              >
                <option value="vrm">vrm</option>
                <option value="glb">glb</option>
              </select>
            </label>
            <label className="block text-sm text-slate-300">
              ProtoFlux preset
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={protofluxPreset}
                onChange={(e) => setProtofluxPreset(e.target.value)}
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "list_vrm_staging",
                    vrm_dir: vrmDir,
                    staging_dir: stagingDir,
                  })
                }
              >
                List VRM staging
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "import_vrm_batch",
                    vrm_dir: vrmDir,
                    staging_dir: stagingDir,
                  })
                }
              >
                Import VRM batch
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "pull_avatar_vrm",
                    vrm_dir: vrmDir,
                    avatar_url: avatarUrl,
                    staging_dir: stagingDir,
                  })
                }
              >
                Pull avatar VRM
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "pull_blender_vrm",
                    object_name: objectName,
                    vrm_dir: vrmDir,
                    export_format: exportFormat,
                  })
                }
              >
                Pull blender VRM
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-slate-800 text-slate-200 rounded-md text-sm"
                onClick={() =>
                  run("resonite_fleet", {
                    operation: "list_protoflux_presets",
                    protoflux_preset: protofluxPreset,
                  })
                }
              >
                ProtoFlux preset
              </button>
            </div>
          </>
        )}

        {tab === "pipeline" && (
          <>
            <h3 className="font-semibold text-white">Full fleet pipeline</h3>
            <label className="block text-sm text-slate-300">
              Blender object (optional)
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={objectName}
                onChange={(e) => setObjectName(e.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-300">
              GIMP texture path (optional)
              <input
                className="mt-1 w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-md text-sm text-white"
                value={texturePath}
                onChange={(e) => setTexturePath(e.target.value)}
              />
            </label>
            <div className="flex flex-wrap gap-4 text-sm text-slate-300">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={skipBlender}
                  onChange={(e) => setSkipBlender(e.target.checked)}
                />
                Skip blender
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={skipGimp}
                  onChange={(e) => setSkipGimp(e.target.checked)}
                />
                Skip gimp
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={skipVrm}
                  onChange={(e) => setSkipVrm(e.target.checked)}
                />
                Skip VRM
              </label>
            </div>
            <button
              type="button"
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm"
              onClick={() =>
                run("resonite_fleet", {
                  operation: "run_fleet_pipeline",
                  input_dir: inputDir,
                  staging_dir: stagingDir,
                  vrm_dir: vrmDir,
                  object_name: objectName,
                  texture_path: texturePath,
                  skip_blender: skipBlender,
                  skip_gimp: skipGimp,
                  skip_vrm: skipVrm,
                  export_format: exportFormat,
                })
              }
            >
              Run fleet pipeline
            </button>
          </>
        )}

        <ResultBox text={result} />
      </div>
    </div>
  );
}
