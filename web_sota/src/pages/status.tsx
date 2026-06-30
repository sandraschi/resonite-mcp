import { apiUrl } from "@/lib/api-base";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Users } from "lucide-react";
import { useMemo } from "react";

interface Session {
	id: string;
	name: string;
	active_user_count: number;
}

async function fetchPlatform() {
	const r = await fetch(apiUrl("/api/platform"));
	if (!r.ok) throw new Error("Failed to fetch platform");
	return r.json();
}

async function fetchSessions() {
	const r = await fetch(apiUrl("/api/sessions"));
	if (!r.ok) throw new Error("Failed to fetch sessions");
	return r.json();
}

async function startResoniteAPI() {
	const r = await fetch(apiUrl("/api/start"), { method: "POST" });
	if (!r.ok) throw new Error("Failed to start Resonite");
	return r.json();
}

export function Status() {
	const { data: platform, refetch: refetchPlatform } = useQuery({
		queryKey: ["platform"],
		queryFn: fetchPlatform,
		refetchInterval: 60_000,
	});

	const { data: sessions, refetch: refetchSessions } = useQuery<Session[]>({
		queryKey: ["sessions"],
		queryFn: fetchSessions,
		refetchInterval: 30_000,
	});

	const { mutate: startResonite } = useMutation({
		mutationFn: startResoniteAPI,
		onSuccess: () => {
			setTimeout(() => {
				refetchPlatform();
				refetchSessions();
			}, 3000);
		},
	});

	const isPlatformDown = !platform?.os;

	// Fix react-hooks/purity by using static timestamps for mock logs
	const mockLogs = useMemo(
		() => [
			{
				type: "INFO",
				color: "text-indigo-400/50",
				time: "2026-02-23T15:00:00Z",
				msg: "OSC Pulse check passed: Latency 15ms",
			},
			{
				type: "INFO",
				color: "text-indigo-400/50",
				time: "2026-02-23T14:59:30Z",
				msg: "Internal bridge heartbeat active",
			},
			{
				type: "OK",
				color: "text-emerald-400/50",
				time: "2026-02-23T14:59:00Z",
				msg: "SOTA UI Module successfully glommed on",
			},
		],
		[],
	);

	return (
		<div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
			{/* Dashboard stats integration placeholder */}
			<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div className="glass p-6 rounded-2xl border border-border/50">
					<h3 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-4">
						Core Resonance
					</h3>
					<div className="space-y-4">
						<div className="flex justify-between items-center">
							<span className="text-xs text-foreground/70">
								Platform Engine
							</span>
							<span
								className={
									isPlatformDown
										? "text-red-400 font-mono text-xs"
										: "text-emerald-400 font-mono text-xs"
								}
							>
								{isPlatformDown ? "DISCONNECTED" : "OPERATIONAL"}
							</span>
						</div>
						<div className="h-1 bg-muted rounded-full overflow-hidden">
							<div
								className={
									isPlatformDown
										? "h-full bg-red-400 w-full"
										: "h-full bg-emerald-400 w-full"
								}
							/>
						</div>
						<button
							onClick={() => startResonite()}
							className="w-full py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold uppercase tracking-widest hover:bg-indigo-500/20 transition-colors"
						>
							Reconnect Core
						</button>
					</div>
				</div>
			</div>

			{sessions?.map((session, i) => (
				<div
					key={i}
					className="group p-3 rounded-lg bg-muted/30 border border-border/50 hover:border-indigo-500/30 transition-all duration-300"
				>
					<div className="flex items-start justify-between mb-1">
						<div className="font-bold text-foreground text-xs leading-tight flex items-center gap-2">
							{session.name}
							<span className="text-[8px] bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded tracking-tighter uppercase font-black">
								LIVE
							</span>
						</div>
						<span className="text-[8px] text-muted-foreground font-mono opacity-50 group-hover:opacity-100 transition-opacity">
							{session.id.slice(0, 8)}
						</span>
					</div>
					<div className="mt-2 flex items-center justify-between text-[9px] uppercase font-bold tracking-[0.1em]">
						<div className="flex items-center gap-1.5 text-muted-foreground">
							<Users className="h-3 w-3 opacity-50" />
							<span>{session.active_user_count} Users</span>
						</div>
						<div className="flex items-center gap-1.5 text-emerald-500/80">
							<div className="h-1 w-1 rounded-full bg-emerald-500" />
							OK
						</div>
					</div>
				</div>
			))}
			{/* ... */}
			{/* Health Logs Trace (Placeholder/Mock) */}
			<div className="mt-8 bg-black/40 rounded-2xl border border-border/50 p-6 backdrop-blur-md">
				<div className="flex items-center justify-between mb-4">
					<h3 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground italic">
						Hardware Event Horizon
					</h3>
					<div className="flex gap-1">
						<div className="h-1 w-1 rounded-full bg-indigo-500" />
						<div className="h-1 w-1 rounded-full bg-indigo-500/50" />
						<div className="h-1 w-1 rounded-full bg-indigo-500/20" />
					</div>
				</div>
				<div className="space-y-2 font-mono text-[10px]">
					{mockLogs.map((log, i) => (
						<div
							key={i}
							className="flex gap-4 p-2 rounded hover:bg-white/[0.02] transition-colors"
						>
							<span className={log.color}>[{log.type}]</span>
							<span className="text-muted-foreground">{log.time}</span>
							<span className="text-foreground">{log.msg}</span>
						</div>
					))}
				</div>
			</div>
		</div>
	);
}
