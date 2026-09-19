import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Inbox as InboxIcon, RefreshCw } from "lucide-react";
import { useState } from "react";
import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";

interface LogEntry {
	id: string;
	timestamp: string;
	level: string;
	kind: string;
	detail: string;
}

const ATTENTION_LEVELS = ["WARNING", "ERROR", "CRITICAL"];

async function fetchAttention(): Promise<LogEntry[]> {
	const r = await fetch(apiUrl("/api/logs?limit=200"));
	if (!r.ok) throw new Error("Failed to fetch logs");
	const d = await r.json();
	return (d.entries ?? []).filter((e: LogEntry) =>
		ATTENTION_LEVELS.includes(e.level),
	);
}

export function Inbox() {
	const [refreshTick, setRefreshTick] = useState(0);
	const { data, isLoading, isError, refetch, isRefetching } = useQuery({
		queryKey: ["inbox", refreshTick],
		queryFn: fetchAttention,
	});

	const items = data ?? [];

	return (
		<div className="space-y-8 animate-in fade-in duration-700">
			<div className="relative group">
				<div className="absolute -inset-1 bg-gradient-to-r from-amber-500/20 to-red-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000" />
				<div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6 bg-card/40 backdrop-blur-xl border border-white/10 p-6 rounded-xl glass-card">
					<div className="flex items-center gap-5">
						<div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-inner">
							<InboxIcon
								className="w-8 h-8 text-amber-400"
								aria-hidden="true"
							/>
						</div>
						<div>
							<h2 className="text-3xl font-black tracking-tighter text-foreground">
								Inbox
							</h2>
							<p className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1 flex items-center gap-2">
								<span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
								{items.length > 0
									? `${items.length} warnings or errors need attention`
									: "Backend warnings and errors land here"}
							</p>
						</div>
					</div>

					<button
						type="button"
						onClick={() => {
							setRefreshTick((t) => t + 1);
							void refetch();
						}}
						disabled={isLoading || isRefetching}
						title="Refresh inbox"
						className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 text-amber-300 text-xs font-bold uppercase tracking-widest transition-all disabled:opacity-50"
					>
						<RefreshCw
							className={cn("w-4 h-4", isRefetching && "animate-spin")}
						/>
						{isRefetching ? "Refreshing..." : "Refresh"}
					</button>
				</div>
			</div>

			<div className="min-h-[300px]">
				{isLoading ? (
					<div className="flex items-center justify-center py-20 opacity-60">
						<RefreshCw className="w-8 h-8 animate-spin text-amber-500" />
					</div>
				) : isError ? (
					<div className="glass-card p-12 flex flex-col items-center justify-center text-center gap-4 border-red-500/20 bg-red-500/5">
						<p className="text-red-400 font-bold">Inbox unavailable</p>
						<p className="text-sm text-slate-400">
							Could not reach the log API. Is the backend running?
						</p>
					</div>
				) : items.length === 0 ? (
					<div className="flex flex-col items-center justify-center py-20 bg-card/20 backdrop-blur-sm border border-dashed border-white/10 rounded-2xl gap-4">
						<InboxIcon className="w-12 h-12 text-slate-700" />
						<div className="text-center">
							<p className="text-sm font-bold text-foreground">All quiet</p>
							<p className="text-xs text-slate-400 mt-1">
								No warnings or errors in the recent log buffer.
							</p>
						</div>
						<a
							href="/logs"
							className="text-xs text-indigo-400 font-bold hover:underline"
						>
							VIEW FULL LOGS
						</a>
					</div>
				) : (
					<div className="grid gap-3">
						{items.map((entry) => (
							<div
								key={entry.id}
								className={cn(
									"glass-card border rounded-2xl p-5 transition-all",
									entry.level === "ERROR"
										? "border-red-500/30 bg-red-500/[0.03]"
										: "border-amber-500/20 bg-amber-500/[0.02]",
								)}
							>
								<div className="flex items-center gap-3 mb-2">
									<AlertTriangle
										className={cn(
											"w-4 h-4",
											entry.level === "ERROR"
												? "text-red-400"
												: "text-amber-400",
										)}
									/>
									<span
										className={cn(
											"text-[10px] font-black uppercase tracking-widest",
											entry.level === "ERROR"
												? "text-red-400"
												: "text-amber-400",
										)}
									>
										{entry.level}
									</span>
									<span className="text-[10px] font-mono text-slate-500">
										{entry.kind}
									</span>
									<span className="text-[10px] font-mono text-slate-600 ml-auto">
										{entry.timestamp}
									</span>
								</div>
								<p className="text-sm text-slate-200 font-mono break-all">
									{entry.detail}
								</p>
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	);
}
