import { Box, Globe2, Cpu, ArrowRight, RefreshCw, CheckCircle2, AlertCircle, Users } from 'lucide-react';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { cn } from '@/common/utils';
import { apiUrl } from '@/lib/api-base';

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
    buttonText
}: IntegrationCardProps) {
    return (
        <div className="glass-card p-6 flex flex-col justify-between space-y-4 hover:border-indigo-500/30 transition-all group">
            <div className="space-y-3">
                <div className="p-3 rounded-xl bg-white/[0.04] w-fit group-hover:bg-indigo-500/10 transition-colors">
                    <Icon className="w-6 h-6 text-indigo-400" aria-hidden="true" />
                </div>
                <div>
                    <h3 className="text-lg font-bold text-white mb-1">{title}</h3>
                    <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
                </div>
            </div>

            <div className="space-y-3">
                {isSuccess && (
                    <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-2 rounded-lg border border-emerald-500/20">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Operation successful!
                    </div>
                )}
                {isError && (
                    <div className="flex items-center gap-2 text-xs text-red-400 bg-red-500/10 px-3 py-2 rounded-lg border border-red-500/20">
                        <AlertCircle className="w-3.5 h-3.5" />
                        {error || 'Operation failed'}
                    </div>
                )}

                <button
                    onClick={onAction}
                    disabled={isLoading}
                    title={buttonText}
                    aria-label={`${buttonText} integration`}
                    className={cn(
                        "w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all",
                        isLoading
                            ? "bg-white/[0.05] text-slate-500 cursor-not-allowed"
                            : "bg-indigo-500 hover:bg-indigo-600 text-white shadow-lg shadow-indigo-500/20"
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
    const [worldlabsStatus, setWorldlabsStatus] = useState<{ success?: boolean; error?: string }>({});
    const [blenderStatus, setBlenderStatus] = useState<{ success?: boolean; error?: string }>({});
    const [unityStatus, setUnityStatus] = useState<{ success?: boolean; error?: string }>({});

    const worldlabsMutation = useMutation({
        mutationFn: async () => {
            const resp = await fetch(apiUrl('/api/integrations/worldlabs/import'), { method: 'POST' });
            if (!resp.ok) throw new Error(await resp.text());
            return resp.json();
        },
        onSuccess: () => setWorldlabsStatus({ success: true }),
        onError: (e: Error) => setWorldlabsStatus({ error: e.message }),
    });

    const blenderMutation = useMutation({
        mutationFn: async () => {
            const resp = await fetch(apiUrl('/api/integrations/blender/import'), { method: 'POST' });
            if (!resp.ok) throw new Error(await resp.text());
            return resp.json();
        },
        onSuccess: () => setBlenderStatus({ success: true }),
        onError: (e: Error) => setBlenderStatus({ error: e.message }),
    });

    const unityMutation = useMutation({
        mutationFn: async () => {
            const resp = await fetch(apiUrl('/api/integrations/unity/avatar'), { method: 'POST' });
            if (!resp.ok) throw new Error(await resp.text());
            return resp.json();
        },
        onSuccess: () => setUnityStatus({ success: true }),
        onError: (e: Error) => setUnityStatus({ error: e.message }),
    });

    return (
        <div className="space-y-8 page-enter">
            <div>
                <h2 className="text-2xl font-bold text-white mb-2">Cross-Server Integrations</h2>
                <p className="text-slate-500">Bridge Resonite with WorldLabs, Blender, and Unity3D for advanced spatial workflows.</p>
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
                />

                <IntegrationCard
                    title="Blender Assets"
                    description="Export current Blender selection as GLB and spawn it in Resonite instantly."
                    icon={Box}
                    buttonText="Sync Selection"
                    onAction={() => blenderMutation.mutate()}
                    isLoading={blenderMutation.isPending}
                    isSuccess={blenderStatus.success}
                    isError={!!blenderStatus.error}
                    error={blenderStatus.error}
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
                />
            </div>

            <div className="glass-card p-6 border-indigo-500/20 bg-indigo-500/[0.02]">
                <div className="flex gap-4 items-start">
                    <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 mt-1">
                        <Cpu className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className="font-bold text-white mb-1">Fleet Discovery Active</h4>
                        <p className="text-sm text-slate-500 mb-4">
                            The Resonite MCP is automatically detecting compatible servers in your local fleet.
                            Ensure WorldLabs, Blender, and Unity3D MCP servers are running for these workflows to activate.
                        </p>
                        <div className="flex flex-wrap gap-2">
                            <span className="px-2 py-1 rounded bg-white/[0.04] border border-white/[0.08] text-[10px] uppercase tracking-wider text-slate-400 font-bold">worldlabs-mcp: active</span>
                            <span className="px-2 py-1 rounded bg-white/[0.04] border border-white/[0.08] text-[10px] uppercase tracking-wider text-slate-400 font-bold">blender-mcp: active</span>
                            <span className="px-2 py-1 rounded bg-white/[0.04] border border-white/[0.08] text-[10px] uppercase tracking-wider text-slate-400 font-bold">unity3d-mcp: active</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

