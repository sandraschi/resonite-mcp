import { Loader2, Package, RefreshCw, Rocket, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";

interface Spawn {
	id: string;
	kind: string;
	name: string;
	slot_id: string | null;
	detail: string;
	created_at: string;
}

export function SpawnedPage() {
	const [spawns, setSpawns] = useState<Spawn[]>([]);
	const [loading, setLoading] = useState(true);
	const [confirmId, setConfirmId] = useState<string | null>(null);
	const [busyId, setBusyId] = useState<string | null>(null);
	const [message, setMessage] = useState<string | null>(null);

	const fetchSpawns = useCallback(async () => {
		setLoading(true);
		try {
			const res = await fetch(apiUrl("/api/spawns"));
			const data = (await res.json().catch(() => null)) as {
				spawns?: Spawn[];
			} | null;
			setSpawns(data?.spawns || []);
		} catch {
			setSpawns([]);
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		void fetchSpawns();
	}, [fetchSpawns]);

	const handleDelete = async (id: string) => {
		if (confirmId !== id) {
			setConfirmId(id);
			return;
		}
		setConfirmId(null);
		setBusyId(id);
		setMessage(null);
		try {
			const res = await fetch(apiUrl(`/api/spawns/${id}`), {
				method: "DELETE",
			});
			const data = (await res.json().catch(() => null)) as {
				detail?: string;
				slot_id?: string;
			} | null;
			if (!res.ok) throw new Error(data?.detail || "Delete failed");
			setMessage(`Destroyed slot ${data?.slot_id || id}.`);
			await fetchSpawns();
		} catch (error) {
			setMessage(error instanceof Error ? error.message : "Delete failed.");
		} finally {
			setBusyId(null);
		}
	};

	return (
		<div className="space-y-6 page-enter">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-3">
					<div className="bg-rose-500/10 p-2.5 rounded-xl border border-rose-500/20">
						<Rocket className="w-6 h-6 text-rose-400" />
					</div>
					<div>
						<h2 className="text-xl font-bold text-white">Spawned Objects</h2>
						<p className="text-sm text-slate-500">
							Every slot this backend spawned via the webapp — model imports and
							World Builder rooms — with one-click delete for erroneous spawns.
						</p>
					</div>
				</div>
				<button
					onClick={() => void fetchSpawns()}
					disabled={loading}
					title="Refresh spawn list"
					aria-label="Refresh spawn list"
					className="p-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all"
				>
					<RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
				</button>
			</div>

			{message && (
				<p role="status" className="text-xs text-slate-300">
					{message}
				</p>
			)}

			{loading ? (
				<div className="py-20 text-center">
					<Loader2 className="w-8 h-8 text-slate-600 animate-spin mx-auto" />
				</div>
			) : spawns.length === 0 ? (
				<div className="py-20 text-center space-y-3">
					<Package className="w-12 h-12 text-slate-700 mx-auto" />
					<p className="text-slate-400 font-medium">No recorded spawns yet</p>
					<p className="text-xs text-slate-600 max-w-md mx-auto">
						Spawn a model or build a room from the{" "}
						<Link
							to="/world-builder"
							className="text-emerald-400 hover:underline"
						>
							World Builder
						</Link>{" "}
						and it shows up here. Only webapp spawns are tracked — MCP-tool and
						inventory spawns aren&apos;t recorded.
					</p>
				</div>
			) : (
				<div className="flex flex-col gap-3">
					{spawns.map((spawn) => (
						<div
							key={spawn.id}
							className="glass-card rounded-2xl border border-white/[0.05] hover:border-rose-500/20 transition-all p-4 flex flex-col md:flex-row md:items-center gap-3"
						>
							<span
								className={cn(
									"text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded shrink-0 w-fit",
									spawn.kind === "room"
										? "bg-amber-500/15 text-amber-300 border border-amber-500/30"
										: "bg-indigo-500/15 text-indigo-300 border border-indigo-500/30",
								)}
							>
								{spawn.kind}
							</span>
							<div className="flex-1 min-w-0">
								<p className="text-sm font-bold text-white truncate">
									{spawn.name}
								</p>
								<p className="text-[11px] text-slate-500 truncate">
									{spawn.detail || "—"}
								</p>
								<p className="text-[10px] text-slate-600 font-mono mt-0.5">
									{spawn.slot_id || "no slot recorded"} ·{" "}
									{spawn.created_at
										? new Date(spawn.created_at).toLocaleString()
										: ""}
								</p>
							</div>
							<button
								onClick={() => void handleDelete(spawn.id)}
								disabled={busyId === spawn.id || !spawn.slot_id}
								title={
									spawn.slot_id
										? confirmId === spawn.id
											? "Click again to confirm destroy"
											: `Destroy ${spawn.name} in-world`
										: "No world slot recorded — nothing to destroy"
								}
								aria-label={`Delete ${spawn.name}`}
								data-testid={`spawned-delete-${spawn.id}`}
								className={cn(
									"shrink-0 flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border",
									confirmId === spawn.id
										? "bg-rose-500 text-white border-rose-500"
										: "bg-white/[0.05] text-slate-400 border-white/[0.08] hover:border-rose-500/40 hover:text-rose-300",
									"disabled:opacity-40 disabled:cursor-not-allowed",
								)}
							>
								{busyId === spawn.id ? (
									<Loader2 className="w-3.5 h-3.5 animate-spin" />
								) : (
									<Trash2 className="w-3.5 h-3.5" />
								)}
								{confirmId === spawn.id ? "Confirm?" : "Delete"}
							</button>
						</div>
					))}
				</div>
			)}
		</div>
	);
}
