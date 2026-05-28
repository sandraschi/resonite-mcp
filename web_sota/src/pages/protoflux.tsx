import {
    Cpu,
    CheckCircle2,
    AlertTriangle,
    Copy,
    ChevronRight,
    Zap,
    Link2,
    RefreshCw,
    Radio,
} from 'lucide-react';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiUrl } from '@/lib/api-base';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface RLStatus {
    connected: boolean;
    uri: string;
    session_info: Record<string, unknown>;
}

interface ConnectForm {
    host: string;
    port: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function CopyButton({ text }: { text: string }) {
    const [copied, setCopied] = useState(false);
    return (
        <button
            onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
            className="ml-2 text-slate-500 hover:text-indigo-400 transition-colors"
            title="Copy"
        >
            {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
    );
}

function CodeBlock({ code, lang = '' }: { code: string; lang?: string }) {
    return (
        <div className="relative group">
            <pre className={`bg-black/40 border border-white/[0.06] rounded-xl p-4 text-xs font-mono text-slate-300 overflow-x-auto leading-relaxed language-${lang}`}>
                {code}
            </pre>
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <CopyButton text={code} />
            </div>
        </div>
    );
}

function Step({ n, title, children }: { n: number; title: string; children: React.ReactNode }) {
    return (
        <div className="flex gap-4">
            <div className="flex-shrink-0 w-7 h-7 rounded-full bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-xs font-bold text-indigo-300 mt-0.5">
                {n}
            </div>
            <div className="flex-1 space-y-2">
                <p className="font-semibold text-white text-sm">{title}</p>
                <div className="text-xs text-slate-400 leading-relaxed space-y-2">{children}</div>
            </div>
        </div>
    );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export function ProtoFluxPage() {
    const qc = useQueryClient();
    const [form, setForm] = useState<ConnectForm>({ host: 'localhost', port: 4242 });
    const [activeTab, setActiveTab] = useState<'guide' | 'control'>('guide');

    // ResoniteLink status
    const { data: rlStatus, isLoading: rlLoading } = useQuery<RLStatus>({
        queryKey: ['rl-status'],
        queryFn: () => fetch(apiUrl('/rl/status')).then(r => r.json()),
        refetchInterval: 5000,
    });

    // Connect mutation
    const connectMut = useMutation({
        mutationFn: (f: ConnectForm) =>
            fetch(apiUrl('/rl/connect'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ host: f.host, port: f.port }) }).then(r => r.json()),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['rl-status'] }),
    });

    // Disconnect mutation
    const disconnectMut = useMutation({
        mutationFn: () => fetch(apiUrl('/rl/disconnect'), { method: 'POST' }).then(r => r.json()),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['rl-status'] }),
    });

    const isConnected = rlStatus?.connected ?? false;

    return (
        <div className="space-y-6 page-enter">

            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Cpu className="w-6 h-6 text-indigo-400" />
                    <div>
                        <h2 className="text-xl font-bold text-white">ProtoFlux & ResoniteLink</h2>
                        <p className="text-sm text-slate-500">In-world setup guide + live data model control</p>
                    </div>
                </div>
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${isConnected
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    : 'bg-slate-500/10 border-slate-500/30 text-slate-400'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
                    {rlLoading ? 'Checking...' : isConnected ? `Connected · ${rlStatus?.uri}` : 'Not connected'}
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 bg-white/[0.03] rounded-xl p-1 border border-white/[0.06] w-fit">
                {(['guide', 'control'] as const).map(t => (
                    <button
                        key={t}
                        onClick={() => setActiveTab(t)}
                        className={`px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${activeTab === t
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                            : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        {t === 'guide' ? 'Setup Guide' : 'Live Control'}
                    </button>
                ))}
            </div>

            {/* ---------------------------------------------------------------- */}
            {/* GUIDE TAB                                                        */}
            {/* ---------------------------------------------------------------- */}
            {activeTab === 'guide' && (
                <div className="space-y-6">

                    {/* Overview card */}
                    <div className="glass-card p-5 space-y-3">
                        <div className="flex items-center gap-2 text-indigo-400">
                            <Zap className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wider">How it works</span>
                        </div>
                        <p className="text-sm text-slate-400 leading-relaxed">
                            ResoniteLink is Resonite's official WebSocket data-model bridge (v0.8.3, Feb 2026).
                            It lets external tools read and write any field in the world scene graph by <span className="text-white font-medium">ref ID</span>.
                            ProtoFlux logix nodes expose gameplay logic that you can trigger from outside.
                            This MCP server bridges HTTP → ResoniteLink so your AI tools, scripts, and dashboards
                            can control what happens inside the world.
                        </p>
                        <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2">
                            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                            ResoniteLink must be enabled per-world by the host. Only the host (or Admin) can enable it.
                        </div>
                    </div>

                    {/* Part 1 – Enable ResoniteLink */}
                    <div className="glass-card p-6 space-y-5">
                        <h3 className="font-bold text-white flex items-center gap-2">
                            <Radio className="w-4 h-4 text-indigo-400" />
                            Part 1 — Enable ResoniteLink in your world
                        </h3>
                        <div className="space-y-5">
                            <Step n={1} title="Open the Sessions panel">
                                <p>Open your Resonite dash → <span className="text-white">Sessions</span> tab.
                                    Find your world in the list (or the world you're currently hosting).</p>
                            </Step>
                            <Step n={2} title='Click "Enable ResoniteLink"'>
                                <p>On the world entry, click the <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">Enable ResoniteLink</span> button.
                                    The default port is <span className="text-white">4242</span>.
                                    You can override it in the world's session settings.</p>
                                <p className="text-slate-500">Headless alternative — add to your headless Config.json:</p>
                                <CodeBlock lang="json" code={`"enableResoniteLink": true,\n"forceResoniteLinkPort": 4242`} />
                            </Step>
                            <Step n={3} title="Set permissions">
                                <p>From v0.8.x, you can also add a <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">ResoniteLinkPermissions</span> component
                                    to your world root slot to control who can read/write. Defaults to host/admin only.</p>
                            </Step>
                        </div>
                    </div>

                    {/* Part 2 – ProtoFlux nodes */}
                    <div className="glass-card p-6 space-y-5">
                        <h3 className="font-bold text-white flex items-center gap-2">
                            <Cpu className="w-4 h-4 text-indigo-400" />
                            Part 2 — Build ProtoFlux control nodes in the world
                        </h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            ResoniteLink writes to fields by <em>ref ID</em>. The easiest way to expose a controllable
                            parameter is to attach a <span className="text-white font-mono text-[11px]">DynamicValueVariable&lt;T&gt;</span> component
                            and wire it into your ProtoFlux graph. Then read the ref ID via the inspector and paste it here.
                        </p>

                        <div className="space-y-5">
                            <Step n={1} title="Create a control slot">
                                <p>In your world, press <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">Create New → Empty Slot</span>.
                                    Name it something like <span className="text-white">_MCPControls</span>.</p>
                            </Step>

                            <Step n={2} title="Add a DynamicValueVariable for each parameter">
                                <p>Attach a <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">DynamicValueVariable&lt;float3&gt;</span>
                                    (for position/scale) or <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">DynamicValueVariable&lt;bool&gt;</span>
                                    (for toggles) to that slot.</p>
                                <p>Give each a unique <span className="text-white">VariableName</span>, e.g. <span className="text-white font-mono text-[11px]">MCP/TeleportTarget</span>.</p>
                            </Step>

                            <Step n={3} title="Wire into ProtoFlux">
                                <p>In your ProtoFlux graph, use a <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">Read DynamicVariable</span> node
                                    pointing at your variable name. Connect its output to whatever you want to control —
                                    teleport target, animation speed, colour, etc.</p>
                                <p>For triggerable actions, use <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">DynamicImpulseReceiver</span>
                                    and trigger it by writing a bool field to true.</p>
                            </Step>

                            <Step n={4} title="Find the ref ID">
                                <p>Open the Inspector on your DynamicValueVariable component.
                                    The <span className="text-white">ID</span> shown at the top of the inspector panel is the <strong>ref ID</strong>
                                    you'll use in ResoniteLink write calls.</p>
                                <p>It looks like: <span className="text-white font-mono text-[11px] bg-white/10 px-1.5 py-0.5 rounded">ID:UUID-xxxx-xxxx</span></p>
                            </Step>

                            <Step n={5} title="Test a write from the Live Control tab">
                                <p>Connect to ResoniteLink below, then switch to the <span className="text-white">Live Control</span> tab.
                                    Paste the ref ID and write a value — you should see the effect in-world immediately.</p>
                            </Step>
                        </div>
                    </div>

                    {/* Part 3 – Teleport example */}
                    <div className="glass-card p-6 space-y-4">
                        <h3 className="font-bold text-white flex items-center gap-2">
                            <ChevronRight className="w-4 h-4 text-indigo-400" />
                            Example — Avatar Teleport via ProtoFlux
                        </h3>
                        <p className="text-xs text-slate-400">
                            Complete ProtoFlux setup to allow external teleport writes via ResoniteLink:
                        </p>
                        <CodeBlock lang="text" code={`World slot layout:
  _MCPControls
    └─ DynamicValueVariable<float3>   VariableName = "MCP/TeleportTarget"
    └─ DynamicValueVariable<bool>     VariableName = "MCP/TeleportTrigger"

ProtoFlux graph (attach to any slot):
  [Read DynamicVariable "MCP/TeleportTrigger"] → [On True] ──►
    [Read DynamicVariable "MCP/TeleportTarget"] ──► [Set User Root Position]

To fire from MCP HTTP API:
  POST /rl/field   { "ref_id": "<DV bool ref ID>", "value": true }
  POST /rl/field   { "ref_id": "<DV float3 ref ID>", "value": {"x":0,"y":1,"z":5} }`} />
                    </div>

                </div>
            )}

            {/* ---------------------------------------------------------------- */}
            {/* LIVE CONTROL TAB                                                 */}
            {/* ---------------------------------------------------------------- */}
            {activeTab === 'control' && (
                <div className="space-y-5">

                    {/* Connect panel */}
                    <div className="glass-card p-5 space-y-4">
                        <div className="flex items-center gap-2 text-indigo-400 mb-1">
                            <Link2 className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wider">ResoniteLink Connection</span>
                        </div>

                        <div className="flex gap-3 items-end flex-wrap">
                            <div className="space-y-1">
                                <label className="text-[10px] text-slate-500 uppercase tracking-wider">Host</label>
                                <input
                                    value={form.host}
                                    onChange={e => setForm(f => ({ ...f, host: e.target.value }))}
                                    className="bg-black/20 border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50 w-36"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-[10px] text-slate-500 uppercase tracking-wider">Port</label>
                                <input
                                    type="number"
                                    value={form.port}
                                    onChange={e => setForm(f => ({ ...f, port: Number(e.target.value) }))}
                                    className="bg-black/20 border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50 w-24"
                                />
                            </div>
                            {!isConnected ? (
                                <button
                                    onClick={() => connectMut.mutate(form)}
                                    disabled={connectMut.isPending}
                                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {connectMut.isPending ? 'Connecting...' : 'Connect'}
                                </button>
                            ) : (
                                <button
                                    onClick={() => disconnectMut.mutate()}
                                    disabled={disconnectMut.isPending}
                                    className="px-4 py-2 bg-rose-600/80 hover:bg-rose-500 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-50"
                                >
                                    Disconnect
                                </button>
                            )}
                            <button
                                onClick={() => qc.invalidateQueries({ queryKey: ['rl-status'] })}
                                className="p-2 text-slate-500 hover:text-indigo-400 transition-colors"
                                title="Refresh status"
                            >
                                <RefreshCw className="w-4 h-4" />
                            </button>
                        </div>

                        {connectMut.isError && (
                            <p className="text-xs text-rose-400">Connection failed. Is Resonite running with ResoniteLink enabled?</p>
                        )}
                        {connectMut.isSuccess && !isConnected && (
                            <p className="text-xs text-rose-400">Got a response but status shows disconnected — check server logs.</p>
                        )}

                        {isConnected && rlStatus?.session_info && Object.keys(rlStatus.session_info).length > 0 && (
                            <div className="bg-black/20 rounded-lg p-3 text-xs font-mono text-slate-400">
                                <p className="text-slate-500 text-[10px] uppercase tracking-wider mb-1">Session info</p>
                                <pre>{JSON.stringify(rlStatus.session_info, null, 2)}</pre>
                            </div>
                        )}
                    </div>

                    {/* Read/Write panel */}
                    {isConnected && <FieldPanel />}

                    {/* Reflection panel */}
                    {isConnected && <ReflectPanel />}

                    {!isConnected && (
                        <div className="glass-card p-10 text-center space-y-2">
                            <Cpu className="w-10 h-10 text-slate-700 mx-auto" />
                            <p className="text-slate-500 font-medium">Connect to ResoniteLink to access live controls</p>
                            <p className="text-xs text-slate-600">Resonite must be running and ResoniteLink enabled in the world</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// ---------------------------------------------------------------------------
// Sub-components for Live Control tab
// ---------------------------------------------------------------------------

function FieldPanel() {
    const [refId, setRefId] = useState('');
    const [writeValue, setWriteValue] = useState('');
    const [readResult, setReadResult] = useState<unknown>(null);
    const [readError, setReadError] = useState('');

    const readMut = useMutation({
        mutationFn: async (id: string) => {
            const r = await fetch(apiUrl(`/rl/field/${encodeURIComponent(id)}`));
            if (!r.ok) throw new Error(await r.text());
            return r.json();
        },
        onSuccess: d => { setReadResult(d.value); setReadError(''); },
        onError: (e: Error) => { setReadError(e.message); setReadResult(null); },
    });

    const writeMut = useMutation({
        mutationFn: async ({ id, value }: { id: string; value: string }) => {
            let parsed: unknown = value;
            try { parsed = JSON.parse(value); } catch { /* keep as string */ }
            const r = await fetch(apiUrl('/rl/field'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ref_id: id, value: parsed }),
            });
            if (!r.ok) throw new Error(await r.text());
            return r.json();
        },
    });

    return (
        <div className="glass-card p-5 space-y-4">
            <div className="flex items-center gap-2 text-amber-400">
                <Zap className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-wider">Field Read / Write</span>
            </div>

            <div className="space-y-1">
                <label className="text-[10px] text-slate-500 uppercase tracking-wider">Ref ID</label>
                <input
                    placeholder="ID:xxxx-xxxx-xxxx"
                    value={refId}
                    onChange={e => setRefId(e.target.value)}
                    className="bg-black/20 border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-indigo-500/50 w-full"
                />
            </div>

            <div className="flex gap-3 flex-wrap">
                <button
                    onClick={() => readMut.mutate(refId)}
                    disabled={!refId || readMut.isPending}
                    className="px-4 py-2 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] text-sm text-white rounded-lg transition-colors disabled:opacity-40"
                >
                    {readMut.isPending ? 'Reading...' : 'Read Field'}
                </button>
            </div>

            {readError && <p className="text-xs text-rose-400 font-mono">{readError}</p>}
            {readResult !== null && (
                <div className="bg-black/30 rounded-lg p-3 text-xs font-mono text-emerald-300">
                    {JSON.stringify(readResult, null, 2)}
                </div>
            )}

            <div className="border-t border-white/[0.05] pt-4 space-y-3">
                <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase tracking-wider">Value (JSON or string)</label>
                    <input
                        placeholder='e.g. true  or  {"x":0,"y":1,"z":5}  or  42.0'
                        value={writeValue}
                        onChange={e => setWriteValue(e.target.value)}
                        className="bg-black/20 border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-indigo-500/50 w-full"
                    />
                </div>
                <button
                    onClick={() => writeMut.mutate({ id: refId, value: writeValue })}
                    disabled={!refId || !writeValue || writeMut.isPending}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-40"
                >
                    {writeMut.isPending ? 'Writing...' : 'Write Field'}
                </button>
                {writeMut.isSuccess && <p className="text-xs text-emerald-400">Write OK</p>}
                {writeMut.isError && <p className="text-xs text-rose-400">{(writeMut.error as Error).message}</p>}
            </div>
        </div>
    );
}

function ReflectPanel() {
    const [componentType, setComponentType] = useState('');
    const [result, setResult] = useState<unknown>(null);
    const [err, setErr] = useState('');

    const reflectMut = useMutation({
        mutationFn: async () => {
            const r = await fetch(apiUrl('/rl/reflect'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ component_type: componentType || null }),
            });
            if (!r.ok) throw new Error(await r.text());
            return r.json();
        },
        onSuccess: d => { setResult(d); setErr(''); },
        onError: (e: Error) => { setErr(e.message); setResult(null); },
    });

    return (
        <div className="glass-card p-5 space-y-4">
            <div className="flex items-center gap-2 text-purple-400">
                <Cpu className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-wider">Reflection API (v0.8.3+)</span>
            </div>
            <p className="text-xs text-slate-500">Leave type blank to list all supported components. Enter a type to list its fields.</p>
            <div className="flex gap-3 items-end flex-wrap">
                <div className="flex-1 space-y-1 min-w-48">
                    <label className="text-[10px] text-slate-500 uppercase tracking-wider">Component Type (optional)</label>
                    <input
                        placeholder="e.g. FrooxEngine.AudioStreamController"
                        value={componentType}
                        onChange={e => setComponentType(e.target.value)}
                        className="bg-black/20 border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-indigo-500/50 w-full"
                    />
                </div>
                <button
                    onClick={() => reflectMut.mutate()}
                    disabled={reflectMut.isPending}
                    className="px-4 py-2 bg-purple-600/80 hover:bg-purple-500 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-40"
                >
                    {reflectMut.isPending ? 'Querying...' : 'Reflect'}
                </button>
            </div>
            {err && <p className="text-xs text-rose-400 font-mono">{err}</p>}
            {result !== null && (
                <div className="bg-black/30 rounded-lg p-3 text-xs font-mono text-slate-300 max-h-64 overflow-y-auto">
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}
