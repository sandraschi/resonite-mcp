import { useMutation } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowRight,
  Box,
  CheckCircle2,
  Cpu,
  Globe2,
  RefreshCw,
  Users,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";

interface IntegrationCardProps {
  title: string;
  description: string;
  icon: React.ElementType;
  onAction: () => void;
  isLoading?: boolean;
  isSuccess?: boolean;
  isError?: boolean;
  error?: string;
  buttonText: string;
  inputLabel?: string;
  inputValue?: string;
  onInputChange?: (val: string) => void;
  inputPlaceholder?: string;
}

function IntegrationCard({
  title,
  description,
  icon: Icon,
  onAction,
  isLoading,
  isSuccess,
  isError,
  error,
  buttonText,
  inputLabel,
  inputValue,
  onInputChange,
  inputPlaceholder,
}: IntegrationCardProps) {
  return (
    <div className="glass-card p-6 flex flex-col justify-between space-y-4 hover:border-indigo-500/30 transition-all group">
      <div className="space-y-3">
        <div className="p-3 rounded-xl bg-white/[0.04] w-fit group-hover:bg-indigo-500/10 transition-colors">
          <Icon className="w-6 h-6 text-indigo-400" aria-hidden="true" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white mb-1">{title}</h3>
          <p className="text-sm text-slate-500 leading-relaxed">
            {description}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {inputLabel && onInputChange && (
          <div>
            <label
              htmlFor={`integration-input-${title}`}
              className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block mb-1"
            >
              {inputLabel}
            </label>
            <input
              id={`integration-input-${title}`}
              value={inputValue ?? ""}
              onChange={(e) => onInputChange(e.target.value)}
              placeholder={inputPlaceholder}
              title={inputLabel}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono focus:border-indigo-500/50 focus:outline-none transition-colors"
            />
          </div>
        )}
        {isSuccess && (
          <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-2 rounded-lg border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Operation successful!
          </div>
        )}
        {isError && (
          <div className="flex items-center gap-2 text-xs text-red-400 bg-red-500/10 px-3 py-2 rounded-lg border border-red-500/20">
            <AlertCircle className="w-3.5 h-3.5" />
            {error || "Operation failed"}
          </div>
        )}

        <button
          type="button"
          onClick={onAction}
          disabled={!!(isLoading || (inputLabel && !inputValue))}
          title={buttonText}
          aria-label={`${buttonText} integration`}
          className={cn(
            "w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all",
            !!(isLoading || (inputLabel && !inputValue))
              ? "bg-white/[0.05] text-slate-500 cursor-not-allowed"
              : "bg-indigo-500 hover:bg-indigo-600 text-white shadow-lg shadow-indigo-500/20",
          )}
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              {buttonText}
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export function Integrations() {
  const [splatUrl, setSplatUrl] = useState("");
  const [objectName, setObjectName] = useState("");
  const [avatarPath, setAvatarPath] = useState("");

  const [worldlabsStatus, setWorldlabsStatus] = useState<{
    success?: boolean;
    error?: string;
  }>({});
  const [blenderStatus, setBlenderStatus] = useState<{
    success?: boolean;
    error?: string;
  }>({});
  const [unityStatus, setUnityStatus] = useState<{
    success?: boolean;
    error?: string;
  }>({});

  const worldlabsMutation = useMutation({
    mutationFn: async () => {
      const resp = await fetch(apiUrl("/api/resonite/integrations/worldlabs"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ splat_url: splatUrl }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      return resp.json();
    },
    onSuccess: () => setWorldlabsStatus({ success: true }),
    onError: (e: Error) => setWorldlabsStatus({ error: e.message }),
  });

  const blenderMutation = useMutation({
    mutationFn: async () => {
      const resp = await fetch(apiUrl("/api/resonite/integrations/blender"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ object_name: objectName }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      return resp.json();
    },
    onSuccess: () => setBlenderStatus({ success: true }),
    onError: (e: Error) => setBlenderStatus({ error: e.message }),
  });

  const unityMutation = useMutation({
    mutationFn: async () => {
      const resp = await fetch(apiUrl("/api/resonite/integrations/unity"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ avatar_path: avatarPath }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      return resp.json();
    },
    onSuccess: () => setUnityStatus({ success: true }),
    onError: (e: Error) => setUnityStatus({ error: e.message }),
  });

  return (
    <div className="space-y-8 page-enter">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">
          Cross-Server Integrations
        </h2>
        <p className="text-slate-500">
          Bridge Resonite with WorldLabs, Blender, and Unity3D for advanced
          spatial workflows.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <IntegrationCard
          title="WorldLabs Splats"
          description="Import Marble/Chisel splat 'miniworlds' directly into your Resonite session."
          icon={Globe2}
          buttonText="Import Splat"
          onAction={() => worldlabsMutation.mutate()}
          isLoading={worldlabsMutation.isPending}
          isSuccess={worldlabsStatus.success}
          isError={!!worldlabsStatus.error}
          error={worldlabsStatus.error}
          inputLabel="Splat URL (required)"
          inputValue={splatUrl}
          onInputChange={setSplatUrl}
          inputPlaceholder="https://.../scene.spz"
        />

        <IntegrationCard
          title="Blender Assets"
          description="Export a named Blender object as GLB and spawn it in Resonite instantly."
          icon={Box}
          buttonText="Sync Selection"
          onAction={() => blenderMutation.mutate()}
          isLoading={blenderMutation.isPending}
          isSuccess={blenderStatus.success}
          isError={!!blenderStatus.error}
          error={blenderStatus.error}
          inputLabel="Blender object name (required)"
          inputValue={objectName}
          onInputChange={setObjectName}
          inputPlaceholder="Cube.001"
        />

        <IntegrationCard
          title="Unity Avatar Sync"
          description="Map Unity3D rig parameters to Resonite components for persistent avatar setups."
          icon={Users}
          buttonText="Sync Avatar"
          onAction={() => unityMutation.mutate()}
          isLoading={unityMutation.isPending}
          isSuccess={unityStatus.success}
          isError={!!unityStatus.error}
          error={unityStatus.error}
          inputLabel="Avatar path (required)"
          inputValue={avatarPath}
          onInputChange={setAvatarPath}
          inputPlaceholder="C:\path\to\avatar.fbx"
        />
      </div>

      <div className="glass-card p-6 border-indigo-500/20 bg-indigo-500/[0.02]">
        <div className="flex gap-4 items-start">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 mt-1">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-white mb-1">Not Auto-Detected</h4>
            <p className="text-sm text-slate-500">
              These integrations call resonite-mcp's own endpoints directly —
              there's no live fleet-discovery mechanism checking whether
              worldlabs-mcp, blender-mcp, or a Unity3D bridge are actually
              reachable. If an operation fails, check that the relevant service
              is running and reachable from this machine.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
