import { useState } from 'react';
import { Package, Search, ExternalLink, Folder, File } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { cn } from '@/common/utils';

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
    const r = await fetch(`/api/records?${params}`);
    if (!r.ok) throw new Error(`Failed: ${r.status}`);
    const data = await r.json() as { records?: Record[] };
    return data.records ?? (Array.isArray(data) ? data as Record[] : []);
}

export function Inventory() {
    const [path, setPath] = useState('Inventory');
    const [inputPath, setInputPath] = useState('Inventory');

    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['records', path],
        queryFn: () => fetchRecords(path),
    });

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center gap-3">
                <Package className="w-5 h-5 text-purple-400" aria-hidden="true" />
                <div>
                    <h2 className="text-lg font-bold gradient-text">Inventory</h2>
                    <p className="text-sm text-slate-500">Browse your Resonite records &amp; inventory</p>
                </div>
            </div>

            {/* Path browser */}
            <div className="glass-card p-4 flex gap-2">
                <input
                    type="text"
                    value={inputPath}
                    onChange={e => setInputPath(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && setPath(inputPath)}
                    placeholder="Record path, e.g. Inventory/WorldLabs"
                    className="input-glass flex-1 text-sm font-mono"
                    aria-label="Record path"
                />
                <button
                    onClick={() => setPath(inputPath)}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-purple-600/40 hover:bg-purple-600/60 border border-purple-500/30 text-sm text-purple-300 transition-all"
                    aria-label="Browse path"
                >
                    <Search className="w-4 h-4" aria-hidden="true" />
                    Browse
                </button>
            </div>

            {/* Auth warning */}
            {isError && (
                <div className="glass-card p-4 border border-amber-500/20 bg-amber-500/10">
                    <p className="text-sm text-amber-300">
                        {String(error).includes('401')
                            ? 'Authentication required. Set RESONITE_USER_ID + RESONITE_TOKEN or use resonite_rest_login.'
                            : String(error)}
                    </p>
                </div>
            )}

            {isLoading && <p className="text-sm text-slate-600">Loading {path}…</p>}

            {/* Records grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {data?.map(rec => (
                    <div key={rec.id} className={cn('glass-card p-3 space-y-2 group cursor-pointer hover:border-purple-500/30 transition-all')}>
                        {rec.thumbnailUri ? (
                            <img src={rec.thumbnailUri} alt={rec.name} className="w-full aspect-square object-cover rounded-md" />
                        ) : (
                            <div className="w-full aspect-square rounded-md bg-white/[0.03] flex items-center justify-center">
                                {rec.recordType === 'directory' ? (
                                    <Folder className="w-8 h-8 text-slate-600" aria-hidden="true" />
                                ) : (
                                    <File className="w-8 h-8 text-slate-600" aria-hidden="true" />
                                )}
                            </div>
                        )}
                        <div>
                            <p className="text-xs font-medium text-slate-200 truncate" title={rec.name}>{rec.name}</p>
                            {rec.recordType && <p className="text-[10px] text-slate-600 capitalize">{rec.recordType}</p>}
                        </div>
                        {rec.recordType === 'directory' && (
                            <button
                                onClick={() => { setPath(rec.path ?? rec.name); setInputPath(rec.path ?? rec.name); }}
                                className="w-full text-xs text-purple-400 hover:text-purple-200 flex items-center gap-1 transition-colors"
                                aria-label={`Open folder ${rec.name}`}
                            >
                                <ExternalLink className="w-3 h-3" aria-hidden="true" />
                                Open
                            </button>
                        )}
                    </div>
                ))}
            </div>

            {data?.length === 0 && !isLoading && (
                <p className="text-sm text-slate-600 text-center py-8">No records found at {path}</p>
            )}
        </div>
    );
}
