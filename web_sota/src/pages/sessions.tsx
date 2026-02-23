import { useState } from 'react';
import { Globe2, Search, Users, Lock, Unlock } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { cn } from '@/common/utils';

interface Session {
    sessionId: string;
    name?: string;
    activeUsers?: number;
    maxUsers?: number;
    hostUsername?: string;
    sessionAccessLevel?: string;
    universeId?: string;
}

async function fetchSessions(name: string): Promise<Session[]> {
    const params = new URLSearchParams();
    if (name) params.set('name', name);
    const r = await fetch(`/api/sessions?${params}`);
    if (!r.ok) throw new Error('Failed to fetch sessions');
    return r.json() as Promise<Session[]>;
}

export function Sessions() {
    const [search, setSearch] = useState('');
    const [query, setQuery] = useState('');

    const { data, isLoading, isError } = useQuery({
        queryKey: ['sessions', query],
        queryFn: () => fetchSessions(query),
        refetchInterval: 30_000,
    });

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center gap-3">
                <Globe2 className="w-5 h-5 text-indigo-400" aria-hidden="true" />
                <div>
                    <h2 className="text-lg font-bold gradient-text">World Sessions</h2>
                    <p className="text-sm text-slate-500">Browse public Resonite sessions</p>
                </div>
            </div>

            <div className="glass-card p-4">
                <div className="flex gap-2">
                    <input
                        type="search"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && setQuery(search)}
                        placeholder="Search session name…"
                        className="input-glass flex-1 text-sm"
                        aria-label="Search sessions by name"
                    />
                    <button
                        onClick={() => setQuery(search)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600/40 hover:bg-indigo-600/60 border border-indigo-500/30 text-sm text-indigo-300 transition-all"
                        aria-label="Search"
                    >
                        <Search className="w-4 h-4" aria-hidden="true" />
                        Search
                    </button>
                </div>
            </div>

            {isLoading && <p className="text-sm text-slate-600">Loading sessions…</p>}
            {isError && <p className="text-sm text-red-400">Failed to load sessions from api.resonite.com</p>}

            <div className="space-y-2">
                {data?.map(s => (
                    <div key={s.sessionId} className="glass-card p-4 flex items-center justify-between">
                        <div className="space-y-0.5">
                            <div className="flex items-center gap-2">
                                {s.sessionAccessLevel === 'Private' ? (
                                    <Lock className="w-3.5 h-3.5 text-slate-500" aria-label="Private" />
                                ) : (
                                    <Unlock className="w-3.5 h-3.5 text-emerald-500" aria-label="Public" />
                                )}
                                <p className="text-sm font-medium text-slate-100">{s.name ?? 'Unnamed'}</p>
                            </div>
                            <p className="text-xs text-slate-500">Host: {s.hostUsername ?? 'unknown'} · ID: {s.sessionId}</p>
                        </div>
                        <div className={cn('flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium',
                            (s.activeUsers ?? 0) > 0 ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-700/40 text-slate-500'
                        )}>
                            <Users className="w-3 h-3" aria-hidden="true" />
                            {s.activeUsers ?? 0}/{s.maxUsers ?? '?'}
                        </div>
                    </div>
                ))}
                {data?.length === 0 && (
                    <p className="text-sm text-slate-600 text-center py-8">No sessions found</p>
                )}
            </div>
        </div>
    );
}
