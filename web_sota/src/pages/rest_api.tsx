import { Cloud, Search, Globe2, Shield, Info, ExternalLink, RefreshCw, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';


interface ResoniteSession {
    sessionId?: string;
    name?: string;
    activeUsers?: number;
    maxUsers?: number;
    hostUsername?: string;
    universeId?: string;
}

export function RestApiPage() {
    const [searchQuery, setSearchQuery] = useState('');

    const { data: platformData } = useQuery({
        queryKey: ['platform'],
        queryFn: async () => {
            const r = await fetch('/api/platform');
            return r.json();
        }
    });

    const { data: sessionData, isLoading: sessLoading, refetch: refetchSessions } = useQuery({
        queryKey: ['sessions'],
        queryFn: async () => {
            const r = await fetch('/api/sessions');
            return r.json();
        }
    });

    const filteredSessions = sessionData?.filter((s: ResoniteSession) =>
    (s.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.hostUsername?.toLowerCase().includes(searchQuery.toLowerCase()))
    ) || [];

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Cloud className="w-6 h-6 text-indigo-400" />
                    <div>
                        <h2 className="text-xl font-bold text-white">Resonite Cloud API</h2>
                        <p className="text-sm text-slate-500">Query platform metadata and live session registry</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-card p-4 space-y-2">
                    <div className="flex items-center gap-2 text-indigo-400 mb-1">
                        <Info className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">Platform</span>
                    </div>
                    <p className="text-xs text-slate-400">Version: <span className="text-white">{platformData?.version || 'N/A'}</span></p>
                    <p className="text-xs text-slate-400">Build: <span className="text-white font-mono">{platformData?.build || 'N/A'}</span></p>
                </div>
                <div className="glass-card p-4 space-y-2">
                    <div className="flex items-center gap-2 text-emerald-400 mb-1">
                        <Shield className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">Core Auth</span>
                    </div>
                    <p className="text-xs text-slate-400">Authenticated: <span className="text-emerald-400">Yes</span></p>
                    <p className="text-xs text-slate-500 italic">Connected via local Resonite session</p>
                </div>
                <div className="glass-card p-4 space-y-2">
                    <div className="flex items-center gap-2 text-purple-400 mb-1">
                        <Globe2 className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">Registry</span>
                    </div>
                    <p className="text-xs text-slate-400">Total sessions: <span className="text-white">{sessionData?.length || 0}</span></p>
                    <button onClick={() => refetchSessions()} className="text-[10px] text-indigo-400 hover:underline flex items-center gap-1">
                        <RefreshCw className="w-2.5 h-2.5" />
                        Sync now
                    </button>
                </div>
            </div>

            <div className="glass-card p-6 space-y-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <h3 className="font-bold text-white">Live Session Explorer</h3>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Search sessions or hosts..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="bg-black/20 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50 transition-all w-full md:w-64"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead>
                            <tr className="border-b border-white/[0.05]">
                                <th className="pb-3 text-slate-500 font-semibold px-2">Session Name</th>
                                <th className="pb-3 text-slate-500 font-semibold px-2">Host</th>
                                <th className="pb-3 text-slate-500 font-semibold px-2">Users</th>
                                <th className="pb-3 text-slate-500 font-semibold px-2 text-right">Universe</th>
                                <th className="pb-3 text-slate-500 font-semibold px-2"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.02]">
                            {sessLoading ? (
                                <tr><td colSpan={5} className="py-8 text-center text-slate-600">Loading sessions...</td></tr>
                            ) : filteredSessions.slice(0, 20).map((session: ResoniteSession) => (
                                <tr key={session.sessionId} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="py-3 px-2 font-medium text-slate-200">{session.name}</td>
                                    <td className="py-3 px-2 text-slate-400">{session.hostUsername}</td>
                                    <td className="py-3 px-2">
                                        <span className="bg-white/[0.05] border border-white/[0.08] px-2 py-0.5 rounded text-[10px] text-slate-300">
                                            {session.activeUsers} / {session.maxUsers}
                                        </span>
                                    </td>
                                    <td className="py-3 px-2 text-right text-slate-600 font-mono text-[10px]">{session.universeId?.split('-')[0]}...</td>
                                    <td className="py-3 px-2 text-right">
                                        <button title="View external link" className="p-1.5 opacity-0 group-hover:opacity-100 transition-opacity text-indigo-400 hover:text-indigo-300">
                                            <ExternalLink className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {!sessLoading && filteredSessions.length === 0 && (
                        <div className="py-12 text-center space-y-2">
                            <AlertCircle className="w-8 h-8 text-slate-800 mx-auto" />
                            <p className="text-slate-600 font-medium">No sessions matching your query</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
