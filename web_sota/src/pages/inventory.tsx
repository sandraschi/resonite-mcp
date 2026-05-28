import { useState, useMemo } from 'react';
import { Package, Search, Folder, File, ChevronRight, LayoutGrid, List as ListIcon, Info, AlertTriangle, Loader2, ArrowLeft, Plus, Upload, Trash2, Share2, Play } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cn } from '../common/utils';
import { Card, CardContent } from "@/components/ui/card";
import { apiUrl } from '@/lib/api-base';

interface Record {
    id: string;
    name: string;
    recordType?: string;
    path?: string;
    thumbnailUri?: string;
    lastModificationTime?: string;
}

async function fetchRecords(path: string): Promise<Record[]> {
    const params = new URLSearchParams({ path: path || 'Inventory' });
    const r = await fetch(apiUrl(`/api/records?${params}`));
    if (!r.ok) {
        if (r.status === 401) throw new Error('AUTH_REQUIRED');
        throw new Error(`Failed: ${r.status}`);
    }
    const data = await r.json() as { records?: Record[] };
    return data.records ?? (Array.isArray(data) ? data as Record[] : []);
}

export function Inventory() {
    const queryClient = useQueryClient();
    const [path, setPath] = useState('Inventory');
    const [inputPath, setInputPath] = useState('Inventory');
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

    const { data: records, isLoading, isError, error, refetch } = useQuery({
        queryKey: ['records', path],
        queryFn: () => fetchRecords(path),
        retry: false
    });

    const spawnMutation = useMutation({
        mutationFn: async (record: Record) => {
            const r = await fetch(apiUrl('/api/resonite/inventory/spawn'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_path: record.path || `${path}/${record.name}` })
            });
            if (!r.ok) throw new Error('Spawn failed');
            return r.json();
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (record: Record) => {
            const r = await fetch(apiUrl('/api/resonite/inventory/delete'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_path: record.path || `${path}/${record.name}` })
            });
            if (!r.ok) throw new Error('Delete failed');
            return r.json();
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['records'] })
    });

    const breadcrumbs = useMemo(() => {
        const parts = path.split('/').filter(Boolean);
        return parts.map((part, i) => ({
            name: part,
            path: parts.slice(0, i + 1).join('/')
        }));
    }, [path]);

    const handleNavigate = (newPath: string) => {
        setPath(newPath);
        setInputPath(newPath);
    };

    const handleBack = () => {
        const parts = path.split('/');
        if (parts.length > 1) {
            const nextPath = parts.slice(0, -1).join('/');
            handleNavigate(nextPath);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Header Section */}
            <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                <div className="relative flex flex-col md:flex-row md:items-end justify-between gap-6 bg-card/40 backdrop-blur-xl border border-white/10 p-6 rounded-xl glass-card">
                    <div className="flex items-center gap-5">
                        <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl shadow-inner group-hover:scale-110 transition-transform duration-500">
                            <Package className="w-8 h-8 text-purple-400 animate-pulse-slow" />
                        </div>
                        <div>
                            <h2 className="text-3xl font-black tracking-tighter text-foreground bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/60">
                                Inventory <span className="text-purple-400">Vault</span>
                            </h2>
                            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1 opacity-70 flex items-center gap-2">
                                <span className="h-1.5 w-1.5 rounded-full bg-purple-500 animate-pulse"></span>
                                Neural Storage Nexus • Level 4 Access
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            title="Upload Asset"
                            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all shadow-lg shadow-purple-500/20 active:scale-95 border border-purple-400/30"
                        >
                            <Upload className="w-4 h-4" />
                            Upload
                        </button>
                        <button
                            title="New Folder"
                            className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border border-white/10 active:scale-95"
                        >
                            <Plus className="w-4 h-4" />
                            Folder
                        </button>
                        <div className="w-px h-8 bg-white/10 mx-2 hidden md:block"></div>
                        <div className="flex items-center gap-1 bg-black/20 p-1.5 rounded-lg border border-white/5">
                            <button
                                onClick={() => setViewMode('grid')}
                                title="Grid View"
                                className={cn(
                                    "p-2 rounded-md transition-all duration-300",
                                    viewMode === 'grid' ? "bg-purple-500/20 text-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.2)]" : "text-muted-foreground hover:text-foreground"
                                )}
                            >
                                <LayoutGrid className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                title="List View"
                                className={cn(
                                    "p-2 rounded-md transition-all duration-300",
                                    viewMode === 'list' ? "bg-purple-500/20 text-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.2)]" : "text-muted-foreground hover:text-foreground"
                                )}
                            >
                                <ListIcon className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation & Search */}
            <div className="grid gap-4 md:grid-cols-[auto_1fr] items-center">
                <button
                    onClick={handleBack}
                    disabled={path === 'Inventory'}
                    title="Go Back"
                    className="flex items-center justify-center w-12 h-12 rounded-xl border border-white/10 bg-card/40 backdrop-blur-md hover:border-purple-500/50 disabled:opacity-30 disabled:cursor-not-allowed transition-all group"
                >
                    <ArrowLeft className="w-5 h-5 text-purple-400 group-hover:-translate-x-1 transition-transform" />
                </button>

                <div className="relative group flex-1">
                    <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-muted-foreground group-focus-within:text-purple-400 transition-colors" />
                    </div>
                    <input
                        type="text"
                        value={inputPath}
                        title="Search Path"
                        onChange={e => setInputPath(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && setPath(inputPath)}
                        className="w-full bg-card/40 backdrop-blur-md border border-white/10 focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/20 rounded-xl py-3 pl-12 pr-4 text-sm font-mono tracking-tight transition-all outline-none"
                        placeholder="Neural Path (e.g. Inventory/Assets/Shaders)"
                    />
                    <div className="absolute inset-y-1.5 right-1.5">
                        <button
                            onClick={() => setPath(inputPath)}
                            title="Synchronize Path"
                            className="h-full px-4 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-[10px] font-bold uppercase tracking-widest border border-purple-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
                        >
                            Sync Path
                        </button>
                    </div>
                </div>
            </div>


            {/* Breadcrumbs */}
            <nav className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide no-scrollbar">
                <button
                    onClick={() => handleNavigate('Inventory')}
                    className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground hover:text-purple-400 transition-colors flex items-center gap-1 shrink-0"
                >
                    Root
                </button>
                {breadcrumbs.map((bc, i) => (
                    <div key={bc.path} className="flex items-center gap-2 shrink-0">
                        <ChevronRight className="w-3 h-3 text-white/20" />
                        <button
                            onClick={() => handleNavigate(bc.path)}
                            className={cn(
                                "text-[10px] font-bold uppercase tracking-widest transition-colors",
                                i === breadcrumbs.length - 1 ? "text-purple-400 pointer-events-none" : "text-muted-foreground hover:text-purple-400"
                            )}
                        >
                            {bc.name}
                        </button>
                    </div>
                ))}
            </nav>

            {/* Error States */}
            {isError && (
                <Card className="border-amber-500/20 bg-amber-500/5 backdrop-blur-md overflow-hidden">
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                            <AlertTriangle className="w-5 h-5 text-amber-500" />
                        </div>
                        <div className="flex-1">
                            <p className="text-sm font-bold text-amber-200">System Anomaly Detected</p>
                            <p className="text-[11px] text-amber-500/70 font-medium">
                                {error?.message === 'AUTH_REQUIRED'
                                    ? 'High-level authentication required. Ensure RESONITE_USER_ID is provisioned.'
                                    : error?.message || 'Unknown matrix error occurred during synchronization.'}
                            </p>
                        </div>
                        <button
                            onClick={() => refetch()}
                            className="px-4 py-2 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 text-[10px] font-bold uppercase tracking-widest text-amber-400 transition-all"
                        >
                            Retry Sync
                        </button>
                    </CardContent>
                </Card>
            )}

            {/* Loading Grid */}
            {isLoading && (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 animate-pulse">
                    {[...Array(12)].map((_, i) => (
                        <div key={i} className="aspect-square rounded-xl bg-card/40 border border-white/5" />
                    ))}
                    <div className="col-span-full flex flex-col items-center justify-center py-12 text-muted-foreground gap-3">
                        <Loader2 className="w-8 h-8 animate-spin text-purple-500/50" />
                        <p className="text-[10px] font-bold uppercase tracking-[0.3em]">Synching Neural Records...</p>
                    </div>
                </div>
            )}

            {/* Data Display */}
            {!isLoading && !isError && (
                <>
                    {records && records.length > 0 ? (
                        <div className={cn(
                            "grid gap-4 transition-all duration-500 animate-in fade-in slide-in-from-bottom-4",
                            viewMode === 'grid'
                                ? "grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6"
                                : "grid-cols-1"
                        )}>
                            {records.map((rec) => (
                                <div
                                    key={rec.id}
                                    onClick={() => rec.recordType === 'directory' && handleNavigate(rec.path ?? `${path}/${rec.name}`)}
                                    className={cn(
                                        "group relative bg-card/40 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden cursor-pointer transition-all duration-300 hover:border-purple-500/50 hover:bg-card/60 hover:-translate-y-1 hover:shadow-[0_10px_30px_rgba(0,0,0,0.5),0_0_20px_rgba(168,85,247,0.1)]",
                                        viewMode === 'list' && "flex items-center gap-4 p-3 h-20"
                                    )}
                                >
                                    {/* Thumbnail / Icon Wrapper */}
                                    <div className={cn(
                                        "relative overflow-hidden bg-black/40",
                                        viewMode === 'grid' ? "aspect-square w-full" : "h-14 w-14 rounded-lg shrink-0"
                                    )}>
                                        {rec.thumbnailUri ? (
                                            <img
                                                src={rec.thumbnailUri}
                                                alt={rec.name}
                                                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                                loading="lazy"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center">
                                                {rec.recordType === 'directory' ? (
                                                    <Folder className="w-8 h-8 text-indigo-400 group-hover:scale-110 transition-transform duration-500" />
                                                ) : (
                                                    <File className="w-8 h-8 text-slate-500 group-hover:scale-110 transition-transform duration-500" />
                                                )}
                                            </div>
                                        )}

                                        {/* Action Overlays for Objects */}
                                        {rec.recordType !== 'directory' && (
                                            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 p-2">
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); spawnMutation.mutate(rec); }}
                                                    disabled={spawnMutation.isPending}
                                                    title={`Spawn ${rec.name}`}
                                                    className="p-2 rounded-lg bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/40 transition-all active:scale-95"
                                                >
                                                    <Play className="w-4 h-4 fill-current" />
                                                </button>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); }}
                                                    title={`Share ${rec.name}`}
                                                    className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/40 transition-all active:scale-95"
                                                >
                                                    <Share2 className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(rec); }}
                                                    disabled={deleteMutation.isPending}
                                                    title={`Delete ${rec.name}`}
                                                    className="p-2 rounded-lg bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/40 transition-all active:scale-95"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        )}

                                        {/* Type Overlay */}
                                        <div className="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                                            <p className="text-[8px] font-black uppercase tracking-tighter text-white/70">
                                                {rec.recordType}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Content Wrapper */}
                                    <div className={cn(
                                        "p-3 space-y-1 flex flex-col justify-center min-w-0 flex-1",
                                        viewMode === 'list' && "p-0"
                                    )}>
                                        <h3 className="text-[11px] font-bold text-foreground truncate group-hover:text-purple-400 transition-colors" title={rec.name}>
                                            {rec.name}
                                        </h3>
                                        <div className="flex items-center justify-between gap-2">
                                            <span className="text-[9px] text-muted-foreground font-mono truncate uppercase opacity-60">
                                                {rec.id.split('-')[0]}
                                            </span>
                                            {rec.recordType === 'directory' && (
                                                <ChevronRight className="w-3 h-3 text-purple-500/50 group-hover:text-purple-400 transition-colors shrink-0" />
                                            )}
                                        </div>
                                    </div>

                                    {/* Action Hover */}
                                    {viewMode === 'grid' && (
                                        <div className="absolute inset-0 bg-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-20 bg-card/20 backdrop-blur-sm border border-dashed border-white/10 rounded-2xl gap-4">
                            <div className="p-4 rounded-full bg-muted border border-border">
                                <Info className="w-6 h-6 text-muted-foreground" />
                            </div>
                            <div className="text-center">
                                <p className="text-sm font-bold text-foreground">Record Repository Empty</p>
                                <p className="text-[11px] text-muted-foreground max-w-[200px] mx-auto mt-1 uppercase tracking-tight">
                                    The path <span className="text-purple-400 font-mono tracking-tighter lowercase">{path}</span> contains no neural assets.
                                </p>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}



