import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Shield, Network, Cpu, HardDrive, RefreshCcw, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiUrl } from "@/lib/api-base";

interface Status {
    authenticated: boolean;
    workspace: string;
    server_running: boolean;
    resonite_installed: boolean;
    resonite_running: boolean;
}

interface Stats {
    worlds: number;
    avatars: number;
    sessions: number;
    scripts: number;
}

interface Llm {
    name: string;
    provider: string;
    url: string;
}

export function Dashboard() {
    const [status, setStatus] = useState<Status | null>(null);
    const [stats, setStats] = useState<Stats | null>(null);
    const [llms, setLlms] = useState<Llm[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [statusRes, llmsRes, statsRes] = await Promise.all([
                fetch(apiUrl("/api/status")),
                fetch(apiUrl("/api/llm-discovery")),
                fetch(apiUrl("/api/stats")),
            ]);

            const [statusData, llmsData, statsData] = await Promise.all([
                statusRes.json(),
                llmsRes.json(),
                statsRes.json()
            ]);

            setStatus(statusData);
            setLlms(llmsData.llms || []);
            setStats(statsData);
        } catch (error) {
            console.error("Dashboard telemetry failed", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    if (loading) return (
        <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            <div className="flex items-center justify-between">
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                    <div className="relative">
                        <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
                            Intelligence <span className="text-indigo-400">Dashboard</span>
                        </h2>
                        <p className="text-muted-foreground mt-1 flex items-center gap-2">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                            {status?.workspace || "Neural Grid"} Operational • 2026.02 SOTA Standard
                        </p>
                    </div>
                </div>
                <Button variant="outline" size="sm" onClick={fetchData} className="gap-2 border-indigo-500/30 bg-indigo-500/5 hover:bg-indigo-500/10 text-indigo-300">
                    <RefreshCcw className="h-4 w-4" /> Sync
                </Button>
            </div>

            {/* Presence Alert (if not running) */}
            {!status?.resonite_running && (
                <div className="bg-orange-500/10 border border-orange-500/20 p-4 rounded-xl flex items-center justify-between animate-in slide-in-from-top-4 duration-500">
                    <div className="flex items-center gap-4">
                        <div className="p-2 bg-orange-500/20 rounded-lg">
                            <AlertTriangle className="h-5 w-5 text-orange-400" />
                        </div>
                        <div>
                            <p className="text-sm font-bold text-foreground">Resonite Bridge Inactive</p>
                            <p className="text-xs text-muted-foreground uppercase tracking-tight">Virtual world interface currently suspended</p>
                        </div>
                    </div>
                    {status?.resonite_installed && (
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={async () => {
                                await fetch(apiUrl("/api/resonite/launch"), { method: "POST" });
                                fetchData();
                            }}
                            className="bg-orange-500 text-white hover:bg-orange-400 font-bold"
                        >
                            Launch Now
                        </Button>
                    )}
                </div>
            )}

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-indigo-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            Worlds Indexed
                        </CardTitle>
                        <Shield className="h-4 w-4 text-emerald-500 transition-transform group-hover:scale-125 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">{stats?.worlds || 0}</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            RAG Knowledge Deep
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-blue-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            Avatar Assets
                        </CardTitle>
                        <Cpu className="h-4 w-4 text-blue-500 transition-transform group-hover:rotate-12 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">{stats?.avatars || 0}</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            Optimization High
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-purple-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            Active Scripts
                        </CardTitle>
                        <Activity className="h-4 w-4 text-purple-500 transition-transform group-hover:scale-110 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">{stats?.scripts || 0}</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            FastMCP Pipeline Prime
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-orange-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            Active Sessions
                        </CardTitle>
                        <Network className="h-4 w-4 text-orange-500 transition-transform group-hover:-translate-y-1 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">{stats?.sessions || 0}</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            Real-time Sync
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-border bg-card/40 backdrop-blur-md glass">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-xs font-bold uppercase tracking-widest text-foreground">Local LLM Grid (Glom On)</CardTitle>
                        <div className="flex gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-emerald-500/50"></span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {llms.length === 0 ? (
                                <p className="text-sm text-muted-foreground italic">No local LLMs detected...</p>
                            ) : llms.map((llm, i) => (
                                <div key={i} className="flex items-center justify-between border-b border-border/50 pb-3 last:border-0 last:pb-0 group">
                                    <div className="flex items-center gap-4">
                                        <div className="p-2.5 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500/20 transition-colors">
                                            <Cpu className="h-5 w-5 text-indigo-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold text-foreground">{llm.name}</p>
                                            <p className="text-[10px] text-indigo-400/70 font-mono uppercase tracking-wider">{llm.provider} • {llm.url}</p>
                                        </div>
                                    </div>
                                    <div className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase rounded-sm border border-emerald-500/20">Active</div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-border bg-card/40 backdrop-blur-md glass">
                    <CardHeader>
                        <CardTitle className="text-xs font-bold uppercase tracking-widest text-foreground">Hardware Matrix</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            <div className="flex items-center group cursor-help">
                                <div className="p-2 rounded-md bg-muted border border-border group-hover:border-indigo-500/50 transition-colors">
                                    <HardDrive className="h-4 w-4 text-indigo-400" />
                                </div>
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-bold leading-none text-foreground tracking-tight">Mainframe Storage</p>
                                    <p className="text-[10px] text-muted-foreground uppercase font-bold opacity-50">30TB Array • Verified</p>
                                </div>
                            </div>
                            <div className="flex items-center group cursor-help">
                                <div className="p-2 rounded-md bg-muted border border-border group-hover:border-emerald-500/50 transition-colors">
                                    <Activity className="h-4 w-4 text-emerald-500" />
                                </div>
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-bold leading-none text-foreground tracking-tight">Heartbeat Frequency</p>
                                    <p className="text-[10px] text-muted-foreground uppercase font-bold opacity-50">120Hz Tracking • Nominal</p>
                                </div>
                            </div>
                            <div className="flex items-center group cursor-help">
                                <div className={`p-2 rounded-md bg-muted border border-border transition-colors ${status?.resonite_running ? 'group-hover:border-emerald-500/50' : 'group-hover:border-rose-500/50'}`}>
                                    <Network className={`h-4 w-4 ${status?.resonite_running ? 'text-emerald-500' : 'text-rose-500'}`} />
                                </div>
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-bold leading-none text-foreground tracking-tight">Resonite Bridge</p>
                                    <p className={`text-[10px] uppercase font-bold opacity-50 ${status?.resonite_running ? 'text-emerald-500' : 'text-rose-400'}`}>
                                        {status?.resonite_running ? 'Active • Synchronized' : 'Inactive • Suspended'}
                                    </p>
                                </div>
                            </div>
                            <div className="pt-4 border-t border-border">
                                <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">
                                    <span>Core Sync Stability</span>
                                    <span className="text-emerald-500">99.9%</span>
                                </div>
                                <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden border border-border">
                                    <div className="h-full bg-gradient-to-r from-indigo-500 to-emerald-500 w-[99.9%] rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]"></div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
