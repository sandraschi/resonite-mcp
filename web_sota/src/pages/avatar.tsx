import { User, Sliders, RefreshCw, Zap, Camera, Move, Wand2, Activity, Eye, ShieldCheck, Play, Sparkles, Binary, Fingerprint, Layers } from 'lucide-react';
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { cn } from '../common/utils';

interface AvatarInfo {
    name?: string;
    id?: string;
    isEquipped?: boolean;
    parameters?: Record<string, string | number | boolean>;
    thumbnail?: string;
}

export function AvatarPage() {
    const [selectedParam, setSelectedParam] = useState<string | null>(null);

    const { data: avatarInfo, isLoading, refetch, isRefetching } = useQuery({
        queryKey: ['avatar'],
        queryFn: async (): Promise<AvatarInfo> => {
            const r = await fetch('/api/resonite/avatar/info');
            if (!r.ok) {
                // Mock data for simulation if API fails
                return {
                    name: 'Sandra Schipal',
                    id: 'res_u-4f2d-908b-62d25f8b482b',
                    isEquipped: true,
                    parameters: {
                        'VoiceIntensity': 0.82,
                        'EyeTrack': true,
                        'LipSync': 0.45,
                        'GestureSmoothing': 0.3,
                        'NeuralSync': true,
                        'EmoteGain': 1.0
                    }
                };
            }
            return r.json();
        }
    });

    const setParamMutation = useMutation({
        mutationFn: async ({ param, value }: { param: string, value: string | number | boolean }) => {
            const r = await fetch('/api/resonite/avatar/set_parameter', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ parameter: param, value })
            });
            return r.json();
        },
        onSuccess: () => refetch()
    });

    const resetPoseMutation = useMutation({
        mutationFn: async () => {
            const r = await fetch('/api/resonite/avatar/reset_pose', { method: 'POST' });
            return r.json();
        }
    });

    const locomotionMutation = useMutation({
        mutationFn: async (type: string) => {
            const r = await fetch('/api/resonite/avatar/locomotion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type })
            });
            return r.json();
        }
    });

    const killSequencesMutation = useMutation({
        mutationFn: async () => {
            const r = await fetch('/api/resonite/avatar/kill_sequences', { method: 'POST' });
            return r.json();
        }
    });

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-1">
                <div className="flex items-center gap-4">
                    <div className="relative">
                        <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                        <div className="relative bg-slate-900/50 p-3 rounded-2xl border border-white/10 glass-morphism">
                            <User className="w-7 h-7 text-purple-400" />
                        </div>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                            Avatar Neural Link
                            <Sparkles className="w-4 h-4 text-purple-400 animate-pulse" />
                        </h2>
                        <p className="text-sm text-slate-400 max-w-md">
                            Identity synchronization and biometric performance tuning
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => refetch()}
                        disabled={isLoading || isRefetching}
                        title="Refresh Avatar Data"
                        className="p-2.5 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-all border border-transparent hover:border-white/10 glass-morphism active:scale-95 disabled:opacity-50"
                    >
                        <RefreshCw className={cn("w-5 h-5", (isLoading || isRefetching) && "animate-spin")} />
                    </button>
                    <button className="flex items-center gap-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-lg shadow-purple-500/20 active:scale-95 border border-white/10">
                        <Camera className="w-4 h-4" />
                        Neural Capture
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Column: Avatar Identity & Metrics */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="group relative">
                        <div className="absolute -inset-0.5 bg-gradient-to-b from-purple-500/20 to-transparent rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition duration-700"></div>
                        <div className="relative glass-card overflow-hidden border-white/10 rounded-3xl">
                            <div className="aspect-[4/5] bg-slate-950 relative overflow-hidden">
                                {avatarInfo?.thumbnail ? (
                                    <img src={avatarInfo.thumbnail} alt="Avatar" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                                ) : (
                                    <div className="w-full h-full flex flex-col items-center justify-center gap-4 text-slate-800">
                                        <div className="p-8 rounded-full bg-white/[0.02] border border-white/[0.05]">
                                            <User className="w-20 h-20 opacity-20" />
                                        </div>
                                        <div className="flex flex-col items-center">
                                            <span className="text-[10px] font-bold uppercase tracking-[0.3em] opacity-30">Identity Matrix</span>
                                            <span className="text-xs font-mono opacity-20 mt-1">NO_SIG_DETECTED</span>
                                        </div>
                                    </div>
                                )}

                                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-60"></div>

                                <div className="absolute bottom-4 left-4 right-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2 glass-morphism px-3 py-1.5 rounded-full border border-white/10">
                                            <div className={cn("w-1.5 h-1.5 rounded-full", avatarInfo?.isEquipped ? "bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.6)]" : "bg-slate-500")}></div>
                                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-200">
                                                {avatarInfo?.isEquipped ? 'Active Link' : 'Standby'}
                                            </span>
                                        </div>
                                        <Fingerprint className="w-5 h-5 text-white/20" />
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 space-y-2 border-t border-white/[0.05] bg-white/[0.02]">
                                <h3 className="text-xl font-bold text-white tracking-tight">{avatarInfo?.name || 'Sandra Schipal'}</h3>
                                <div className="flex items-center gap-2">
                                    <Binary className="w-3 h-3 text-purple-500/50" />
                                    <p className="text-[10px] text-slate-500 font-mono tracking-tighter uppercase">{avatarInfo?.id || 'RES_XRAY_ALPHA_990'}</p>
                                </div>
                            </div>

                            <div className="p-2 grid grid-cols-3 gap-1 bg-black/40 border-t border-white/[0.05]">
                                <button className="p-3 flex flex-col items-center gap-1.5 rounded-2xl hover:bg-white/5 transition-all group/btn">
                                    <Zap className="w-4 h-4 text-slate-400 group-hover/btn:text-yellow-400 transition-colors" />
                                    <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500">Tune</span>
                                </button>
                                <button className="p-3 flex flex-col items-center gap-1.5 rounded-2xl hover:bg-white/5 transition-all group/btn border-x border-white/[0.05]">
                                    <Wand2 className="w-4 h-4 text-slate-400 group-hover/btn:text-purple-400 transition-colors" />
                                    <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500">Morph</span>
                                </button>
                                <button className="p-3 flex flex-col items-center gap-1.5 rounded-2xl hover:bg-white/5 transition-all group/btn">
                                    <ShieldCheck className="w-4 h-4 text-slate-400 group-hover/btn:text-emerald-400 transition-colors" />
                                    <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500">Auth</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card p-5 space-y-5 rounded-3xl border-white/10 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Activity className="w-16 h-16 text-white" />
                        </div>
                        <div className="flex items-center gap-2 text-indigo-400 border-b border-white/[0.05] pb-3">
                            <Activity className="w-4 h-4" />
                            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em]">Diagnostic Stream</h3>
                        </div>
                        <div className="space-y-5">
                            <div className="space-y-2">
                                <div className="flex justify-between items-end">
                                    <span className="text-[10px] font-bold uppercase text-slate-500">Geometric Load</span>
                                    <span className="text-xs font-mono text-white">42.1K <span className="text-[10px] opacity-30">tris</span></span>
                                </div>
                                <div className="h-1.5 bg-black/40 rounded-full overflow-hidden border border-white/[0.05]">
                                    <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.4)] w-[65%]" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex justify-between items-end">
                                    <span className="text-[10px] font-bold uppercase text-slate-500">Material Slots</span>
                                    <span className="text-xs font-mono text-white">8 <span className="text-[10px] opacity-30">/ 16</span></span>
                                </div>
                                <div className="h-1.5 bg-black/40 rounded-full overflow-hidden border border-white/[0.05]">
                                    <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.4)] w-[50%]" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex justify-between items-end">
                                    <span className="text-[10px] font-bold uppercase text-slate-500">VRAM Occupancy</span>
                                    <span className="text-xs font-mono text-white">124 <span className="text-[10px] opacity-30">MB</span></span>
                                </div>
                                <div className="h-1.5 bg-black/40 rounded-full overflow-hidden border border-white/[0.05]">
                                    <div className="h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full shadow-[0_0_8px_rgba(249,115,22,0.4)] w-[30%]" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Parameters and Controls */}
                <div className="lg:col-span-8 space-y-8">
                    <div className="glass-card p-1 rounded-3xl border-white/10 bg-white/[0.01]">
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-8">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20">
                                        <Sliders className="w-5 h-5 text-purple-400" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-white text-lg tracking-tight">Biometric Overrides</h3>
                                        <p className="text-xs text-slate-500">Real-time neural driver parameters</p>
                                    </div>
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                    <span className="flex items-center gap-1.5 text-[10px] text-emerald-400 uppercase tracking-widest font-bold">
                                        <div className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse"></div>
                                        Live Driver Synced
                                    </span>
                                    <span className="text-[9px] text-slate-600 font-mono">LATENCY: 12ms</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                                {Object.entries(avatarInfo?.parameters || {}).map(([key, value]) => (
                                    <div
                                        key={key}
                                        className={cn(
                                            "relative p-5 rounded-2xl border transition-all duration-300 group/item overflow-hidden",
                                            selectedParam === key
                                                ? 'bg-white/[0.05] border-purple-500/40 shadow-lg shadow-purple-500/5'
                                                : 'bg-black/40 border-white/[0.05] hover:border-white/20 hover:bg-white/[0.02]'
                                        )}
                                        onClick={() => setSelectedParam(key)}
                                    >
                                        <div className="absolute top-0 right-0 p-3 opacity-0 group-hover/item:opacity-100 transition-opacity">
                                            <div className="w-1.5 h-1.5 rounded-full bg-purple-500/50 blur-[2px]"></div>
                                        </div>

                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex flex-col">
                                                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-0.5">{key}</span>
                                                <span className="text-xs font-mono text-slate-300">
                                                    {typeof value === 'boolean' ? (value ? 'ENABLED' : 'DISABLED') : value}
                                                </span>
                                            </div>
                                            {typeof value === 'number' && (
                                                <div className="text-[10px] font-mono p-1 bg-purple-500/10 text-purple-400 rounded px-2 border border-purple-500/20">
                                                    {(value * 100).toFixed(0)}%
                                                </div>
                                            )}
                                        </div>

                                        {typeof value === 'number' && (
                                            <div className="relative pt-2">
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max="1"
                                                    step="0.01"
                                                    value={value}
                                                    title={`Adjust ${key}`}
                                                    aria-label={`Adjust ${key}`}
                                                    onChange={(e) => setParamMutation.mutate({ param: key, value: parseFloat(e.target.value) })}
                                                    className="w-full h-1 bg-white/5 rounded-full appearance-none cursor-pointer accent-purple-500 hover:accent-purple-400"
                                                />
                                                <progress
                                                    value={value as number || 0}
                                                    max={1}
                                                    className="absolute top-0 left-0 w-full h-1 bg-transparent accent-purple-500 rounded-full pointer-events-none opacity-40"
                                                />
                                            </div>
                                        )}

                                        {typeof value === 'boolean' && (
                                            <button
                                                onClick={(e) => { e.stopPropagation(); setParamMutation.mutate({ param: key, value: !value }); }}
                                                className={cn(
                                                    "w-full py-2 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all border",
                                                    value
                                                        ? 'bg-purple-500/20 border-purple-500/30 text-purple-400 shadow-[inset_0_0_12px_rgba(168,85,247,0.1)]'
                                                        : 'bg-white/5 border-white/10 text-slate-500 hover:bg-white/10'
                                                )}
                                            >
                                                {value ? 'Deactivate Channel' : 'Activate Channel'}
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <div className="glass-card p-6 space-y-5 rounded-3xl border-white/10 hover:border-indigo-500/30 transition-colors group">
                            <div className="flex items-center gap-3 text-indigo-400">
                                <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 group-hover:scale-110 transition-transform">
                                    <Eye className="w-5 h-5" />
                                </div>
                                <h3 className="text-xs font-black uppercase tracking-[0.2em]">Ocular Systems</h3>
                            </div>
                            <div className="grid grid-cols-1 gap-2">
                                <button
                                    onClick={() => setParamMutation.mutate({ param: 'EyeTrack', value: !avatarInfo?.parameters?.EyeTrack })}
                                    className="w-full bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 rounded-2xl py-3 text-[11px] font-bold uppercase tracking-widest text-slate-300 transition-all hover:translate-x-1 group/btn"
                                >
                                    <span className="flex items-center justify-center gap-2">
                                        Neural Gaze {avatarInfo?.parameters?.EyeTrack ? 'Lock' : 'Unlock'}
                                        <Wand2 className="w-3.5 h-3.5 opacity-0 group-hover/btn:opacity-50" />
                                    </span>
                                </button>
                                <button
                                    onClick={() => setParamMutation.mutate({ param: 'NeuralSync', value: !avatarInfo?.parameters?.NeuralSync })}
                                    className="w-full bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 rounded-2xl py-3 text-[11px] font-bold uppercase tracking-widest text-slate-300 transition-all hover:translate-x-1 group/btn"
                                >
                                    <span className="flex items-center justify-center gap-2">
                                        Focus {avatarInfo?.parameters?.NeuralSync ? 'Release' : 'Persistence'}
                                        <Activity className="w-3.5 h-3.5 opacity-0 group-hover/btn:opacity-50" />
                                    </span>
                                </button>
                            </div>
                        </div>

                        <div className="glass-card p-6 space-y-5 rounded-3xl border-white/10 hover:border-orange-500/30 transition-colors group">
                            <div className="flex items-center gap-3 text-orange-400">
                                <div className="p-2 rounded-xl bg-orange-500/10 border border-orange-500/20 group-hover:scale-110 transition-transform">
                                    <Move className="w-5 h-5" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-xs font-black uppercase tracking-[0.2em]">Locomotion Hooks</h3>
                                </div>
                                <div className="flex gap-1">
                                    <button
                                        onClick={() => locomotionMutation.mutate('walk')}
                                        title="Walk Mode"
                                        className="p-1 px-2 text-[8px] bg-white/5 border border-white/10 rounded hover:bg-white/10 text-slate-400 hover:text-white"
                                    >W</button>
                                    <button
                                        onClick={() => locomotionMutation.mutate('fly')}
                                        title="Fly Mode"
                                        className="p-1 px-2 text-[8px] bg-white/5 border border-white/10 rounded hover:bg-white/10 text-slate-400 hover:text-white"
                                    >F</button>
                                </div>
                            </div>
                            <div className="grid grid-cols-1 gap-2">
                                <button
                                    onClick={() => resetPoseMutation.mutate()}
                                    className="w-full bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 rounded-2xl py-3 text-[11px] font-bold uppercase tracking-widest text-slate-300 transition-all hover:translate-x-1"
                                >
                                    Reset Neural Pose
                                </button>
                                <button className="w-full bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 rounded-2xl py-3 text-[11px] font-bold uppercase tracking-widest text-slate-300 transition-all hover:translate-x-1">
                                    Global Scale Matrix
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card p-4 rounded-3xl border-white/10 bg-gradient-to-r from-purple-900/10 to-transparent relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Play className="w-24 h-24 text-white" />
                        </div>
                        <div className="flex flex-col sm:flex-row items-center justify-between gap-6 p-2">
                            <div className="flex gap-5 items-center">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-purple-500 blur-lg opacity-20 animate-pulse"></div>
                                    <div className="relative bg-black/40 p-4 rounded-2xl border border-purple-500/30 flex items-center justify-center shadow-lg">
                                        <Layers className="w-7 h-7 text-purple-400 animate-bounce" />
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    <h4 className="font-black text-white text-xl tracking-tight uppercase">Kinetic State</h4>
                                    <div className="flex items-center gap-2">
                                        <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Active Sequence:</span>
                                        <span className="text-sm font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">NEURAL_WAVE_SOTA</span>
                                    </div>
                                </div>
                            </div>
                            <button
                                onClick={() => killSequencesMutation.mutate()}
                                className="w-full sm:w-auto px-8 py-3.5 bg-white text-black rounded-2xl font-black text-[11px] uppercase tracking-[0.2em] hover:bg-slate-200 transition-all shadow-2xl shadow-white/10 hover:-translate-y-1 active:scale-95"
                            >
                                Kill All Sequences
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
