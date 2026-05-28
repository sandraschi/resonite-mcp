import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Navigation, Users, RefreshCw, Layers, ZoomIn, ZoomOut } from 'lucide-react';
import { cn } from '@/common/utils';
import { apiUrl } from '@/lib/api-base';

interface Node {
    id: string;
    name: string;
    position: { x: number; y: number; z: number };
    type: 'avatar' | 'object';
}


export function Map() {
    const [zoom, setZoom] = useState(1.0);
    const { data, isLoading, refetch, isFetching } = useQuery({
        queryKey: ['world-map'],
        queryFn: async () => {
            const resp = await fetch(apiUrl('/api/world/map-data'));
            return resp.json();
        },
        refetchInterval: 3000, // Poll every 3 seconds
    });

    const nodes = data?.nodes || [];
    const isConnected = data?.connected ?? false;

    // Map configuration
    const mapSize = 600;
    const worldSize = 100 / zoom; // View range in meters

    const project = (val: number) => {
        return (val / worldSize) * (mapSize / 2) + (mapSize / 2);
    };

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-pink-500/20 text-pink-400 border border-pink-500/30 shadow-lg shadow-pink-500/10">
                        <Navigation className="h-6 w-6" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight text-foreground">Spatial Map</h1>
                        <p className="text-sm text-muted-foreground">Real-time 2D visualization of the current world.</p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <div className="flex items-center bg-card/50 border border-border rounded-lg p-1">
                        <button
                            onClick={() => setZoom(z => Math.max(0.5, z - 0.2))}
                            className="p-1.5 hover:bg-white/5 rounded-md text-muted-foreground hover:text-foreground transition-colors"
                            aria-label="Zoom Out"
                            title="Zoom Out"
                        >
                            <ZoomOut className="h-4 w-4" />
                        </button>
                        <span className="px-2 text-xs font-mono text-muted-foreground w-12 text-center">{zoom.toFixed(1)}x</span>
                        <button
                            onClick={() => setZoom(z => Math.min(5, z + 0.2))}
                            className="p-1.5 hover:bg-white/5 rounded-md text-muted-foreground hover:text-foreground transition-colors"
                            aria-label="Zoom In"
                            title="Zoom In"
                        >
                            <ZoomIn className="h-4 w-4" />
                        </button>
                    </div>

                    <button
                        onClick={() => refetch()}
                        disabled={isLoading || isFetching}
                        className={cn(
                            "flex items-center gap-2 rounded-lg bg-indigo-500/15 border border-indigo-500/30 px-3 py-1.5 text-xs font-medium text-indigo-300 transition-all hover:bg-indigo-500/25",
                            isFetching && "animate-pulse"
                        )}
                    >
                        <RefreshCw className={cn("h-3.5 w-3.5", isFetching && "animate-spin")} />
                        {isFetching ? 'Scanning...' : 'Scan World'}
                    </button>

                    <div className={cn(
                        "h-2 w-2 rounded-full",
                        isConnected ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" : "bg-red-500"
                    )} />
                </div>
            </header>

            <div className="grid gap-6 lg:grid-cols-4">
                {/* Map Visualizer */}
                <div className="lg:col-span-3 rounded-3xl border border-border bg-card/20 p-4 backdrop-blur-sm relative overflow-hidden shadow-2xl min-h-[600px] flex items-center justify-center">
                    {/* Grid Background */}
                    <style>{`
                        .map-grid-bg {
                            background-image: radial-gradient(circle, #6366f1 1px, transparent 1px);
                            background-size: ${30 * zoom}px ${30 * zoom}px;
                        }
                    `}</style>
                    <div className="absolute inset-0 opacity-20 pointer-events-none map-grid-bg" />

                    {!isConnected && !isLoading && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/40 backdrop-blur-sm z-10">
                            <Layers className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
                            <h3 className="text-lg font-bold text-foreground">No Connection</h3>
                            <p className="text-sm text-muted-foreground">Please connect through ResoniteLink to see world data.</p>
                            <a href="/resonite-link" className="mt-4 px-4 py-2 bg-indigo-500 text-white rounded-lg text-sm font-semibold hover:bg-indigo-400 transition-colors">
                                Connect to Link
                            </a>
                        </div>
                    )}

                    <svg
                        viewBox={`0 0 ${mapSize} ${mapSize}`}
                        className="w-full h-full max-w-[600px] max-h-[600px] relative z-0"
                    >
                        {/* Reference Axis */}
                        <line x1={mapSize / 2} y1="0" x2={mapSize / 2} y2={mapSize} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                        <line x1="0" y1={mapSize / 2} x2={mapSize} y2={mapSize / 2} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                        <circle cx={mapSize / 2} cy={mapSize / 2} r={mapSize / 2} fill="none" stroke="rgba(99,102,241,0.1)" strokeWidth="1" />

                        {/* Nodes */}
                        {nodes.map((node: Node) => {
                            const x = project(node.position.x);
                            const y = project(-node.position.z); // Z is usually forward/back in 3D, mapped to Y in 2D

                            // Bounds check
                            if (x < 0 || x > mapSize || y < 0 || y > mapSize) return null;

                            return (
                                <g key={node.id} className="transition-all duration-700">
                                    <circle
                                        cx={x}
                                        cy={y}
                                        r={node.type === 'avatar' ? 8 : 4}
                                        className={cn(
                                            "transition-colors",
                                            node.type === 'avatar' ? "fill-pink-500/80 stroke-pink-400" : "fill-indigo-500/40 stroke-indigo-400"
                                        )}
                                        strokeWidth="2"
                                    />
                                    {node.type === 'avatar' && (
                                        <circle cx={x} cy={y} r={12} className="fill-none stroke-pink-500/20 animate-ping" strokeWidth="1" />
                                    )}
                                    <text
                                        x={x}
                                        y={y + (node.type === 'avatar' ? 20 : 15)}
                                        className="fill-muted-foreground text-[10px] font-bold uppercase tracking-widest text-center"
                                        textAnchor="middle"
                                    >
                                        {node.name}
                                    </text>
                                </g>
                            );
                        })}
                    </svg>

                    {/* Compass */}
                    <div className="absolute bottom-6 right-6 flex h-12 w-12 items-center justify-center rounded-full bg-black/40 border border-white/5 text-muted-foreground text-[10px] font-bold shadow-lg">
                        <div className="relative">
                            <div className="absolute top-[-15px] left-1/2 -translate-x-1/2 text-white">N</div>
                            <div className="h-8 w-0.5 bg-indigo-500/50 rounded-full" />
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-1.5 w-1.5 rounded-full bg-indigo-500" />
                        </div>
                    </div>

                    <div className="absolute bottom-6 left-6 text-[10px] font-mono text-muted-foreground uppercase tracking-widest border border-white/5 bg-black/40 px-3 py-1.5 rounded-full backdrop-blur-md">
                        Scale: 1:{Math.round(100 / zoom)}m
                    </div>
                </div>

                {/* Legend & Stats */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="rounded-2xl border border-border bg-card/30 p-6 backdrop-blur-md shadow-xl">
                        <h3 className="text-sm font-bold text-foreground mb-4 uppercase tracking-wider flex items-center gap-2">
                            <Layers className="h-4 w-4 text-indigo-400" />
                            World Legend
                        </h3>
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <div className="h-3 w-3 rounded-full bg-pink-500 shadow-[0_0_8px_rgba(236,72,153,0.5)]" />
                                <div className="flex-1">
                                    <span className="text-xs font-semibold text-foreground block">Active Avatars</span>
                                    <span className="text-[10px] text-muted-foreground">User-controlled entities</span>
                                </div>
                                <span className="text-xs font-mono text-muted-foreground">
                                    {nodes.filter((n: Node) => n.type === 'avatar').length}
                                </span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="h-3 w-3 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.5)]" />
                                <div className="flex-1">
                                    <span className="text-xs font-semibold text-foreground block">World Objects</span>
                                    <span className="text-[10px] text-muted-foreground">Tracked landmarks & props</span>
                                </div>
                                <span className="text-xs font-mono text-muted-foreground">
                                    {nodes.filter((n: Node) => n.type === 'object').length}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="rounded-2xl border border-border bg-card/30 p-6 backdrop-blur-md shadow-xl overflow-y-auto max-h-[350px] scrollbar-thin">
                        <h3 className="text-sm font-bold text-foreground mb-4 uppercase tracking-wider flex items-center gap-2">
                            <Users className="h-4 w-4 text-pink-400" />
                            Current Users
                        </h3>
                        <div className="space-y-2">
                            {nodes.filter((n: Node) => n.type === 'avatar').map((user: Node) => (
                                <div key={user.id} className="flex items-center justify-between p-2 rounded-lg bg-white/5 border border-white/5 group hover:border-indigo-500/30 transition-colors">
                                    <div className="flex items-center gap-2">
                                        <div className="h-1.5 w-1.5 rounded-full bg-pink-400 animate-pulse" />
                                        <span className="text-xs text-foreground group-hover:text-pink-300 transition-colors">{user.name}</span>
                                    </div>
                                    <span className="text-[10px] font-mono text-muted-foreground">
                                        {Math.round(user.position.x)}, {Math.round(user.position.z)}
                                    </span>
                                </div>
                            ))}
                            {nodes.filter((n: Node) => n.type === 'avatar').length === 0 && (
                                <div className="text-center py-6">
                                    <p className="text-xs text-muted-foreground italic">No avatars detected</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
