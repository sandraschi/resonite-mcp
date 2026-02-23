import { Activity, Wifi, WifiOff, RefreshCw, Globe2, Users, Layers } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { cn } from '@/common/utils';

interface PlatformInfo {
    version?: string;
    build?: string;
    status?: string;
}

interface SessionInfo {
    sessionId?: string;
    name?: string;
    activeUsers?: number;
    maxUsers?: number;
    hostUsername?: string;
    universeId?: string;
}

async function fetchStatus(): Promise<{ platform: PlatformInfo; sessions: SessionInfo[] }> {
    const [pfResp, sessResp] = await Promise.allSettled([
        fetch('/api/platform').then(r => r.json()),
        fetch('/api/sessions').then(r => r.json()),
    ]);
    return {
        platform: pfResp.status === 'fulfilled' ? (pfResp.value as PlatformInfo) : {},
        sessions: sessResp.status === 'fulfilled' ? ((sessResp.value as SessionInfo[]).slice(0, 8)) : [],
    };
}

function StatCard({ label, value, icon: Icon, color = 'text-indigo-400' }: { label: string; value: string | number; icon: React.ElementType; color?: string }) {
    return (
        <div className="glass-card p-4 flex items-center gap-4">
            <div className="p-2.5 rounded-lg bg-white/[0.04]">
                <Icon className={cn('w-5 h-5', color)} aria-hidden="true" />
            </div>
            <div>
                <p className="text-xs text-slate-500">{label}</p>
                <p className="text-lg font-bold text-white">{value}</p>
            </div>
        </div>
    );
}

export function Status() {
    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ['status'],
        queryFn: fetchStatus,
        refetchInterval: 30_000,
    });

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Activity className="w-5 h-5 text-indigo-400" aria-hidden="true" />
                    <div>
                        <h2 className="text-lg font-bold gradient-text">System Status</h2>
                        <p className="text-sm text-slate-500">Resonite platform health &amp; live sessions</p>
                    </div>
                </div>
                <button
                    onClick={() => refetch()}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.07] text-xs text-slate-400 hover:text-white transition-all"
                    aria-label="Refresh status"
                >
                    <RefreshCw className="w-3.5 h-3.5" aria-hidden="true" />
                    Refresh
                </button>
            </div>

            {/* Connection banner */}
            <div className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl border text-sm',
                isError ? 'bg-red-500/10 border-red-500/20 text-red-300' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
            )}>
                {isError ? <WifiOff className="w-4 h-4" aria-hidden="true" /> : <Wifi className="w-4 h-4" aria-hidden="true" />}
                {isError ? 'Cannot reach Resonite API — check your connection or RESONITE_TOKEN' : 'Connected to api.resonite.com'}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                <StatCard label="Platform version" value={data?.platform?.version ?? (isLoading ? '…' : 'N/A')} icon={Layers} />
                <StatCard label="Public sessions" value={data?.sessions?.length ?? (isLoading ? '…' : 0)} icon={Globe2} color="text-emerald-400" />
                <StatCard label="Active users (sampled)" value={data?.sessions?.reduce((acc, s) => acc + (s.activeUsers ?? 0), 0) ?? 0} icon={Users} color="text-purple-400" />
            </div>

            {/* Live sessions */}
            <div className="glass-card p-4 space-y-3">
                <h3 className="text-sm font-semibold text-slate-400">Public Sessions (top 8)</h3>
                {isLoading && <p className="text-xs text-slate-600">Loading…</p>}
                {isError && <p className="text-xs text-red-400">Failed to load sessions</p>}
                {data?.sessions && data.sessions.length === 0 && <p className="text-xs text-slate-600">No sessions found</p>}
                {data?.sessions?.map((s, i) => (
                    <div key={s.sessionId ?? i} className="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0">
                        <div>
                            <p className="text-sm text-slate-200">{s.name ?? 'Unnamed session'}</p>
                            <p className="text-xs text-slate-500">Host: {s.hostUsername ?? 'unknown'}</p>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-slate-400">
                            <Users className="w-3 h-3" aria-hidden="true" />
                            {s.activeUsers ?? 0}/{s.maxUsers ?? '?'}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
