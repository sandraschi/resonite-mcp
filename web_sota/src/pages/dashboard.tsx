import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Shield, Network, Cpu, HardDrive } from "lucide-react";

export function Dashboard() {
    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative">
                    <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
                        Intelligence <span className="text-indigo-400">Dashboard</span>
                    </h2>
                    <p className="text-muted-foreground mt-1 flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        Neural Grid Operational • 2026.02 SOTA Standard
                    </p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-indigo-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            Security Protocol
                        </CardTitle>
                        <Shield className="h-4 w-4 text-emerald-500 transition-transform group-hover:scale-125 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">ENCRYPTED</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            Zero-Trust Tunnel Active
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-blue-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            Compute Load
                        </CardTitle>
                        <Cpu className="h-4 w-4 text-blue-500 transition-transform group-hover:rotate-12 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">NOMINAL</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            RTX 4090 Optimization High
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-purple-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            API Bridge
                        </CardTitle>
                        <Activity className="h-4 w-4 text-purple-500 transition-transform group-hover:scale-110 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">SYNCED</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            FastMCP Pipeline Prime
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-orange-500/50 transition-all duration-500 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
                            Mesh Latency
                        </CardTitle>
                        <Network className="h-4 w-4 text-orange-500 transition-transform group-hover:-translate-y-1 duration-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-foreground tracking-tight">4ms</div>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold opacity-50">
                            Fibre / Alsergrund Grid
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-border bg-card/40 backdrop-blur-md glass">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-xs font-bold uppercase tracking-widest text-foreground">Intelligence Matrix Logs</CardTitle>
                        <div className="flex gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-red-500/50"></span>
                            <span className="h-2 w-2 rounded-full bg-amber-500/50"></span>
                            <span className="h-2 w-2 rounded-full bg-emerald-500/50"></span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[250px] font-mono text-[11px] p-4 overflow-y-auto border border-border/50 rounded-lg bg-black/40 text-muted-foreground space-y-1.5 scrollbar-thin">
                            <p className="text-blue-400 opacity-80 flex gap-3"><span className="opacity-30">15:42:01</span> [system] Neural daemon v3.0 initialized</p>
                            <p className="flex gap-3"><span className="opacity-30">15:42:02</span> [network] Multiplexing API endpoints...</p>
                            <p className="text-emerald-400 opacity-80 flex gap-3"><span className="opacity-30">15:42:04</span> [success] FastMCP SOTA Bridge established</p>
                            <p className="flex gap-3"><span className="opacity-30">15:42:05</span> [status] Monitoring Resonite headless instance</p>
                            <p className="text-indigo-400 opacity-80 flex gap-3"><span className="opacity-30">15:42:10</span> [mcp] Registered 42 tools to local host</p>
                            <div className="animate-pulse inline-block h-3 w-1.5 bg-indigo-500/50 ml-[72px]" />
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-border bg-card/40 backdrop-blur-md glass">
                    <CardHeader>
                        <CardTitle className="text-xs font-bold uppercase tracking-widest text-foreground">Hardware Status</CardTitle>
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
