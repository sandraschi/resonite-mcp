import {
	Box,
	Download,
	ExternalLink,
	LayoutGrid,
	List,
	Loader2,
	Search,
	ShoppingBag,
	Sparkles,
	Star,
	Users,
	Wrench,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api-base";

interface MarketplaceItem {
	id: string;
	name: string;
	author: string;
	description: string;
	price: string;
	rating: number;
	downloads: number;
	thumbnail?: string;
	category: string;
	tags: string[];
}

const MOCK_ITEMS: MarketplaceItem[] = [
	{
		id: "1",
		name: "Sota Avatar Base V4",
		author: "ResoniteSOTA",
		description:
			"Premium avatar base with full facial tracking and ProtoFlux logic.",
		price: "Free",
		rating: 4.9,
		downloads: 1240,
		category: "Avatars",
		tags: ["SOTA", "Facial Tracking", "SDK"],
	},
	{
		id: "2",
		name: "ProtoFlux Debugger Pro",
		author: "LogicMaster",
		description: "Advanced in-world debugger for complex ProtoFlux chains.",
		price: "Free",
		rating: 4.8,
		downloads: 850,
		category: "Tools",
		tags: ["Utility", "Scripting", "Debug"],
	},
	{
		id: "3",
		name: "Nebula Skybox Pack",
		author: "WorldSmith",
		description: "Collection of 8K high-detail space skyboxes.",
		price: "Free",
		rating: 4.7,
		downloads: 3200,
		category: "Worlds",
		tags: ["Skybox", "Space", "Art"],
	},
	{
		id: "4",
		name: "OSC Relay Node",
		author: "SandraS",
		description: "Connect internal Resonite events to external OSC apps.",
		price: "Free",
		rating: 5.0,
		downloads: 410,
		category: "Tools",
		tags: ["OSC", "Network", "Bridge"],
	},
];

type InstallState = {
	status: "installing" | "done" | "error";
	message: string;
};

interface AssetSource {
	name: string;
	url: string;
	blurb: string;
}

interface SourceGroup {
	title: string;
	// Icon is a lucide component type
	Icon: typeof Wrench;
	note?: string;
	items: AssetSource[];
}

// Verified 2026-09-20: GitHub entries checked live via the API,
// homepages are the sites' canonical roots (no deep links to rot).
const SOURCE_GROUPS: SourceGroup[] = [
	{
		title: "Tools & mods",
		Icon: Wrench,
		items: [
			{
				name: "ResoniteUnityExporter",
				url: "https://github.com/Phylliida/ResoniteUnityExporter",
				blurb:
					"Community Unity plugin: export avatars or worlds from Unity into Resonite.",
			},
			{
				name: "ResoniteModLoader",
				url: "https://github.com/resonite-modding-group/ResoniteModLoader",
				blurb: "Mod loader using Resonite's built-in plugin system.",
			},
			{
				name: "Resolute",
				url: "https://github.com/Gawdl3y/Resolute",
				blurb: "Mod manager GUI for installing and updating Resonite mods.",
			},
			{
				name: "Unofficial Resonite Docs",
				url: "https://github.com/FlippedCodes/Unofficial-Resonite-Docs",
				blurb: "Community docs: desktop keybinds, ProtoFlux, gameplay guides.",
			},
			{
				name: "Avatar-Toolkit",
				url: "https://github.com/teamneoneko/Avatar-Toolkit",
				blurb: "Blender addon for preparing avatars (archived, still useful).",
			},
		],
	},
	{
		title: "Models & avatars",
		Icon: Box,
		note: "Check each asset's license before uploading — downloadable doesn't mean free to use.",
		items: [
			{
				name: "Booth",
				url: "https://booth.pm",
				blurb:
					"Huge creator market for VRM avatars, outfits, and world assets.",
			},
			{
				name: "VRoid Hub",
				url: "https://hub.vroid.com",
				blurb: "Free VRM avatars to download and wear.",
			},
			{
				name: "poly.pizza",
				url: "https://poly.pizza",
				blurb: "Free low-poly CC0 models, searchable and downloadable.",
			},
			{
				name: "Sketchfab",
				url: "https://sketchfab.com",
				blurb: "Large 3D library; many models offer downloads.",
			},
			{
				name: "Quaternius",
				url: "https://quaternius.com",
				blurb: "Free CC0 stylized game assets.",
			},
			{
				name: "Kenney",
				url: "https://kenney.nl",
				blurb: "Free game assets, a longtime community staple.",
			},
		],
	},
	{
		title: "Community & learning",
		Icon: Users,
		items: [
			{
				name: "Discord",
				url: "https://discord.gg/resonite",
				blurb: "Main community hub with help channels.",
			},
			{
				name: "Wiki",
				url: "https://wiki.resonite.com/Main_Page",
				blurb: "Official wiki: tutorials, components, guides.",
			},
			{
				name: "Steam guides",
				url: "https://steamcommunity.com/app/2519830/guides/",
				blurb: "Player-written setup, avatar, and modding guides.",
			},
			{
				name: "YouTube @resoniteapp",
				url: "https://www.youtube.com/@resoniteapp",
				blurb: "Official channel: trailers, updates, showcases.",
			},
		],
	},
];

export function MarketplacePage() {
	const [searchQuery, setSearchQuery] = useState("");
	const [activeCategory, setActiveCategory] = useState("All");
	const [view, setView] = useState<"cards" | "list">(() => {
		try {
			return localStorage.getItem("marketplace-view") === "list"
				? "list"
				: "cards";
		} catch {
			return "cards";
		}
	});
	const [installs, setInstalls] = useState<Record<string, InstallState>>({});
	const [resoniteRunning, setResoniteRunning] = useState<boolean | null>(null);

	useEffect(() => {
		let cancelled = false;
		fetch(apiUrl("/api/status"))
			.then((r) => (r.ok ? r.json() : null))
			.then((d) => {
				if (!cancelled && d) setResoniteRunning(!!d.resonite_running);
			})
			.catch(() => {
				if (!cancelled) setResoniteRunning(false);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	const switchView = (next: "cards" | "list") => {
		setView(next);
		try {
			localStorage.setItem("marketplace-view", next);
		} catch {
			// ignore storage errors
		}
	};

	const handleInstall = async (item: MarketplaceItem) => {
		if (installs[item.id]?.status === "installing") return;
		setInstalls((prev) => ({
			...prev,
			[item.id]: { status: "installing", message: "Sending spawn request…" },
		}));
		try {
			const res = await fetch(apiUrl("/api/resonite/inventory/spawn"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ item_id: item.id }),
			});
			const data = await res.json().catch(() => null);
			if (!res.ok) {
				const detail =
					(data as { detail?: string } | null)?.detail ||
					`Request failed (HTTP ${res.status})`;
				throw new Error(detail);
			}
			const message =
				(data as { message?: string; status?: string } | null)?.message ||
				"Spawn request sent to Resonite.";
			setInstalls((prev) => ({
				...prev,
				[item.id]: { status: "done", message },
			}));
		} catch (error) {
			setInstalls((prev) => ({
				...prev,
				[item.id]: {
					status: "error",
					message: error instanceof Error ? error.message : "Install failed.",
				},
			}));
		}
	};

	const renderInstallButton = (item: MarketplaceItem, compact: boolean) => {
		const state = installs[item.id];
		const busy = state?.status === "installing";
		const offline = resoniteRunning === false;
		return (
			<div className={compact ? "shrink-0" : "w-full"}>
				<button
					onClick={() => handleInstall(item)}
					disabled={busy || offline}
					title={
						offline
							? "Start Resonite to install items"
							: `Install ${item.name} to Resonite`
					}
					aria-label={`Install ${item.name} to Resonite`}
					data-testid={`marketplace-install-${item.id}`}
					className={`${compact ? "px-3 py-1.5 text-xs" : "w-full px-4 py-2 text-sm"} bg-white/[0.05] hover:bg-emerald-500 disabled:hover:bg-white/[0.05] disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-bold transition-all border border-white/[0.08] hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/20 active:scale-95 flex items-center justify-center gap-2`}
				>
					{busy ? (
						<Loader2 className="w-4 h-4 animate-spin" />
					) : (
						<Download className="w-4 h-4" />
					)}
					{busy ? "Installing…" : "Install to Resonite"}
				</button>
				{state && state.status !== "installing" && (
					<p
						className={`mt-1.5 text-[11px] leading-snug ${state.status === "done" ? "text-emerald-400" : "text-rose-400"}`}
						role="status"
					>
						{state.message}
					</p>
				)}
			</div>
		);
	};

	const filteredItems = MOCK_ITEMS.filter(
		(item) =>
			(activeCategory === "All" || item.category === activeCategory) &&
			(item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				item.tags.some((t) =>
					t.toLowerCase().includes(searchQuery.toLowerCase()),
				)),
	);

	return (
		<div className="space-y-6 page-enter">
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div className="flex items-center gap-3">
					<div className="bg-emerald-500/10 p-2.5 rounded-xl border border-emerald-500/20">
						<ShoppingBag className="w-6 h-6 text-emerald-400" />
					</div>
					<div>
						<h2 className="text-xl font-bold text-white flex items-center gap-2">
							Asset Downloads
						</h2>
						<p className="text-sm text-slate-500">
							Resonite has no official marketplace, so there is no one-click
							catalog. Assets come from community sites, 3D libraries, and
							GitHub tools — collected here with how each one gets into
							Resonite.
						</p>
					</div>
				</div>
				<div className="flex items-center gap-2">
					<div className="flex items-center rounded-xl border border-white/[0.08] bg-black/20 p-1">
						<button
							onClick={() => switchView("cards")}
							title="Card view"
							aria-label="Card view"
							aria-pressed={view === "cards"}
							data-testid="marketplace-view-cards"
							className={`p-2 rounded-lg transition-all ${
								view === "cards"
									? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20"
									: "text-slate-500 hover:text-slate-300"
							}`}
						>
							<LayoutGrid className="w-4 h-4" />
						</button>
						<button
							onClick={() => switchView("list")}
							title="List view"
							aria-label="List view"
							aria-pressed={view === "list"}
							data-testid="marketplace-view-list"
							className={`p-2 rounded-lg transition-all ${
								view === "list"
									? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20"
									: "text-slate-500 hover:text-slate-300"
							}`}
						>
							<List className="w-4 h-4" />
						</button>
					</div>
					<div className="relative">
						<Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
						<input
							type="text"
							title="Search sample entries"
							aria-label="Search sample entries"
							placeholder="Search samples..."
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							className="bg-black/20 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all w-full md:w-64"
						/>
					</div>
				</div>
			</div>

			{SOURCE_GROUPS.map((group) => (
				<section key={group.title} aria-label={group.title}>
					<div className="flex items-center gap-3 px-1 mb-3">
						<group.Icon className="w-4 h-4 text-emerald-400" />
						<h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/70">
							{group.title}
						</h3>
						<div className="h-px flex-1 bg-gradient-to-r from-border/50 to-transparent" />
					</div>
					{group.note && (
						<p className="text-[11px] text-amber-300/80 px-1 mb-3">
							{group.note}
						</p>
					)}
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
						{group.items.map((source) => (
							<a
								key={source.url}
								href={source.url}
								target="_blank"
								rel="noreferrer"
								className="group glass-card rounded-2xl border border-white/[0.05] hover:border-emerald-500/30 transition-all p-4 flex items-start gap-3"
							>
								<div className="flex-1 min-w-0">
									<p className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">
										{source.name}
									</p>
									<p className="text-xs text-slate-500 mt-1 leading-relaxed">
										{source.blurb}
									</p>
									<p className="text-[10px] text-slate-600 font-mono mt-1.5 truncate">
										{source.url.replace("https://", "")}
									</p>
								</div>
								<ExternalLink className="w-4 h-4 shrink-0 text-slate-600 group-hover:text-emerald-400 transition-colors mt-1" />
							</a>
						))}
					</div>
				</section>
			))}

			<section aria-label="Getting assets into Resonite">
				<div className="flex items-center gap-3 px-1 mb-3">
					<Download className="w-4 h-4 text-emerald-400" />
					<h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/70">
						Getting it into Resonite
					</h3>
					<div className="h-px flex-1 bg-gradient-to-r from-border/50 to-transparent" />
				</div>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-3">
					{[
						{
							step: "1",
							title: "Download",
							text: "Grab VRM files for avatars, or GLB / GLTF / FBX / OBJ for objects and world props.",
						},
						{
							step: "2",
							title: "Import",
							text: "Avatars go through the in-game Avatar Creator; objects via the Files tab or the Unity exporter linked above.",
						},
						{
							step: "3",
							title: "Save & spawn",
							text: "Save creations to your inventory to spawn them anytime, anywhere — or spawn from this webapp's Inventory and IO pages.",
						},
					].map((s) => (
						<div
							key={s.step}
							className="glass-card rounded-2xl border border-white/[0.05] p-4 flex gap-3"
						>
							<span className="shrink-0 w-7 h-7 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-sm font-black flex items-center justify-center">
								{s.step}
							</span>
							<div>
								<p className="text-sm font-bold text-white">{s.title}</p>
								<p className="text-xs text-slate-500 mt-1 leading-relaxed">
									{s.text}
								</p>
							</div>
						</div>
					))}
				</div>
				<p className="text-[11px] text-slate-600 px-1 mt-3">
					Step-by-step avatar import:{" "}
					<a
						href="https://steamcommunity.com/sharedfiles/filedetails/?id=3711969917"
						target="_blank"
						rel="noreferrer"
						className="text-emerald-400 hover:underline"
					>
						Jewel&apos;s Steam guide to the Avatar Creator
					</a>
					.
				</p>
			</section>

			<div className="flex items-center gap-3 px-1">
				<ShoppingBag className="w-4 h-4 text-emerald-400" />
				<h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/70">
					Install-flow preview — sample entries
				</h3>
				<div className="h-px flex-1 bg-gradient-to-r from-border/50 to-transparent" />
			</div>

			<div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
				{["All", "Avatars", "Worlds", "Tools", "Skins", "Plugins", "Audio"].map(
					(category) => (
						<button
							key={category}
							onClick={() => setActiveCategory(category)}
							title={`Filter by ${category}`}
							className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all whitespace-nowrap border ${
								activeCategory === category
									? "bg-emerald-500 text-white border-emerald-500 shadow-lg shadow-emerald-500/20"
									: "bg-white/[0.03] text-slate-500 border-white/[0.05] hover:text-slate-300 hover:border-white/10"
							}`}
						>
							{category}
						</button>
					),
				)}
			</div>

			{filteredItems.length === 0 ? (
				<div className="py-20 text-center space-y-4">
					<ShoppingBag className="w-16 h-16 text-slate-800 mx-auto" />
					<div>
						<p className="text-xl font-bold text-slate-500">
							No treasures found here
						</p>
						<p className="text-slate-600">
							Try adjusting your filters or search terms
						</p>
					</div>
					<button
						onClick={() => {
							setSearchQuery("");
							setActiveCategory("All");
						}}
						className="text-emerald-400 font-bold hover:underline"
					>
						Clear all filters
					</button>
				</div>
			) : view === "list" ? (
				<div className="flex flex-col gap-3">
					{filteredItems.map((item) => (
						<div
							key={item.id}
							className="group glass-card rounded-2xl border border-white/[0.05] hover:border-emerald-500/30 transition-all p-4 flex flex-col md:flex-row md:items-center gap-4"
						>
							<div className="w-12 h-12 shrink-0 rounded-xl bg-slate-900 flex items-center justify-center text-slate-700">
								<Sparkles className="w-6 h-6" />
							</div>
							<div className="flex-1 min-w-0">
								<div className="flex items-center gap-2 flex-wrap">
									<h3 className="font-bold text-white group-hover:text-emerald-400 transition-colors">
										{item.name}
									</h3>
									<span className="bg-white/[0.05] text-slate-400 text-[10px] font-bold px-2 py-0.5 rounded">
										{item.category}
									</span>
									<span
										title="Sample catalog entry, not a live Resonite record"
										className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold px-2 py-0.5 rounded"
									>
										SAMPLE
									</span>
									<span className="text-xs font-bold text-emerald-400">
										{item.price}
									</span>
								</div>
								<p className="text-xs text-slate-500 line-clamp-1 mt-1">
									{item.description}
								</p>
								<div className="flex items-center gap-3 mt-1.5 text-[11px] text-slate-500">
									<span className="flex items-center gap-1">
										<Star className="w-3 h-3 text-amber-400 fill-amber-400" />
										<span className="text-slate-300">{item.rating}</span>
										<span>({item.downloads})</span>
									</span>
									<span>
										by <span className="text-slate-300">{item.author}</span>
									</span>
									<span className="hidden sm:inline text-slate-600">
										{item.tags.join(" · ")}
									</span>
								</div>
							</div>
							{renderInstallButton(item, true)}
						</div>
					))}
				</div>
			) : (
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
					{filteredItems.map((item) => (
						<div
							key={item.id}
							className="group glass-card rounded-2xl overflow-hidden flex flex-col border border-white/[0.05] hover:border-emerald-500/30 hover:bg-emerald-500/[0.02] transition-all"
						>
							<div className="aspect-video bg-slate-900 relative">
								{item.thumbnail ? (
									<img
										src={item.thumbnail}
										alt={item.name}
										className="w-full h-full object-cover"
									/>
								) : (
									<div className="w-full h-full flex items-center justify-center text-slate-800">
										<Sparkles className="w-12 h-12" />
									</div>
								)}
								<div className="absolute bottom-3 left-3 flex items-center gap-1.5">
									<span className="bg-black/60 text-white text-[10px] font-bold px-2 py-1 rounded backdrop-blur-md">
										{item.category}
									</span>
									<span
										title="Sample catalog entry, not a live Resonite record"
										className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold px-2 py-1 rounded backdrop-blur-md"
									>
										SAMPLE
									</span>
								</div>
							</div>
							<div className="p-4 flex-1 flex flex-col">
								<div className="flex items-start justify-between gap-2 mb-1">
									<h3 className="font-bold text-white group-hover:text-emerald-400 transition-colors line-clamp-1">
										{item.name}
									</h3>
									<span className="text-xs font-bold text-emerald-400">
										{item.price}
									</span>
								</div>
								<p className="text-xs text-slate-500 line-clamp-2 mb-4 flex-1">
									{item.description}
								</p>

								<div className="flex items-center justify-between mb-4">
									<div className="flex items-center gap-1">
										<Star className="w-3 h-3 text-amber-400 fill-amber-400" />
										<span className="text-xs text-slate-300">
											{item.rating}
										</span>
										<span className="text-[10px] text-slate-600">
											({item.downloads})
										</span>
									</div>
									<span className="text-[10px] text-slate-500">
										by <span className="text-slate-300">{item.author}</span>
									</span>
								</div>

								{renderInstallButton(item, false)}
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
}
