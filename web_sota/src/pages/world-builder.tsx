import { Hammer, Loader2, Play } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";

interface StylePreset {
	id: string;
	name: string;
	description: string;
	swatches: string[];
}

interface SizePreset {
	id: string;
	name: string;
	description: string;
}

interface FurniturePreset {
	id: string;
	name: string;
	description: string;
}

interface Presets {
	styles: StylePreset[];
	sizes: SizePreset[];
	furniture: FurniturePreset[];
	defaults: {
		style: string;
		size: string;
		furniture: string[];
		origin: { x: number; y: number; z: number };
	};
}

interface BuiltPiece {
	name: string;
	ok: boolean;
	slot_id?: string;
	error?: string;
}

interface BuildResult {
	status: string;
	room: string;
	room_slot_id: string;
	style: string;
	pieces_ok: number;
	pieces_total: number;
	warnings: string[];
	pieces: BuiltPiece[];
}

export function WorldBuilderPage() {
	const [presets, setPresets] = useState<Presets | null>(null);
	const [connected, setConnected] = useState<boolean | null>(null);
	const [name, setName] = useState("BuilderRoom");
	const [style, setStyle] = useState("");
	const [size, setSize] = useState("");
	const [furniture, setFurniture] = useState<string[]>([]);
	const [origin, setOrigin] = useState({ x: 0, y: 0, z: 0 });
	const [building, setBuilding] = useState(false);
	const [elapsed, setElapsed] = useState(0);
	const [result, setResult] = useState<BuildResult | null>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		let cancelled = false;
		fetch(apiUrl("/api/world-builder/presets"))
			.then((r) => (r.ok ? r.json() : null))
			.then((data: Presets | null) => {
				if (cancelled || !data) return;
				setPresets(data);
				setStyle((s) => s || data.defaults.style);
				setSize((s) => s || data.defaults.size);
				setFurniture((f) => (f.length ? f : data.defaults.furniture));
				setName((n) => n || "BuilderRoom");
			})
			.catch(() => {});
		fetch(apiUrl("/rl/status"))
			.then((r) => (r.ok ? r.json() : null))
			.then((data) => {
				if (!cancelled && data) setConnected(!!data.connected);
			})
			.catch(() => {
				if (!cancelled) setConnected(false);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	useEffect(() => {
		if (!building) return;
		setElapsed(0);
		const timer = window.setInterval(() => setElapsed((s) => s + 1), 1000);
		return () => window.clearInterval(timer);
	}, [building]);

	const toggleFurniture = (id: string) => {
		setFurniture((prev) =>
			prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id],
		);
	};

	const handleBuild = async () => {
		if (building) return;
		setBuilding(true);
		setResult(null);
		setError(null);
		try {
			const res = await fetch(apiUrl("/api/world-builder/build"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ name, style, size, furniture, origin }),
			});
			const data = (await res.json().catch(() => null)) as
				| (BuildResult & { detail?: string })
				| null;
			if (!res.ok)
				throw new Error(data?.detail || `Build failed (${res.status})`);
			setResult(data as BuildResult);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Build failed.");
		} finally {
			setBuilding(false);
		}
	};

	const activeStyle = presets?.styles.find((s) => s.id === style);

	return (
		<div className="space-y-6 page-enter">
			<div className="flex items-center gap-3">
				<div className="bg-amber-500/10 p-2.5 rounded-xl border border-amber-500/20">
					<Hammer className="w-6 h-6 text-amber-400" />
				</div>
				<div>
					<h2 className="text-xl font-bold text-white">World Builder</h2>
					<p className="text-sm text-slate-500">
						Assemble a furnished room in your live session from a form — every
						piece is a real slot spawned over ResoniteLink, reported back with
						its ID.
					</p>
				</div>
			</div>

			{connected === false && (
				<div className="p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20 text-sm text-amber-300">
					ResoniteLink isn&apos;t connected — builds need a live session.{" "}
					<Link to="/resonite-link" className="font-bold hover:underline">
						Connect on the ResoniteLink page →
					</Link>
				</div>
			)}

			<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<div className="lg:col-span-2 space-y-6">
					<div className="glass-card p-6 space-y-5">
						<div>
							<label
								htmlFor="wb-name"
								className="text-[10px] font-bold text-slate-500 uppercase tracking-widest"
							>
								Room name
							</label>
							<input
								id="wb-name"
								type="text"
								value={name}
								onChange={(e) => setName(e.target.value)}
								maxLength={60}
								className="mt-1.5 w-full bg-black/20 border border-white/[0.08] rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-amber-500/50"
							/>
						</div>

						<div>
							<span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
								Style
							</span>
							<div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1.5">
								{presets?.styles.map((s) => (
									<button
										key={s.id}
										onClick={() => setStyle(s.id)}
										aria-pressed={style === s.id}
										className={cn(
											"text-left p-3 rounded-xl border transition-all",
											style === s.id
												? "bg-amber-500/10 border-amber-500/40"
												: "border-white/[0.06] hover:border-white/15",
										)}
									>
										<span className="text-sm font-bold text-white">
											{s.name}
										</span>
										<span className="block text-[11px] text-slate-500 mt-0.5">
											{s.description}
										</span>
										<span className="flex gap-1 mt-2">
											{s.swatches.map((c) => (
												<span
													key={c}
													className="w-4 h-4 rounded border border-white/20"
													style={{ backgroundColor: c }}
												/>
											))}
										</span>
									</button>
								))}
							</div>
						</div>

						<div>
							<span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
								Size
							</span>
							<div className="grid grid-cols-3 gap-2 mt-1.5">
								{presets?.sizes.map((s) => (
									<button
										key={s.id}
										onClick={() => setSize(s.id)}
										aria-pressed={size === s.id}
										title={s.description}
										className={cn(
											"p-3 rounded-xl border transition-all",
											size === s.id
												? "bg-amber-500/10 border-amber-500/40 text-white"
												: "border-white/[0.06] text-slate-400 hover:border-white/15",
										)}
									>
										<span className="block text-sm font-bold">{s.name}</span>
										<span className="block text-[10px] text-slate-500 mt-0.5">
											{s.description}
										</span>
									</button>
								))}
							</div>
						</div>

						<div>
							<span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
								Furniture
							</span>
							<div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1.5">
								{presets?.furniture.map((f) => (
									<button
										key={f.id}
										onClick={() => toggleFurniture(f.id)}
										aria-pressed={furniture.includes(f.id)}
										className={cn(
											"text-left p-3 rounded-xl border transition-all",
											furniture.includes(f.id)
												? "bg-amber-500/10 border-amber-500/40"
												: "border-white/[0.06] hover:border-white/15",
										)}
									>
										<span className="text-sm font-bold text-white">
											{f.name}
										</span>
										<span className="block text-[11px] text-slate-500 mt-0.5">
											{f.description}
										</span>
									</button>
								))}
							</div>
						</div>

						<div>
							<span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
								Origin (world coordinates)
							</span>
							<div className="grid grid-cols-3 gap-2 mt-1.5">
								{(["x", "y", "z"] as const).map((axis) => (
									<label
										key={axis}
										className="flex items-center gap-2 bg-black/20 border border-white/[0.08] rounded-xl px-3 py-2"
									>
										<span className="text-[10px] font-black text-slate-500 uppercase">
											{axis}
										</span>
										<input
											type="number"
											step="0.5"
											value={origin[axis]}
											onChange={(e) =>
												setOrigin((prev) => ({
													...prev,
													[axis]: Number(e.target.value),
												}))
											}
											aria-label={`Origin ${axis}`}
											className="w-full bg-transparent text-sm text-white focus:outline-none"
										/>
									</label>
								))}
							</div>
							<p className="text-[11px] text-slate-600 mt-1.5">
								Room floor-center in world space. Default builds at the world
								origin — move the pieces in-world afterwards (furniture is
								grabbable).
							</p>
						</div>

						<button
							onClick={handleBuild}
							disabled={building || connected === false || !presets}
							title={
								connected === false
									? "Connect ResoniteLink first"
									: "Build this room in the live session"
							}
							data-testid="world-builder-build"
							className="w-full bg-amber-500 hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed text-black px-4 py-3 rounded-xl text-sm font-black transition-all shadow-lg shadow-amber-500/20 active:scale-[0.99] flex items-center justify-center gap-2"
						>
							{building ? (
								<Loader2 className="w-4 h-4 animate-spin" />
							) : (
								<Play className="w-4 h-4" />
							)}
							{building ? `Building… (${elapsed}s)` : "Build in Resonite"}
						</button>
					</div>
				</div>

				<div className="space-y-4">
					<div className="glass-card p-5">
						<h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
							What happens
						</h3>
						<ul className="text-xs text-slate-400 space-y-1.5 list-disc pl-4 leading-relaxed">
							<li>One parent slot named after your room.</li>
							<li>
								Every wall, floor piece, and furniture part as its own slot with
								BoxMesh + colored material.
							</li>
							<li>Floor and walls get colliders; furniture is grabbable.</li>
							<li>Lamps get real Light components.</li>
							<li>
								{activeStyle
									? `Palette: ${activeStyle.name} — ${activeStyle.description}`
									: "Pick a style to see its palette."}
							</li>
						</ul>
					</div>

					{error && (
						<div
							role="alert"
							className="p-4 rounded-2xl bg-rose-500/5 border border-rose-500/20 text-xs text-rose-400"
						>
							{error}
						</div>
					)}

					{result && (
						<div
							className="glass-card p-5 space-y-3"
							data-testid="world-builder-report"
						>
							<div className="flex items-center justify-between">
								<h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
									Build report
								</h3>
								<span
									className={cn(
										"text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded",
										result.status === "built"
											? "bg-emerald-500/15 text-emerald-400"
											: "bg-amber-500/15 text-amber-400",
									)}
								>
									{result.status} {result.pieces_ok}/{result.pieces_total}
								</span>
							</div>
							<p className="text-xs text-slate-400">
								Room slot{" "}
								<code className="text-slate-200 font-mono">
									{result.room_slot_id}
								</code>
							</p>
							<Link
								to="/spawned"
								className="text-[11px] text-amber-400 hover:underline"
							>
								Manage it on the Spawned page →
							</Link>
							{result.warnings.map((w) => (
								<p key={w} className="text-[11px] text-amber-300/80">
									{w}
								</p>
							))}
							<div className="max-h-64 overflow-y-auto space-y-1 pr-1">
								{result.pieces.map((p) => (
									<div
										key={`${p.name}-${p.slot_id ?? "failed"}`}
										className="flex items-center justify-between gap-2 text-[11px] px-2 py-1 rounded-lg bg-white/[0.02]"
									>
										<span
											className={cn(
												"truncate",
												p.ok ? "text-slate-300" : "text-rose-400",
											)}
											title={p.ok ? p.slot_id : p.error}
										>
											{p.name}
										</span>
										<span className="font-mono text-slate-600 shrink-0">
											{p.ok ? p.slot_id : "failed"}
										</span>
									</div>
								))}
							</div>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
