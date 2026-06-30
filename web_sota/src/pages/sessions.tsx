import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";
import { useQuery } from "@tanstack/react-query";
import {
	Globe2,
	Loader2,
	Lock,
	RefreshCw,
	Search,
	Unlock,
	Users,
} from "lucide-react";
import { useState } from "react";

interface Session {
	sessionId: string;
	name?: string;
	activeUsers?: number;
	maxUsers?: number;
	hostUsername?: string;
	sessionAccessLevel?: string;
	universeId?: string;
}

async function fetchSessions(name: string): Promise<Session[]> {
	const params = new URLSearchParams();
	if (name) params.set("name", name);
	const r = await fetch(apiUrl(`/api/sessions?${params}`));
	if (!r.ok) throw new Error("Failed to fetch sessions");
	return r.json() as Promise<Session[]>;
}

export function Sessions() {
	const [search, setSearch] = useState("");
	const [query, setQuery] = useState("");

	const { data, isLoading, isError, refetch, isRefetching } = useQuery({
		queryKey: ["sessions", query],
		queryFn: () => fetchSessions(query),
		refetchInterval: 30_000,
	});

	return (
		<div className="space-y-8 animate-in fade-in duration-700">
			{/* Header Section */}
			<div className="relative group">
				<div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000" />
				<div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6 bg-card/40 backdrop-blur-xl border border-white/10 p-6 rounded-xl glass-card">
					<div className="flex items-center gap-5">
						<div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-inner group-hover:rotate-12 transition-transform duration-500">
							<Globe2 className="w-8 h-8 text-indigo-400" aria-hidden="true" />
						</div>
						<div>
							<h2 className="text-3xl font-black tracking-tighter text-foreground bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/60">
								World <span className="text-indigo-400">Sessions</span>
							</h2>
							<p className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1 opacity-70 flex items-center gap-2">
								<span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" />
								Neural Session Stream • Real-time Consensus
							</p>
						</div>
					</div>

					<button
						onClick={() => refetch()}
						disabled={isLoading || isRefetching}
						title="Refresh Sessions"
						className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-300 text-xs font-bold uppercase tracking-widest transition-all disabled:opacity-50"
					>
						<RefreshCw
							className={cn("w-4 h-4", isRefetching && "animate-spin")}
						/>
						{isRefetching ? "Syncing..." : "Sync Data"}
					</button>
				</div>
			</div>

			{/* Search Section */}
			<div className="relative group">
				<div className="flex gap-3">
					<div className="relative flex-1 group">
						<div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
							<Search
								className="h-4 w-4 text-muted-foreground group-focus-within:text-indigo-400 transition-colors"
								aria-hidden="true"
							/>
						</div>
						<input
							type="search"
							value={search}
							onChange={(e) => setSearch(e.target.value)}
							onKeyDown={(e) => e.key === "Enter" && setQuery(search)}
							placeholder="Search active world sessions..."
							title="Search Sessions"
							className="w-full bg-card/40 backdrop-blur-md border border-white/10 focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 rounded-xl py-4 pl-12 pr-4 text-sm font-medium transition-all outline-none"
							aria-label="Search sessions by name"
						/>
					</div>
					<button
						onClick={() => setQuery(search)}
						className="px-6 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm tracking-wide transition-all shadow-lg shadow-indigo-500/20 active:scale-95 border border-indigo-400/30"
						title="Execute Search"
					>
						Search
					</button>
				</div>
			</div>

			{/* Content Area */}
			<div className="min-h-[400px] space-y-4">
				{isLoading ? (
					<div className="flex flex-col items-center justify-center py-20 grayscale opacity-50 space-y-4">
						<Loader2 className="w-10 h-10 animate-spin text-indigo-500" />
						<p className="text-[10px] font-bold uppercase tracking-[0.3em] text-slate-500">
							Retrieving Neural Flux...
						</p>
					</div>
				) : isError ? (
					<div className="glass-card p-12 flex flex-col items-center justify-center text-center gap-4 border-red-500/20 bg-red-500/5">
						<div className="p-4 rounded-full bg-red-500/10 border border-red-500/20">
							<Globe2 className="w-8 h-8 text-red-400 opacity-50" />
						</div>
						<div>
							<p className="text-red-400 font-bold">
								Network Partition Detected
							</p>
							<p className="text-sm text-slate-500 mt-1">
								Failed to establish connection with Resonite API
							</p>
						</div>
					</div>
				) : (
					<div className="grid gap-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
						{data?.map((s) => (
							<div
								key={s.sessionId}
								className="group flex flex-col md:flex-row md:items-center justify-between p-5 glass-card border border-white/10 rounded-2xl hover:border-violet-500/50 hover:bg-card/60 transition-all duration-300 gap-4"
							>
								<div className="flex items-center gap-4 flex-1 min-w-0">
									<div
										className={cn(
											"p-2.5 rounded-xl border flex items-center justify-center shrink-0",
											s.sessionAccessLevel === "Public"
												? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
												: "bg-amber-500/10 border-amber-500/20 text-amber-400",
										)}
									>
										{s.sessionAccessLevel === "Public" ? (
											<Unlock className="w-5 h-5" />
										) : (
											<Lock className="w-5 h-5" />
										)}
									</div>
									<div className="space-y-1 truncate">
										<h3 className="text-sm font-bold text-slate-100 uppercase tracking-tight truncate">
											{s.name || "Unnamed Session"}
										</h3>
										<div className="flex items-center gap-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
											<span>{s.hostUsername ?? "Unknown Agent"}</span>
											<span className="h-1 w-1 rounded-full bg-slate-700" />
											<span className="font-mono text-slate-600 truncate">
												{s.sessionId.split("-")[0]}…
											</span>
										</div>
									</div>
								</div>

								<div className="flex items-center gap-4 shrink-0">
									<div
										className={cn(
											"flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono text-[10px] font-bold transition-all",
											(s.activeUsers ?? 0) > 0
												? "bg-violet-500/10 border-violet-500/30 text-violet-400 shadow-[0_0_15px_rgba(99,102,241,0.1)]"
												: "bg-slate-700/20 border-white/5 text-slate-600",
										)}
									>
										<Users className="w-3 h-3" />
										<span>{s.activeUsers ?? 0}</span>
										<span className="opacity-40">/</span>
										<span className="opacity-60">{s.maxUsers ?? "?"}</span>
									</div>

									<a
										href={`resonite:///join/${s.sessionId}`}
										className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600/20 hover:bg-violet-600/40 border border-violet-500/30 text-violet-100 text-[10px] font-black uppercase tracking-widest transition-all active:scale-95"
										title={`Join ${s.name} directly in Resonite`}
									>
										<Globe2 className="w-3.5 h-3.5" />
										Join
									</a>
								</div>
							</div>
						))}
						{data?.length === 0 && (
							<div className="flex flex-col items-center justify-center py-20 bg-card/20 backdrop-blur-sm border border-dashed border-white/10 rounded-2xl gap-4">
								<Globe2 className="w-12 h-12 text-slate-800" />
								<div className="text-center">
									<p className="text-sm font-bold text-foreground">
										No Sessions Detected
									</p>
									<p className="text-[11px] text-muted-foreground uppercase tracking-tight mt-1">
										The resonance grid is silent for query:{" "}
										<span className="text-indigo-400">{query || "ALL"}</span>
									</p>
								</div>
								<button
									onClick={() => {
										setSearch("");
										setQuery("");
									}}
									className="text-xs text-indigo-400 font-bold hover:underline"
								>
									RESET FILTERS
								</button>
							</div>
						)}
					</div>
				)}
			</div>
		</div>
	);
}
