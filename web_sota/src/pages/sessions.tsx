import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";
import { useQuery } from "@tanstack/react-query";
import {
	ChevronLeft,
	ChevronRight,
	Globe2,
	ImageIcon,
	Loader2,
	Lock,
	RefreshCw,
	Search,
	Unlock,
	Users,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

interface Session {
	sessionId: string;
	name?: string;
	description?: string | null;
	tags?: string[];
	thumbnailUrl?: string | null;
	activeUsers?: number;
	totalJoinedUsers?: number;
	maxUsers?: number;
	hostUsername?: string;
	accessLevel?: string;
	headlessHost?: boolean;
	lastUpdate?: string;
	correspondingWorldId?: { recordId?: string; ownerId?: string } | null;
}

const PAGE_SIZE = 25;

type SortKey = "users" | "name" | "updated";

/** Session names carry Resonite rich-text tags (<color=...>, <size=...>). */
function plainName(name: string | undefined): string {
	return (name ?? "").replace(/<[^>]*>/g, "").trim();
}

function accessOpen(accessLevel: string | undefined): boolean {
	return accessLevel === "Anyone";
}

async function fetchSessions(): Promise<Session[]> {
	const r = await fetch(apiUrl("/api/sessions"));
	if (!r.ok) throw new Error("Failed to fetch sessions");
	return r.json() as Promise<Session[]>;
}

export function Sessions() {
	const [search, setSearch] = useState("");
	const [access, setAccess] = useState("All");
	const [sort, setSort] = useState<SortKey>("users");
	const [page, setPage] = useState(1);

	const { data, isLoading, isError, refetch, isRefetching } = useQuery({
		queryKey: ["sessions"],
		queryFn: fetchSessions,
		refetchInterval: 30_000,
	});

	const accessLevels = useMemo(() => {
		const levels = new Set<string>();
		for (const s of data ?? []) {
			if (s.accessLevel) levels.add(s.accessLevel);
		}
		return ["All", ...[...levels].sort()];
	}, [data]);

	const worldCount = useMemo(() => {
		const ids = new Set<string>();
		for (const s of data ?? []) {
			const id = s.correspondingWorldId?.recordId;
			if (id) ids.add(id);
		}
		return ids.size;
	}, [data]);

	const filtered = useMemo(() => {
		const q = search.trim().toLowerCase();
		let rows = (data ?? []).filter((s) => {
			if (access !== "All" && s.accessLevel !== access) return false;
			if (!q) return true;
			const hay = [
				plainName(s.name),
				s.hostUsername ?? "",
				s.sessionId,
				(s.tags ?? []).join(" "),
				s.correspondingWorldId?.recordId ?? "",
			]
				.join(" ")
				.toLowerCase();
			return hay.includes(q);
		});
		rows = [...rows].sort((a, b) => {
			if (sort === "name")
				return plainName(a.name).localeCompare(plainName(b.name));
			if (sort === "updated")
				return (
					Date.parse(b.lastUpdate ?? "") - Date.parse(a.lastUpdate ?? "")
				);
			return (b.activeUsers ?? 0) - (a.activeUsers ?? 0);
		});
		return rows;
	}, [data, search, access, sort]);

	useEffect(() => {
		setPage(1);
	}, [search, access, sort]);

	const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
	const safePage = Math.min(page, pageCount);
	const pageRows = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

	const pageWindow = useMemo(() => {
		const start = Math.max(1, Math.min(safePage - 2, pageCount - 4));
		return Array.from({ length: Math.min(5, pageCount) }, (_, i) => start + i);
	}, [safePage, pageCount]);

	return (
		<div className="space-y-8 animate-in fade-in duration-700">
			{/* Header */}
			<div className="relative group">
				<div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000" />
				<div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6 bg-card/40 backdrop-blur-xl border border-white/10 p-6 rounded-xl glass-card">
					<div className="flex items-center gap-5">
						<div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-inner group-hover:rotate-12 transition-transform duration-500">
							<Globe2 className="w-8 h-8 text-indigo-400" aria-hidden="true" />
						</div>
						<div>
							<h2 className="text-3xl font-black tracking-tighter text-foreground">
								World <span className="text-indigo-400">Sessions</span>
							</h2>
							<p className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1 flex items-center gap-2">
								<span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" />
								{data ? (
									<>
										{data.length} sessions • {worldCount} worlds • live
										from the Resonite cloud
									</>
								) : (
									"Live public sessions from the Resonite cloud"
								)}
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
						{isRefetching ? "Refreshing..." : "Refresh"}
					</button>
				</div>
			</div>

			{/* Filter / sort bar */}
			<div className="flex flex-col lg:flex-row gap-3">
				<div className="relative flex-1">
					<div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
						<Search
							className="h-4 w-4 text-muted-foreground"
							aria-hidden="true"
						/>
					</div>
					<input
						type="search"
						value={search}
						onChange={(e) => setSearch(e.target.value)}
						placeholder="Filter by name, host, tag, world ID..."
						className="w-full bg-card/40 backdrop-blur-md border border-white/10 focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 rounded-xl py-3 pl-12 pr-4 text-sm font-medium transition-all outline-none"
						aria-label="Filter sessions"
					/>
				</div>
				<div className="flex gap-3">
					<select
						value={access}
						onChange={(e) => setAccess(e.target.value)}
						className="bg-card/40 border border-white/10 rounded-xl px-4 py-3 text-sm font-medium text-slate-200 outline-none focus:border-indigo-500/50"
						aria-label="Filter by access level"
					>
						{accessLevels.map((level) => (
							<option key={level} value={level} className="bg-slate-900">
								{level === "All" ? "All access levels" : level}
							</option>
						))}
					</select>
					<select
						value={sort}
						onChange={(e) => setSort(e.target.value as SortKey)}
						className="bg-card/40 border border-white/10 rounded-xl px-4 py-3 text-sm font-medium text-slate-200 outline-none focus:border-indigo-500/50"
						aria-label="Sort sessions"
					>
						<option value="users" className="bg-slate-900">
							Most users
						</option>
						<option value="updated" className="bg-slate-900">
							Recently updated
						</option>
						<option value="name" className="bg-slate-900">
							Name A–Z
						</option>
					</select>
				</div>
			</div>

			{/* Content */}
			<div className="min-h-[400px] space-y-4">
				{isLoading ? (
					<div className="flex flex-col items-center justify-center py-20 opacity-60 space-y-4">
						<Loader2 className="w-10 h-10 animate-spin text-indigo-500" />
						<p className="text-xs font-bold uppercase tracking-[0.3em] text-slate-400">
							Loading sessions...
						</p>
					</div>
				) : isError ? (
					<div className="glass-card p-12 flex flex-col items-center justify-center text-center gap-4 border-red-500/20 bg-red-500/5">
						<div className="p-4 rounded-full bg-red-500/10 border border-red-500/20">
							<Globe2 className="w-8 h-8 text-red-400 opacity-50" />
						</div>
						<div>
							<p className="text-red-400 font-bold">Sessions unavailable</p>
							<p className="text-sm text-slate-400 mt-1">
								The Resonite cloud API could not be reached. Try refreshing.
							</p>
						</div>
					</div>
				) : (
					<>
						<div className="grid gap-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
							{pageRows.map((s) => {
								const name = plainName(s.name) || "Unnamed Session";
								const open = accessOpen(s.accessLevel);
								return (
									<div
										key={s.sessionId}
										className="group flex flex-col md:flex-row md:items-center gap-4 p-5 glass-card border border-white/10 rounded-2xl hover:border-violet-500/50 hover:bg-card/60 transition-all duration-300"
									>
										<div className="flex items-center gap-4 flex-1 min-w-0">
											<div className="relative w-16 h-16 rounded-xl overflow-hidden border border-white/10 bg-slate-900 flex-shrink-0 flex items-center justify-center">
												<ImageIcon className="w-6 h-6 text-slate-600" />
												{s.thumbnailUrl && (
													<img
														src={s.thumbnailUrl}
														alt=""
														loading="lazy"
														onError={(e) => {
															e.currentTarget.style.display = "none";
														}}
														className="absolute inset-0 w-full h-full object-cover"
													/>
												)}
											</div>
											<div className="space-y-1 min-w-0 flex-1">
												<h3
													className="text-sm font-bold text-slate-100 tracking-tight truncate"
													title={name}
												>
													{name}
												</h3>
												{s.description && (
													<p
														className="text-xs text-slate-400 line-clamp-2"
														title={s.description}
													>
														{s.description}
													</p>
												)}
												<div className="flex items-center gap-2 text-xs font-semibold text-slate-400 flex-wrap">
													<span
														className={cn(
															"inline-flex items-center gap-1 px-2 py-0.5 rounded-md border text-[10px] font-bold uppercase tracking-wider",
															open
																? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
																: "bg-amber-500/10 border-amber-500/20 text-amber-400",
														)}
													>
														{open ? (
															<Unlock className="w-3 h-3" />
														) : (
															<Lock className="w-3 h-3" />
														)}
														{s.accessLevel ?? "Unknown"}
													</span>
													<span>{s.hostUsername ?? "Unknown host"}</span>
													{(s.tags ?? []).slice(0, 3).map((tag) => (
														<span
															key={tag}
															className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-slate-400"
														>
															{tag}
														</span>
													))}
												</div>
											</div>
										</div>

										<div className="flex items-center gap-4 shrink-0">
											<div
												className={cn(
													"flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono text-xs font-bold",
													(s.activeUsers ?? 0) > 0
														? "bg-violet-500/10 border-violet-500/30 text-violet-300"
														: "bg-white/5 border-white/10 text-slate-400",
												)}
												title={`${s.totalJoinedUsers ?? 0} total joins`}
											>
												<Users className="w-3.5 h-3.5" />
												<span>{s.activeUsers ?? 0}</span>
												<span className="opacity-40">/</span>
												<span className="opacity-70">{s.maxUsers ?? "?"}</span>
											</div>

											<a
												href={`resonite:///join/${s.sessionId}`}
												className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600/20 hover:bg-violet-600/40 border border-violet-500/30 text-violet-100 text-xs font-black uppercase tracking-widest transition-all active:scale-95"
												title={`Join ${name} directly in Resonite`}
											>
												<Globe2 className="w-3.5 h-3.5" />
												Join
											</a>
										</div>
									</div>
								);
							})}
							{filtered.length === 0 && (
								<div className="flex flex-col items-center justify-center py-20 bg-card/20 backdrop-blur-sm border border-dashed border-white/10 rounded-2xl gap-4">
									<Globe2 className="w-12 h-12 text-slate-700" />
									<div className="text-center">
										<p className="text-sm font-bold text-foreground">
											No sessions match
										</p>
										<p className="text-xs text-slate-400 mt-1">
											Nothing matches the current search and filters.
										</p>
									</div>
									<button
										onClick={() => {
											setSearch("");
											setAccess("All");
										}}
										className="text-xs text-indigo-400 font-bold hover:underline"
									>
										RESET FILTERS
									</button>
								</div>
							)}
						</div>

						{/* Pagination */}
						{pageCount > 1 && (
							<div className="flex items-center justify-between pt-2">
								<p className="text-xs text-slate-400">
									Showing {(safePage - 1) * PAGE_SIZE + 1}–
									{Math.min(safePage * PAGE_SIZE, filtered.length)} of{" "}
									{filtered.length}
								</p>
								<div className="flex items-center gap-1">
									<button
										onClick={() => setPage((p) => Math.max(1, p - 1))}
										disabled={safePage === 1}
										aria-label="Previous page"
										className="p-2 rounded-lg border border-white/10 text-slate-300 hover:bg-white/5 disabled:opacity-30 transition-all"
									>
										<ChevronLeft className="w-4 h-4" />
									</button>
									{pageWindow.map((p) => (
										<button
											key={p}
											onClick={() => setPage(p)}
											aria-label={`Page ${p}`}
											aria-current={p === safePage ? "page" : undefined}
											className={cn(
												"min-w-9 px-2 py-1.5 rounded-lg border text-xs font-bold transition-all",
												p === safePage
													? "bg-indigo-500/20 border-indigo-500/40 text-indigo-200"
													: "border-white/10 text-slate-400 hover:bg-white/5",
											)}
										>
											{p}
										</button>
									))}
									<button
										onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
										disabled={safePage === pageCount}
										aria-label="Next page"
										className="p-2 rounded-lg border border-white/10 text-slate-300 hover:bg-white/5 disabled:opacity-30 transition-all"
									>
										<ChevronRight className="w-4 h-4" />
									</button>
								</div>
							</div>
						)}
					</>
				)}
			</div>
		</div>
	);
}
