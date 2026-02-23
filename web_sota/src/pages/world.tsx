import { useState, useCallback } from 'react';
import {
    TreePine, ChevronRight, ChevronDown, Box, Layers, Loader2,
    RefreshCw, AlertTriangle, Upload, FolderOpen, Crosshair,
    Armchair, Building2, Package, User
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cn } from '@/common/utils';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type AssetCategory = 'avatars' | 'props' | 'furniture' | 'architecture' | 'misc';

const CATEGORY_META: Record<AssetCategory, { label: string; icon: React.ReactNode; hint: string }> = {
    avatars: { label: 'Avatars', icon: <User className="w-3.5 h-3.5" />, hint: '~/.avatarmcp/models/' },
    props: { label: 'Props', icon: <Package className="w-3.5 h-3.5" />, hint: '~/Documents/ResoniteAssets/props/' },
    furniture: { label: 'Furniture', icon: <Armchair className="w-3.5 h-3.5" />, hint: '~/Documents/ResoniteAssets/furniture/' },
    architecture: { label: 'Architecture', icon: <Building2 className="w-3.5 h-3.5" />, hint: '~/Documents/ResoniteAssets/architecture/' },
    misc: { label: 'Misc', icon: <FolderOpen className="w-3.5 h-3.5" />, hint: '~/Documents/ResoniteAssets/misc/' },
};

interface AssetFile {
    name: string;
    filename: string;
    path: string;
    extension: string;
    size_bytes: number;
    relative: string;
    category: AssetCategory;
}

interface AssetListResponse {
    category: AssetCategory;
    scan_dir: string;
    files: AssetFile[];
    all_categories: AssetCategory[];
}

interface SlotChild {
    refId: string;
    name?: string;
    active?: boolean;
    type?: string;
}

interface SlotNode {
    refId?: string;
    name?: string;
    active?: boolean;
    position?: { x: number; y: number; z: number };
    rotation?: { x: number; y: number; z: number; w: number };
    scale?: { x: number; y: number; z: number };
    components?: { refId: string; componentType: string }[];
}

interface RLStatus {
    connected: boolean;
    uri: string;
    session_info: Record<string, unknown>;
}

// Depth levels map to Tailwind indent classes
const DEPTH_CLASSES = [
    'pl-2', 'pl-6', 'pl-10', 'pl-14', 'pl-18', 'pl-20', 'pl-24',
];
function depthClass(d: number) {
    return DEPTH_CLASSES[Math.min(d, DEPTH_CLASSES.length - 1)];
}

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function fetchRLStatus(): Promise<RLStatus> {
    const r = await fetch('/rl/status');
    if (!r.ok) throw new Error('Status check failed');
    return r.json() as Promise<RLStatus>;
}

async function fetchRootChildren(): Promise<{ slot_id: string; children: SlotChild[] }> {
    const r = await fetch('/rl/world/children/Root');
    if (!r.ok) throw new Error(await r.text());
    return r.json() as Promise<{ slot_id: string; children: SlotChild[] }>;
}

async function fetchChildren(refId: string): Promise<{ slot_id: string; children: SlotChild[] }> {
    const r = await fetch(`/rl/world/children/${refId}`);
    if (!r.ok) throw new Error(await r.text());
    return r.json() as Promise<{ slot_id: string; children: SlotChild[] }>;
}

async function fetchNode(refId: string): Promise<SlotNode> {
    const r = await fetch(`/rl/world/node/${refId}`);
    if (!r.ok) throw new Error(await r.text());
    return r.json() as Promise<SlotNode>;
}

async function fetchAssets(category: AssetCategory): Promise<AssetListResponse> {
    const r = await fetch(`/rl/world/asset-files?category=${category}`);
    if (!r.ok) throw new Error('Asset list failed');
    return r.json() as Promise<AssetListResponse>;
}

