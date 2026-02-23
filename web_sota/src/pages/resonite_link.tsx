import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cn } from '../common/utils';
import {
    Link2, Wifi, WifiOff, RefreshCw, Search,
    ChevronRight, ChevronDown, Send, Eye, Loader2, AlertTriangle, CheckCircle2
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

// ---- API helpers -------------------------------------------------------

async function fetchRLStatus() {
    const r = await fetch('/rl/status');
    if (!r.ok) throw new Error('status fetch failed');
    return r.json() as Promise<{ connected: boolean; uri: string; session_info: Record<string, unknown> | null }>;
}

async function connectRL(host: string, port: number) {
    const r = await fetch('/rl/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ host, port }),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
}

async function disconnectRL() {
    const r = await fetch('/rl/disconnect', { method: 'POST' });
    if (!r.ok) throw new Error('disconnect failed');
    return r.json();
}

async function readField(refId: string) {
    const r = await fetch(`/rl/field/${encodeURIComponent(refId)}`);
    if (!r.ok) throw new Error(await r.text());
    return r.json() as Promise<{ ref_id: string; value: unknown }>;
}

async function getChildren(slotId: string) {
    const r = await fetch(`/rl/children/${encodeURIComponent(slotId)}`);
    if (!r.ok) throw new Error(await r.text());
    return r.json() as Promise<{ slot_id: string; children: unknown[] }>;
}

async function reflectTypes(componentType?: string) {
    const r = await fetch('/rl/reflect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ component_type: componentType || null }),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
}

// ---- Components --------------------------------------------------------

function StatusBadge({ connected }: { connected: boolean }) {
    return (
        <span className={cn(
            'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest border',
            connected
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'bg-red-500/10 border-red-500/30 text-red-400'
        )}>
            <span className={cn('h-1.5 w-1.5 rounded-full', connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400')} />
            {connected ? 'Connected' : 'Disconnected'}
        </span>
    );
}

function JsonViewer({ data }: { data: unknown }) {
    const text = JSON.stringify(data, null, 2);
    return (
        <pre className="text-[10px] font-mono text-slate-300 whitespace-pre-wrap break-all bg-black/30 rounded-lg p-3 border border-white/5 max-h-40 overflow-y-auto scrollbar-thin">
            {text}
        </pre>
    );
}

// ---- Page --------------------------------------------------------------

export function ResoniteLinkPage() {
    const qc = useQueryClient();

    // Connection form state
    const [host, setHost] = useState('localhost');
    const [port, setPort] = useState('37166');

    // Field reader
    const [fieldRef, setFieldRef] = useState('');
    const [fieldResult, setFieldResult] = useState<unknown>(null);
    const [fieldError, setFieldError] = useState('');

    // Children fetcher
    const [slotRef, setSlotRef] = useState('');
    const [childrenResult, setChildrenResult] = useState<unknown>(null);
    const [childrenError, setChildrenError] = useState('');

    // Reflect
    const [reflectType, setReflectType] = useState('');
    const [reflectResult, setReflectResult] = useState<unknown>(null);
    const [reflectError, setReflectError] = useState('');

    const { data: status, isLoading: statusLoading, refetch: refetchStatus } = useQuery({
        queryKey: ['rl-status'],
        queryFn: fetchRLStatus,
        refetchInterval: 5000,
        retry: false,
    });

    const connectMutation = useMutation({
        mutationFn: () => connectRL(host, parseInt(port, 10)),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['rl-status'] }),
    });

    const disconnectMutation = useMutation({
        mutationFn: disconnectRL,
        onSuccess: () => qc.invalidateQueries({ queryKey: ['rl-status'] }),
    });

    const connected = status?.connected ?? false;

    const handleReadField = async () => {
        setFieldError(''); setFieldResult(null);
        try { setFieldResult(await readField(fieldRef)); }
        catch (e) { setFieldError((e as Error).message); }
    };

    const handleGetChildren = async () => {
        setChildrenError(''); setChildrenResult(null);
        try { setChildrenResult(await getChildren(slotRef || (status?.session_info as Record<string, string> | null)?.root_slot_id || '')); }
        catch (e) { setChildrenError((e as Error).message); }
    };

    const handleReflect = async () => {
        setReflectError(''); setReflectResult(null);
        try { setReflectResult(await reflectTypes(reflectType || undefined)); }
        catch (e) { setReflectError((e as Error).message); }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">

            {/* Header */}
            <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000" />
                <div className="relative flex flex-col md:flex-row md:items-end justify-between gap-6 bg-card/40 backdrop-blur-xl border border-white/10 p-6 rounded-xl glass-card">
                    <div className="flex items-center gap-5">
                        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl shadow-inner group-hover:scale-110 transition-transform duration-500">
                            <Link2 className="w-8 h-8 text-emerald-400" />
                        </div>
                        <div>
                            <h2 className="text-3xl font-black tracking-tighter text-foreground">
                                Resonite<span className="text-emerald-400">Link</span>
                            </h2>
                            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1 opacity-70 flex items-center gap-2">
                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                WebSocket Data Model Bridge · Protocol v0.8.3
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        {statusLoading
                            ? <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                            : <StatusBadge connected={connected} />}
                        <button
                            onClick={() => refetchStatus()}
                            title="Refresh status"
                            className="p-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-muted-foreground hover:text-foreground transition-all"
                        >
                            <RefreshCw className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Connect / Disconnect Panel */}
            <div className="grid md:grid-cols-2 gap-6">
                <Card className="border-white/10 bg-card/30 backdrop-blur-md glass">
                    <CardContent className="p-5 space-y-4">
                        <p className="text-xs font-bold text-foreground uppercase tracking-widest">Connection</p>
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label htmlFor="rl-host" className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider block mb-1">Host</label>
                                <input
                                    id="rl-host"
                                    value={host}
                                    onChange={e => setHost(e.target.value)}
                                    placeholder="localhost"
                                    title="ResoniteLink host"
                                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono focus:border-emerald-500/50 focus:outline-none transition-colors"
                                />
                            </div>
                            <div>
                                <label htmlFor="rl-port" className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider block mb-1">Port</label>
                                <input
                                    id="rl-port"
                                    value={port}
                                    onChange={e => setPort(e.target.value)}
                                    placeholder="37166"
                                    title="ResoniteLink port"
                                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono focus:border-emerald-500/50 focus:outline-none transition-colors"
                                />
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => connectMutation.mutate()}
                                disabled={connectMutation.isPending || connected}
                                className={cn(
                                    "flex-1 flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border active:scale-95",
                                    connected
                                        ? 'bg-white/5 border-white/10 text-muted-foreground cursor-not-allowed'
                                        : 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/30'
                                )}
                            >
                                {connectMutation.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Wifi className="w-3.5 h-3.5" />}
                                Connect
                            </button>
                            <button
                                onClick={() => disconnectMutation.mutate()}
                                disabled={disconnectMutation.isPending || !connected}
                                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/20 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                                {disconnectMutation.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <WifiOff className="w-3.5 h-3.5" />}
                                Disconnect
                            </button>
                        </div>

                        {connectMutation.isError && (
                            <div className="flex items-center gap-2 text-red-400 text-[11px] bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                                <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                                {(connectMutation.error as Error).message}
                            </div>
                        )}
                        {connectMutation.isSuccess && (
                            <div className="flex items-center gap-2 text-emerald-400 text-[11px] bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3 py-2">
                                <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                                Connected — handshake complete
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Session Info */}
                <Card className="border-white/10 bg-card/30 backdrop-blur-md glass">
                    <CardContent className="p-5 space-y-3">
                        <p className="text-xs font-bold text-foreground uppercase tracking-widest">Session Info</p>
                        {status?.session_info
                            ? <JsonViewer data={status.session_info} />
                            : <p className="text-[11px] text-muted-foreground italic">No session info — connect first.</p>
                        }
                    </CardContent>
                </Card>
            </div>

            {/* Field Reader & Node Inspector */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Read Field */}
                <Card className="border-white/10 bg-card/30 backdrop-blur-md glass">
                    <CardContent className="p-5 space-y-3">
                        <div className="flex items-center gap-2">
                            <Eye className="w-4 h-4 text-indigo-400" />
                            <p className="text-xs font-bold text-foreground uppercase tracking-widest">Read Field</p>
                        </div>
                        <input
                            value={fieldRef}
                            onChange={e => setFieldRef(e.target.value)}
                            placeholder="Ref ID (e.g. U-1234:abc)"
                            title="Field ref ID"
                            className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono focus:border-indigo-500/50 focus:outline-none transition-colors"
                        />
                        <button
                            onClick={handleReadField}
                            disabled={!connected || !fieldRef}
                            className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-bold uppercase tracking-wider border bg-indigo-500/20 border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/30 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <Send className="w-3.5 h-3.5" /> Fetch
                        </button>
                        {fieldError && <p className="text-[10px] text-red-400">{fieldError}</p>}
                        {fieldResult !== null && <JsonViewer data={fieldResult} />}
                    </CardContent>
                </Card>

                {/* Children Inspector */}
                <Card className="border-white/10 bg-card/30 backdrop-blur-md glass">
                    <CardContent className="p-5 space-y-3">
                        <div className="flex items-center gap-2">
                            <ChevronDown className="w-4 h-4 text-purple-400" />
                            <p className="text-xs font-bold text-foreground uppercase tracking-widest">Children Of Slot</p>
                        </div>
                        <input
                            value={slotRef}
                            onChange={e => setSlotRef(e.target.value)}
                            placeholder="Slot ID (blank = root from session)"
                            title="Slot ref ID"
                            className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono focus:border-purple-500/50 focus:outline-none transition-colors"
                        />
                        <button
                            onClick={handleGetChildren}
                            disabled={!connected}
                            className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-bold uppercase tracking-wider border bg-purple-500/20 border-purple-500/30 text-purple-400 hover:bg-purple-500/30 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <ChevronRight className="w-3.5 h-3.5" /> Inspect
                        </button>
                        {childrenError && <p className="text-[10px] text-red-400">{childrenError}</p>}
                        {childrenResult !== null && <JsonViewer data={childrenResult} />}
                    </CardContent>
                </Card>
            </div>

            {/* Reflect */}
            <Card className="border-white/10 bg-card/30 backdrop-blur-md glass">
                <CardContent className="p-5 space-y-3">
                    <div className="flex items-center gap-2">
                        <Search className="w-4 h-4 text-amber-400" />
                        <p className="text-xs font-bold text-foreground uppercase tracking-widest">Reflect — Component Type Discovery</p>
                    </div>
                    <div className="flex gap-3">
                        <input
                            value={reflectType}
                            onChange={e => setReflectType(e.target.value)}
                            placeholder="C# type (blank = list all supported types)"
                            title="Component type for reflection"
                            className="flex-1 bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono focus:border-amber-500/50 focus:outline-none transition-colors"
                        />
                        <button
                            onClick={handleReflect}
                            disabled={!connected}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider border bg-amber-500/20 border-amber-500/30 text-amber-400 hover:bg-amber-500/30 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <Search className="w-3.5 h-3.5" /> Reflect
                        </button>
                    </div>
                    {reflectError && <p className="text-[10px] text-red-400">{reflectError}</p>}
                    {reflectResult !== null && <JsonViewer data={reflectResult} />}
                </CardContent>
            </Card>

            {/* Quick Reference */}
            <Card className="border-white/10 bg-card/20 backdrop-blur-sm">
                <CardContent className="p-5 space-y-2">
                    <p className="text-xs font-bold text-foreground uppercase tracking-widest opacity-70">HTTP API Quick Reference</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {[
                            ['POST', '/rl/connect', 'Connect with {host, port}'],
                            ['POST', '/rl/disconnect', 'Graceful disconnect'],
                            ['GET', '/rl/status', 'Connection + session info'],
                            ['GET', '/rl/field/{ref_id}', 'Read field value'],
                            ['POST', '/rl/field', 'Write field value'],
                            ['GET', '/rl/node/{ref_id}', 'Get slot/component info'],
                            ['GET', '/rl/children/{slot_id}', 'List direct children'],
                            ['POST', '/rl/slot', 'Add child slot'],
                            ['POST', '/rl/component', 'Add component to slot'],
                            ['DELETE', '/rl/slot/{slot_id}', 'Destroy slot + children'],
                            ['POST', '/rl/batch', 'Batch multiple ops atomically'],
                            ['POST', '/rl/reflect', 'Discover component types'],
                        ].map(([method, path, desc]) => (
                            <div key={path} className="flex items-start gap-2 text-[10px] font-mono">
                                <span className={cn(
                                    'shrink-0 w-14 text-center rounded px-1 py-0.5 font-bold uppercase',
                                    method === 'GET' && 'bg-emerald-500/10 text-emerald-400',
                                    method === 'POST' && 'bg-indigo-500/10 text-indigo-400',
                                    method === 'DELETE' && 'bg-red-500/10 text-red-400',
                                )}>{method}</span>
                                <span className="text-slate-300">{path}</span>
                                <span className="text-muted-foreground ml-auto text-right hidden sm:block">{desc}</span>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
