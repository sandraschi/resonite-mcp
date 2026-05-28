import { Box, Search, Upload, Download, Trash2, Share2, FolderOpen, MoreVertical, Plus, LayoutGrid, List as ListIcon, HardDrive, Package, ShieldCheck, Globe2 } from 'lucide-react';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiUrl } from '@/lib/api-base';

interface InventoryItem {
    name: string;
    path: string;
    type: 'folder' | 'object' | 'world' | 'avatar';
    id?: string;
    ownerId?: string;
    lastModified?: string;
}

export function IoPage() {
    const queryClient = useQueryClient();
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [currentPath, setCurrentPath] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    const { data: inventory, isLoading } = useQuery({
        queryKey: ['inventory', currentPath],
        queryFn: async () => {
            const r = await fetch(apiUrl(`/api/resonite/inventory/list?path=${encodeURIComponent(currentPath)}`));
            if (!r.ok) throw new Error('Failed to fetch inventory');
            return r.json();
        }
    });

    const spawnMutation = useMutation({
        mutationFn: async (item: InventoryItem) => {
            const r = await fetch(apiUrl('/api/resonite/inventory/spawn'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_path: item.path })
            });
            return r.json();
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (item: InventoryItem) => {
            const r = await fetch(apiUrl('/api/resonite/inventory/delete'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_path: item.path })
            });
            return r.json();
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['inventory'] })
    });

    const items: InventoryItem[] = inventory?.items || [];
    const filteredItems = items.filter(item =>
        item.name?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="space-y-6 page-enter">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="bg-indigo-500/10 p-2.5 rounded-xl border border-indigo-500/20">
                        <Package className="w-6 h-6 text-indigo-400" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">Inventory & Objects</h2>
                        <p className="text-sm text-slate-500">Manage Resonite assets, collections, and world objects</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        title="Upload Asset"
                        aria-label="Upload Asset"
                        className="flex items-center gap-2 bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all shadow-lg shadow-indigo-500/20 active:scale-95"
                    >
                        <Upload className="w-4 h-4" />
                        Upload Asset
                    </button>
                    <button
                        title="New Folder"
                        aria-label="New Folder"
                        className="flex items-center gap-2 bg-white/[0.05] hover:bg-white/[0.1] text-white px-4 py-2 rounded-xl text-sm font-medium transition-all border border-white/[0.08] active:scale-95"
                    >
                        <Plus className="w-4 h-4" />
                        New Folder
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="md:col-span-1 space-y-4">
                    <div className="glass-card p-4 space-y-4">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Storage</h3>
                        <div className="space-y-2">
                            <button
                                title="Primary Cloud Storage"
                                aria-label="Switch to Primary Cloud Storage"
                                className="w-full flex items-center justify-between p-2 rounded-lg bg-indigo-500/10 text-indigo-400 text-sm border border-indigo-500/20"
                            >
                                <div className="flex items-center gap-2">
                                    <HardDrive className="w-4 h-4" />
                                    <span>Primary Cloud</span>
                                </div>
                                <span className="text-[10px] font-mono opacity-60">S-1</span>
                            </button>
                            <button
                                title="Local Cache Storage"
                                aria-label="Switch to Local Cache Storage"
                                className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-white/5 text-slate-400 text-sm transition-colors border border-transparent"
                            >
                                <div className="flex items-center gap-2">
                                    <Box className="w-4 h-4" />
                                    <span>Local Cache</span>
                                </div>
                            </button>
                        </div>

                        <div className="pt-4 border-t border-white/[0.05] space-y-2">
                            <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2">Quick Filters</h3>
                            <button
                                title="Filter by Avatars"
                                aria-label="Filter by Avatars"
                                className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 text-slate-500 hover:text-slate-300 text-xs transition-colors"
                            >
                                <ShieldCheck className="w-3.5 h-3.5" />
                                <span>Avatars</span>
                            </button>
                            <button
                                title="Filter by Worlds"
                                aria-label="Filter by Worlds"
                                className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 text-slate-500 hover:text-slate-300 text-xs transition-colors"
                            >
                                <Globe2 className="w-3.5 h-3.5" />
                                <span>Worlds</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div className="md:col-span-3 space-y-4">
                    <div className="glass-card p-4 flex items-center justify-between gap-4">
                        <div className="flex items-center gap-4 flex-1">
                            <div className="relative flex-1 max-w-md">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                <input
                                    type="text"
                                    title="Search inventory"
                                    aria-label="Search items in current directory"
                                    placeholder="Search in current path..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full bg-black/20 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50 transition-all font-light"
                                />
                            </div>
                        </div>
                        <div className="flex items-center gap-1 bg-black/20 p-1 rounded-lg border border-white/[0.08]">
                            <button
                                onClick={() => setViewMode('grid')}
                                title="Grid View"
                                aria-label="Switch to Grid View"
                                className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-indigo-500 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                            >
                                <LayoutGrid className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                title="List View"
                                aria-label="Switch to List View"
                                className={`p-1.5 rounded ${viewMode === 'list' ? 'bg-indigo-500 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                            >
                                <ListIcon className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-slate-500 px-2 overflow-x-auto whitespace-nowrap scrollbar-hide">
                        <button
                            onClick={() => setCurrentPath('')}
                            title="Go to Root Inventory"
                            aria-label="Go to Root Inventory"
                            className="hover:text-indigo-400"
                        >
                            Inventory
                        </button>
                        {currentPath.split('/').filter(Boolean).map((part, i, arr) => (
                            <div key={i} className="flex items-center gap-2">
                                <span>/</span>
                                <button
                                    onClick={() => setCurrentPath(arr.slice(0, i + 1).join('/'))}
                                    title={`Go to ${part}`}
                                    aria-label={`Go to ${part}`}
                                    className="hover:text-indigo-400"
                                >
                                    {part}
                                </button>
                            </div>
                        ))}
                    </div>

                    {isLoading ? (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} className="glass-card aspect-square animate-pulse" />
                            ))}
                        </div>
                    ) : (
                        <div className={viewMode === 'grid'
                            ? "grid grid-cols-2 lg:grid-cols-4 gap-4"
                            : "space-y-2"
                        }>
                            {filteredItems.map((item, i) => (
                                <div
                                    key={i}
                                    className={`group border border-white/[0.05] hover:border-indigo-500/30 hover:bg-indigo-500/[0.02] transition-all cursor-pointer overflow-hidden ${viewMode === 'grid' ? 'glass-card rounded-2xl flex flex-col' : 'glass-card rounded-xl flex items-center p-3 gap-4'
                                        }`}
                                    onClick={() => item.type === 'folder' && setCurrentPath(item.path)}
                                >
                                    {viewMode === 'grid' ? (
                                        <>
                                            <div className="aspect-square bg-slate-900 flex items-center justify-center relative">
                                                {item.type === 'folder' ? (
                                                    <FolderOpen className="w-12 h-12 text-indigo-400/50" />
                                                ) : (
                                                    <Box className="w-12 h-12 text-slate-700" />
                                                )}
                                                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                                                    <div className="flex gap-2 w-full">
                                                        <button
                                                            onClick={(e) => { e.stopPropagation(); spawnMutation.mutate(item); }}
                                                            title={`Spawn ${item.name}`}
                                                            className="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg py-1.5 text-[10px] font-bold uppercase tracking-wider transition-colors shadow-lg shadow-indigo-500/40"
                                                        >
                                                            Spawn
                                                        </button>
                                                        <button
                                                            onClick={(e) => e.stopPropagation()}
                                                            title={`Share ${item.name}`}
                                                            aria-label={`Share ${item.name}`}
                                                            className="p-1.5 bg-black/40 hover:bg-black/60 text-white rounded-lg transition-colors border border-white/10"
                                                        >
                                                            <Share2 className="w-3.5 h-3.5" />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="p-3">
                                                <div className="flex items-start justify-between gap-1">
                                                    <h4 className="text-sm font-medium text-slate-200 truncate">{item.name}</h4>
                                                    <button
                                                        onClick={(e) => e.stopPropagation()}
                                                        title="More options"
                                                        aria-label={`More options for ${item.name}`}
                                                        className="text-slate-600 hover:text-slate-400"
                                                    >
                                                        <MoreVertical className="w-4 h-4" />
                                                    </button>
                                                </div>
                                                <div className="flex items-center justify-between mt-1">
                                                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-tight">{item.type}</span>
                                                    <span className="text-[10px] text-slate-600 font-mono">1.2 MB</span>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <div className="p-2 bg-slate-900 rounded-lg">
                                                {item.type === 'folder' ? <FolderOpen className="w-5 h-5 text-indigo-400" /> : <Box className="w-5 h-5 text-slate-500" />}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h4 className="text-sm font-medium text-slate-200 truncate">{item.name}</h4>
                                                <p className="text-[10px] text-slate-500 mt-0.5">{item.type} • {item.lastModified || 'Unknown date'}</p>
                                            </div>
                                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); spawnMutation.mutate(item); }}
                                                    title={`Spawn ${item.name}`}
                                                    className="text-xs text-indigo-400 font-bold px-2 py-1 hover:bg-indigo-500/10 rounded"
                                                >
                                                    SPAWN
                                                </button>
                                                <button
                                                    onClick={(e) => e.stopPropagation()}
                                                    title={`Download ${item.name}`}
                                                    aria-label={`Download ${item.name}`}
                                                    className="p-1 text-slate-500 hover:text-slate-300"
                                                >
                                                    <Download className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(item); }}
                                                    title={`Delete ${item.name}`}
                                                    aria-label={`Delete ${item.name}`}
                                                    className="p-1 text-slate-500 hover:text-rose-500"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {!isLoading && filteredItems.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 glass-card rounded-2xl border-dashed border-white/[0.05] bg-transparent">
                            <Box className="w-12 h-12 text-slate-800 mb-4" />
                            <p className="text-slate-500 font-medium">No results found for your search</p>
                            <button onClick={() => setSearchQuery('')} className="mt-2 text-indigo-400 text-sm hover:underline">Clear search filters</button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