async function importAsset(payload: {
    file_path: string;
    target_slot: string;
    position: { x: number; y: number; z: number };
}) {
    const r = await fetch('/rl/world/import-vrm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
}

// ---------------------------------------------------------------------------
// SlotRow — expandable tree row (depth handled via CSS class map)
// ---------------------------------------------------------------------------

interface SlotRowProps {
    slot: SlotChild;
    depth: number;
    selected: string | null;
    onSelect: (refId: string) => void;
}

function SlotRow({ slot, depth, selected, onSelect }: SlotRowProps) {
    const [expanded, setExpanded] = useState(false);
    const [children, setChildren] = useState<SlotChild[] | null>(null);
    const [loading, setLoading] = useState(false);

    const toggle = useCallback(async () => {
        if (!expanded && children === null) {
            setLoading(true);
            try {
                const data = await fetchChildren(slot.refId);
                setChildren(data.children ?? []);
            } catch {
                setChildren([]);
            } finally {
                setLoading(false);
            }
        }
        setExpanded(e => !e);
    }, [expanded, children, slot.refId]);

    const isSelected = selected === slot.refId;

    return (
        <div>
            <button
                onClick={() => { onSelect(slot.refId); void toggle(); }}
                className={cn(
                    'w-full flex items-center gap-2 py-1.5 rounded-lg text-left text-sm transition-all',
                    depthClass(depth),
                    isSelected
                        ? 'bg-violet-500/20 border border-violet-500/30 text-violet-200'
                        : 'hover:bg-white/5 text-slate-300 border border-transparent',
                )}
                title={slot.refId}
            >
                <span className="flex-none text-slate-600 w-3">
                    {loading
                        ? <Loader2 className="w-3 h-3 animate-spin" />
                        : expanded
                            ? <ChevronDown className="w-3 h-3" />
                            : <ChevronRight className="w-3 h-3" />
                    }
                </span>
                <Box className="w-3.5 h-3.5 flex-none text-violet-400/60" aria-hidden="true" />
                <span className="truncate font-mono text-xs">{slot.name ?? slot.refId}</span>
                {slot.active === false && (
                    <span className="ml-auto mr-2 text-[9px] text-slate-600 font-bold uppercase tracking-widest">OFF</span>
                )}
            </button>

            {expanded && children && children.length > 0 && (
                <div>
                    {children.map(child => (
                        <SlotRow key={child.refId} slot={child} depth={depth + 1} selected={selected} onSelect={onSelect} />
                    ))}
                </div>
            )}
            {expanded && children && children.length === 0 && (
                <p className={cn('text-[10px] text-slate-700 py-1', depthClass(depth + 1))}>
                    (empty)
                </p>
            )}
        </div>
    );
}

// ---------------------------------------------------------------------------
// Inspector Panel
// ---------------------------------------------------------------------------

function Inspector({ refId }: { refId: string }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['rl-node', refId],
        queryFn: () => fetchNode(refId),
        enabled: !!refId,
    });

    if (isLoading) return (
        <div className="flex items-center justify-center h-40">
            <Loader2 className="w-6 h-6 animate-spin text-violet-400" />
        </div>
    );
    if (isError || !data) return (
        <div className="text-xs text-red-400 p-4">Failed to load node data.</div>
    );

    const fmt = (v: number) => v.toFixed(3);

    return (
        <div className="space-y-4 p-4 text-xs font-mono">
            <div className="space-y-1">
                <p className="text-[9px] font-bold uppercase tracking-widest text-slate-600">Slot</p>
                <p className="text-violet-300 truncate">{data.name ?? '(unnamed)'}</p>
                <p className="text-slate-600 text-[10px] break-all">{data.refId}</p>
                <span className={cn(
                    'inline-block px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest',
                    data.active !== false ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-700/40 text-slate-600'
                )}>
                    {data.active !== false ? 'Active' : 'Inactive'}
                </span>
            </div>

            {data.position && (
                <div className="space-y-1">
                    <p className="text-[9px] font-bold uppercase tracking-widest text-slate-600">Position</p>
                    <p className="text-slate-300">x: {fmt(data.position.x)} y: {fmt(data.position.y)} z: {fmt(data.position.z)}</p>
                </div>
            )}

            {data.scale && (
                <div className="space-y-1">
                    <p className="text-[9px] font-bold uppercase tracking-widest text-slate-600">Scale</p>
                    <p className="text-slate-300">x: {fmt(data.scale.x)} y: {fmt(data.scale.y)} z: {fmt(data.scale.z)}</p>
                </div>
            )}

            {data.components && data.components.length > 0 && (
                <div className="space-y-1">
                    <p className="text-[9px] font-bold uppercase tracking-widest text-slate-600">Components ({data.components.length})</p>
                    <div className="space-y-1 max-h-40 overflow-y-auto">
                        {data.components.map(c => (
                            <div key={c.refId} className="flex items-center gap-2 py-1 border-b border-white/5">
                                <Layers className="w-3 h-3 text-indigo-400 flex-none" aria-hidden="true" />
                                <span className="text-slate-300 truncate text-[10px]">{c.componentType.split('.').pop()}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

// ---------------------------------------------------------------------------
// AssetPanel — multi-category asset injector (avatars/props/furniture/arch/misc)
// ---------------------------------------------------------------------------

function AssetPanel({ targetSlot }: { targetSlot: string | null }) {
    const queryClient = useQueryClient();
    const [category, setCategory] = useState<AssetCategory>('avatars');
    const [selectedPath, setSelectedPath] = useState('');
    const [pos, setPos] = useState({ x: 0, y: 0, z: 0 });
    const [toast, setToast] = useState<{ ok: boolean; msg: string } | null>(null);

    const { data: assetData, isLoading: assetsLoading } = useQuery({
        queryKey: ['asset-files', category],
        queryFn: () => fetchAssets(category),
    });

    const mutation = useMutation({
        mutationFn: importAsset,
        onSuccess: () => {
            setToast({ ok: true, msg: 'Asset injected! Check Resonite.' });
            void queryClient.invalidateQueries({ queryKey: ['rl-children'] });
            setTimeout(() => setToast(null), 4000);
        },
        onError: (e: Error) => {
            setToast({ ok: false, msg: e.message });
            setTimeout(() => setToast(null), 6000);
        },
    });

    const handleInject = () => {
        if (!selectedPath) return;
        mutation.mutate({ file_path: selectedPath, target_slot: targetSlot ?? 'Root', position: pos });
    };

    // Clear selection when category changes
    const handleCategoryChange = (cat: AssetCategory) => {
        setCategory(cat);
        setSelectedPath('');
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2">
                <Upload className="w-4 h-4 text-violet-400 flex-none" aria-hidden="true" />
                <span className="text-xs font-bold text-slate-200 uppercase tracking-widest">Inject Asset</span>
            </div>

            {/* Category tabs */}
            <div className="flex flex-wrap gap-1">
                {(Object.keys(CATEGORY_META) as AssetCategory[]).map(cat => (
                    <button
                        key={cat}
                        onClick={() => handleCategoryChange(cat)}
                        title={`Browse ${CATEGORY_META[cat].label}`}
                        className={cn(
                            'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all border',
                            category === cat
                                ? 'bg-violet-500/20 border-violet-500/30 text-violet-300'
                                : 'bg-white/5 border-white/5 text-slate-500 hover:text-slate-300 hover:border-white/10'
                        )}
                    >
                        {CATEGORY_META[cat].icon}
                        {CATEGORY_META[cat].label}
                    </button>
                ))}
            </div>

            {/* File picker */}
            <div className="space-y-1.5">
                <p className="text-[9px] text-slate-600 font-bold uppercase tracking-widest">
                    {CATEGORY_META[category].label} File
                    <span className="ml-1 text-slate-700 normal-case font-normal">({CATEGORY_META[category].hint})</span>
                </p>
                {assetsLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin text-violet-400" />
                ) : assetData && assetData.files.length > 0 ? (
                    <select
                        value={selectedPath}
                        onChange={e => setSelectedPath(e.target.value)}
                        title={`Select ${CATEGORY_META[category].label} file`}
                        className="w-full bg-card/40 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 outline-none focus:border-violet-500/50"
                    >
                        <option value="">— Select file —</option>
                        {assetData.files.map(f => (
                            <option key={f.path} value={f.path}>{f.relative} ({f.extension.toUpperCase()})</option>
                        ))}
                    </select>
                ) : (
                    <div className="flex items-center gap-2 text-xs text-slate-600 py-1">
                        <FolderOpen className="w-4 h-4" aria-hidden="true" />
                        <span>No 3D files found in <code className="text-slate-700">{assetData?.scan_dir ?? '…'}</code></span>
                    </div>
                )}
                {/* Manual path fallback */}
                <input
                    type="text"
                    value={selectedPath}
                    onChange={e => setSelectedPath(e.target.value)}
                    placeholder="…or paste absolute path to file"
                    title="Asset file path"
                    className="w-full bg-card/40 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono text-slate-400 placeholder:text-slate-700 outline-none focus:border-violet-500/50"
                />
            </div>

            {/* Spawn position */}
            <div className="space-y-1">
                <p className="text-[9px] text-slate-600 font-bold uppercase tracking-widest flex items-center gap-1">
                    <Crosshair className="w-3 h-3" aria-hidden="true" /> Spawn Position
                </p>
                <div className="grid grid-cols-3 gap-2">
                    {(['x', 'y', 'z'] as const).map(axis => (
                        <div key={axis} className="space-y-0.5">
                            <label htmlFor={`pos-${axis}`} className="text-[9px] text-slate-600 uppercase">{axis}</label>
                            <input
                                id={`pos-${axis}`}
                                type="number"
                                step="0.1"
                                value={pos[axis]}
                                onChange={e => setPos(p => ({ ...p, [axis]: parseFloat(e.target.value) || 0 }))}
                                title={`Position ${axis}`}
                                className="w-full bg-card/40 border border-white/10 rounded-lg px-2 py-1.5 text-xs font-mono text-slate-200 outline-none focus:border-violet-500/50"
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Target slot indicator */}
            {targetSlot && (
                <p className="text-[10px] text-slate-500">
                    Parent slot: <span className="text-violet-400 font-mono">{targetSlot}</span>
                </p>
            )}

            {/* Inject button */}
            <button
                onClick={handleInject}
                disabled={!selectedPath || mutation.isPending}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold uppercase tracking-widest transition-all shadow-lg shadow-violet-500/20 active:scale-95"
                title={`Inject ${CATEGORY_META[category].label} into Resonite world`}
            >
                {mutation.isPending
                    ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Injecting…</>
                    : <><Upload className="w-3.5 h-3.5" /> Inject {CATEGORY_META[category].label}</>
                }
            </button>

            {toast && (
                <div className={cn(
                    'p-3 rounded-lg text-xs font-bold',
                    toast.ok ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-red-500/10 text-red-400 border border-red-500/20'
                )}>
                    {toast.msg}
                </div>
            )}
        </div>
    );
}

// ---------------------------------------------------------------------------
// Main World page
// ---------------------------------------------------------------------------

export function World() {
    const [selectedRefId, setSelectedRefId] = useState<string | null>(null);
    const queryClient = useQueryClient();

    const { data: rlStatus, isLoading: statusLoading } = useQuery({
        queryKey: ['rl-status'],
        queryFn: fetchRLStatus,
        refetchInterval: 5000,
    });

    const { data: rootData, isLoading: rootLoading, isError: rootError, refetch: refetchRoot } = useQuery({
        queryKey: ['rl-children', 'Root'],
        queryFn: fetchRootChildren,
        enabled: rlStatus?.connected === true,
    });

    const connected = rlStatus?.connected ?? false;

    const handleRefresh = () => {
        void queryClient.invalidateQueries({ queryKey: ['rl-children'] });
        void queryClient.invalidateQueries({ queryKey: ['rl-node'] });
        void refetchRoot();
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-700">
            {/* Header */}
            <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-violet-500/20 to-purple-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000" />
                <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card/40 backdrop-blur-xl border border-white/10 p-6 rounded-xl glass-card">
                    <div className="flex items-center gap-5">
                        <div className="p-3 bg-violet-500/10 border border-violet-500/20 rounded-xl shadow-inner group-hover:rotate-12 transition-transform duration-500">
                            <TreePine className="w-8 h-8 text-violet-400" aria-hidden="true" />
                        </div>
                        <div>
                            <h2 className="text-3xl font-black tracking-tighter text-foreground bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/60">
                                World <span className="text-violet-400">Inspector</span>
                            </h2>
                            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1 opacity-70 flex items-center gap-2">
                                <span className={cn('h-1.5 w-1.5 rounded-full', connected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500')} />
                                {connected
                                    ? `ResoniteLink Connected — ${rlStatus?.uri ?? ''}`
                                    : 'ResoniteLink Disconnected'}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={handleRefresh}
                        disabled={!connected || rootLoading}
                        title="Refresh World Tree"
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/20 text-violet-300 text-xs font-bold uppercase tracking-widest transition-all disabled:opacity-40"
                    >
                        <RefreshCw className={cn('w-4 h-4', rootLoading && 'animate-spin')} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Not connected gate */}
            {!statusLoading && !connected && (
                <div className="glass-card p-12 flex flex-col items-center justify-center text-center gap-4 border-amber-500/20 bg-amber-500/5">
                    <div className="p-4 rounded-full bg-amber-500/10 border border-amber-500/20">
                        <AlertTriangle className="w-8 h-8 text-amber-400" aria-hidden="true" />
                    </div>
                    <div>
                        <p className="text-amber-300 font-bold">ResoniteLink Not Connected</p>
                        <p className="text-sm text-slate-500 mt-1">
                            Go to{' '}
                            <a href="/resonite-link" className="text-violet-400 hover:underline font-bold">ResoniteLink</a>
                            {' '}and connect first.
                        </p>
                    </div>
                </div>
            )}

            {/* Main grid: hierarchy tree + right panel */}
            {connected && (
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-4">
                    {/* Left: slot tree */}
                    <div className="glass-card border border-white/10 rounded-xl overflow-hidden">
                        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-card/20">
                            <div className="flex items-center gap-2">
                                <TreePine className="w-4 h-4 text-violet-400" aria-hidden="true" />
                                <span className="text-xs font-bold text-slate-200 uppercase tracking-widest">Scene Hierarchy</span>
                            </div>
                            <span className="text-[9px] font-mono text-slate-600">Root</span>
                        </div>

                        <div className="p-2 max-h-[60vh] overflow-y-auto space-y-0.5">
                            {rootLoading && (
                                <div className="flex items-center justify-center py-10">
                                    <Loader2 className="w-6 h-6 animate-spin text-violet-400" />
                                </div>
                            )}
                            {rootError && (
                                <div className="text-xs text-red-400 p-4 flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4" aria-hidden="true" />
                                    Failed to load world hierarchy.
                                </div>
                            )}
                            {rootData?.children.map(slot => (
                                <SlotRow
                                    key={slot.refId}
                                    slot={slot}
                                    depth={0}
                                    selected={selectedRefId}
                                    onSelect={setSelectedRefId}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Right: inspector + asset injector */}
                    <div className="space-y-4">
                        {/* Inspector */}
                        <div className="glass-card border border-white/10 rounded-xl overflow-hidden">
                            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/10 bg-card/20">
                                <Box className="w-4 h-4 text-violet-400" aria-hidden="true" />
                                <span className="text-xs font-bold text-slate-200 uppercase tracking-widest">Inspector</span>
                                {selectedRefId && (
                                    <span className="ml-auto text-[9px] font-mono text-slate-600 truncate max-w-[120px]">{selectedRefId}</span>
                                )}
                            </div>
                            {selectedRefId
                                ? <Inspector refId={selectedRefId} />
                                : <p className="text-xs text-slate-700 p-4">Select a slot from the hierarchy to inspect.</p>
                            }
                        </div>

                        {/* Asset Inject */}
                        <div className="glass-card border border-white/10 rounded-xl p-4">
                            <AssetPanel targetSlot={selectedRefId} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
