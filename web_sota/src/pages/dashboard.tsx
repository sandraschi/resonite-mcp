import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiUrl } from "@/lib/api-base";
import {
    Activity,
    AlertTriangle,
    Cpu,
    HardDrive,
    MessageSquare,
    Network,
    Radio,
    RefreshCcw,
    Shield,
    Wifi,
} from "lucide-react";
import { useEffect, useState } from "react";

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
                fetch(apiUrl("/api/llm-discovery")).catch(() => null),
                fetch(apiUrl("/api/stats")).catch(() => null),
            ]);

            if (statusRes?.ok) setStatus(await statusRes.json());
            if (llmsRes?.ok) {
                const d = await llmsRes.json();
                setLlms(d.llms || []);
            }
            if (statsRes?.ok) setStats(await statsRes.json());
        } catch (error) {
            console.error("Dashboard telemetry failed", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

	if (loading)
		return (
			<div className="flex items-center justify-center p-12">
				<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
			</div>
		);

	return (
		<div className="space-y-8 animate-in fade-in duration-700">
			{/* Hero */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div className="space-y-1">
					<h2 className="text-2xl font-extrabold tracking-tight text-foreground">
						Resonite MCP Server
					</h2>
					<p className="text-sm text-muted-foreground leading-relaxed max-w-xl">
						AI-powered control for Resonite — chat-based OSC, slot/component
						manipulation, inventory management, cloud API, and fleet asset
						pipeline.{" "}
						<a
							href="/help"
							className="text-indigo-400 hover:text-indigo-300 font-medium"
						>
							Setup guide →
						</a>
					</p>
					<div className="flex flex-wrap items-center gap-3 mt-2 text-[11px]">
						<span className="flex items-center gap-1.5 text-muted-foreground">
							<Radio className="h-3 w-3 text-indigo-400" />
							65 tools
						</span>
						<span className="flex items-center gap-1.5 text-muted-foreground">
							<MessageSquare className="h-3 w-3 text-emerald-400" />
							{status?.resonite_running ? "Resonite connected" : "Resonite off"}
						</span>
						<span className="flex items-center gap-1.5 text-muted-foreground">
							<Wifi className="h-3 w-3 text-blue-400" />
							OSC 9000
						</span>
					</div>
				</div>
				<div className="flex items-center gap-2">
					{status?.resonite_installed && !status?.resonite_running && (
						<Button
							size="sm"
							onClick={async () => {
								await fetch(apiUrl("/api/resonite/launch"), { method: "POST" });
								fetchData();
							}}
							className="bg-orange-500 hover:bg-orange-400 text-white font-bold text-xs"
						>
							Launch Resonite
						</Button>
					)}
					<Button
						variant="outline"
						size="sm"
						onClick={fetchData}
						className="gap-1.5 text-xs"
					>
						<RefreshCcw className="h-3 w-3" /> Refresh
					</Button>
				</div>
			</div>

			{/* Presence Alert (if not installed) */}
			{status && !status.resonite_installed && (
				<div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl flex items-center justify-between animate-in slide-in-from-top-4 duration-500">
					<div className="flex items-center gap-4">
						<div className="p-2 bg-blue-500/20 rounded-lg">
							<AlertTriangle className="h-5 w-5 text-blue-400" />
						</div>
						<div>
							<p className="text-sm font-bold text-foreground">
								Resonite not installed
							</p>
							<p className="text-xs text-muted-foreground">
								Install Resonite (free) via Steam to enable OSC, ResoniteLink, and vBot tools
							</p>
						</div>
					</div>
					<Button
						variant="secondary"
						size="sm"
						onClick={() => window.open("steam://install/2519830", "_blank")}
						className="bg-blue-500 text-white hover:bg-blue-400 font-bold"
					>
						Install via Steam
					</Button>
				</div>
			)}

			{/* KPI Cards */}
			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
				<Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-indigo-500/50 transition-all duration-500 group">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
							Worlds
						</CardTitle>
						<Shield className="h-4 w-4 text-emerald-500 transition-transform group-hover:scale-125 duration-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-black text-foreground tracking-tight">
							{stats?.worlds || 0}
						</div>
						<p className="text-[10px] text-muted-foreground mt-1 opacity-50">
							Indexed in RAG
						</p>
					</CardContent>
				</Card>

				<Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-blue-500/50 transition-all duration-500 group">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
							Avatars
						</CardTitle>
						<Cpu className="h-4 w-4 text-blue-500 transition-transform group-hover:rotate-12 duration-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-black text-foreground tracking-tight">
							{stats?.avatars || 0}
						</div>
						<p className="text-[10px] text-muted-foreground mt-1 opacity-50">
							Available
						</p>
					</CardContent>
				</Card>

				<Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-purple-500/50 transition-all duration-500 group">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
							Scripts
						</CardTitle>
						<Activity className="h-4 w-4 text-purple-500 transition-transform group-hover:scale-110 duration-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-black text-foreground tracking-tight">
							{stats?.scripts || 0}
						</div>
						<p className="text-[10px] text-muted-foreground mt-1 opacity-50">
							ProtoFlux available
						</p>
					</CardContent>
				</Card>

				<Card className="border-border bg-card/40 backdrop-blur-md glass hover:border-orange-500/50 transition-all duration-500 group">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
							Sessions
						</CardTitle>
						<Network className="h-4 w-4 text-orange-500 transition-transform group-hover:-translate-y-1 duration-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-black text-foreground tracking-tight">
							{stats?.sessions || 0}
						</div>
						<p className="text-[10px] text-muted-foreground mt-1 opacity-50">
							Active
						</p>
					</CardContent>
				</Card>
			</div>

			<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
				<Card className="col-span-4 border-border bg-card/40 backdrop-blur-md glass">
					<CardHeader className="flex flex-row items-center justify-between">
						<CardTitle className="text-xs font-bold uppercase tracking-widest text-foreground">
							Local LLMs
						</CardTitle>
						<div className="flex gap-1.5">
							<span className="h-2 w-2 rounded-full bg-emerald-500/50" />
						</div>
					</CardHeader>
					<CardContent>
						<div className="space-y-4">
							{llms.length === 0 ? (
								<p className="text-sm text-muted-foreground italic">
									No local LLMs detected...
								</p>
							) : (
								llms.map((llm, i) => (
									<div
										key={i}
										className="flex items-center justify-between border-b border-border/50 pb-3 last:border-0 last:pb-0 group"
									>
										<div className="flex items-center gap-4">
											<div className="p-2.5 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500/20 transition-colors">
												<Cpu className="h-5 w-5 text-indigo-400" />
											</div>
											<div>
												<p className="text-sm font-bold text-foreground">
													{llm.name}
												</p>
												<p className="text-[10px] text-indigo-400/70 font-mono uppercase tracking-wider">
													{llm.provider} • {llm.url}
												</p>
											</div>
										</div>
										<div className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase rounded-sm border border-emerald-500/20">
											Active
										</div>
									</div>
								))
							)}
						</div>
					</CardContent>
				</Card>
				<Card className="col-span-3 border-border bg-card/40 backdrop-blur-md glass">
					<CardHeader>
						<CardTitle className="text-xs font-bold uppercase tracking-widest text-foreground">
							System Status
						</CardTitle>
					</CardHeader>
					<CardContent>
						<div className="space-y-6">
							<div className="flex items-center group">
								<div className="p-2 rounded-md bg-muted border border-border group-hover:border-indigo-500/50 transition-colors">
									<HardDrive className="h-4 w-4 text-indigo-400" />
								</div>
								<div className="ml-4 space-y-1">
									<p className="text-sm font-bold leading-none text-foreground tracking-tight">
										Backend Server
									</p>
									<p className="text-[10px] text-muted-foreground opacity-50">
										FastMCP 3.2+ • Port 10979
									</p>
								</div>
							</div>
							<div className="flex items-center group">
								<div className="p-2 rounded-md bg-muted border border-border group-hover:border-emerald-500/50 transition-colors">
									<Activity className="h-4 w-4 text-emerald-500" />
								</div>
								<div className="ml-4 space-y-1">
									<p className="text-sm font-bold leading-none text-foreground tracking-tight">
										OSC Status
									</p>
									<p className="text-[10px] text-muted-foreground opacity-50">
										Default port 9000 • UDP
									</p>
								</div>
							</div>
							<div className="flex items-center group">
								<div
									className={`p-2 rounded-md bg-muted border border-border transition-colors ${status?.resonite_running ? "group-hover:border-emerald-500/50" : "group-hover:border-rose-500/50"}`}
								>
									<Network
										className={`h-4 w-4 ${status?.resonite_running ? "text-emerald-500" : "text-rose-500"}`}
									/>
								</div>
								<div className="ml-4 space-y-1">
									<p className="text-sm font-bold leading-none text-foreground tracking-tight">
										Resonite
									</p>
									<p
										className={`text-[10px] opacity-50 ${status?.resonite_running ? "text-emerald-500" : "text-rose-400"}`}
									>
										{status?.resonite_running
											? "Running"
											: "Not running"}
									</p>
								</div>
							</div>
							<div className="pt-4 border-t border-border">
								<div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">
									<span>Tool Coverage</span>
									<span className="text-indigo-400">65 tools</span>
								</div>
								<div className="h-1.5 w-full bg-muted rounded-full overflow-hidden border border-border">
									<div className="h-full bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]" style={{ width: "100%" }} />
								</div>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
