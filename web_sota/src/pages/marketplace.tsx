import {
	ChevronRight,
	Clock,
	Download,
	Flame,
	Heart,
	Search,
	Share2,
	ShoppingBag,
	Sparkles,
	Star,
	Tag,
} from "lucide-react";
import { useState } from "react";

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

export function MarketplacePage() {
	const [searchQuery, setSearchQuery] = useState("");
	const [activeCategory, setActiveCategory] = useState("All");

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
						<h2 className="text-xl font-bold text-white">
							Resonite Marketplace
						</h2>
						<p className="text-sm text-slate-500">
							Discover and install community-driven plugins, avatars, and worlds
						</p>
					</div>
				</div>
				<div className="flex items-center gap-2">
					<div className="relative">
						<Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
						<input
							type="text"
							title="Search marketplace"
							aria-label="Search community designs and assets"
							placeholder="Search marketplace..."
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							className="bg-black/20 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all w-full md:w-64"
						/>
					</div>
				</div>
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
							<div className="absolute top-3 right-3 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
								<button
									title="Like item"
									aria-label={`Like ${item.name}`}
									className="p-2 bg-black/60 text-white rounded-lg backdrop-blur-md hover:bg-black/80 transition-colors"
								>
									<Heart className="w-4 h-4" />
								</button>
								<button
									title="Share item"
									aria-label={`Share ${item.name}`}
									className="p-2 bg-black/60 text-white rounded-lg backdrop-blur-md hover:bg-black/80 transition-colors"
								>
									<Share2 className="w-4 h-4" />
								</button>
							</div>
							<div className="absolute bottom-3 left-3">
								<span className="bg-black/60 text-white text-[10px] font-bold px-2 py-1 rounded backdrop-blur-md">
									{item.category}
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
									<span className="text-xs text-slate-300">{item.rating}</span>
									<span className="text-[10px] text-slate-600">
										({item.downloads})
									</span>
								</div>
								<span className="text-[10px] text-slate-500">
									by <span className="text-slate-300">{item.author}</span>
								</span>
							</div>

							<button
								title="Install to Resonite"
								aria-label={`Install ${item.name} to Resonite`}
								className="w-full bg-white/[0.05] hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-sm font-bold transition-all border border-white/[0.08] hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/20 active:scale-95 flex items-center justify-center gap-2"
							>
								<Download className="w-4 h-4" />
								Install to Resonite
							</button>
						</div>
					</div>
				))}

				{filteredItems.length === 0 && (
					<div className="col-span-full py-20 text-center space-y-4">
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
				)}
			</div>

			<div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
				<div className="glass-card p-6 border-l-4 border-l-emerald-500 flex items-center justify-between">
					<div className="flex items-center gap-4">
						<Flame className="w-8 h-8 text-orange-400" />
						<div>
							<h4 className="font-bold text-white">Trending Now</h4>
							<p className="text-xs text-slate-500">Most installed this week</p>
						</div>
					</div>
					<ChevronRight className="w-5 h-5 text-slate-600" />
				</div>
				<div className="glass-card p-6 border-l-4 border-l-blue-500 flex items-center justify-between">
					<div className="flex items-center gap-4">
						<Clock className="w-8 h-8 text-blue-400" />
						<div>
							<h4 className="font-bold text-white">New Releases</h4>
							<p className="text-xs text-slate-500">Fresh from the community</p>
						</div>
					</div>
					<ChevronRight className="w-5 h-5 text-slate-600" />
				</div>
				<div className="glass-card p-6 border-l-4 border-l-purple-500 flex items-center justify-between">
					<div className="flex items-center gap-4">
						<Tag className="w-8 h-8 text-purple-400" />
						<div>
							<h4 className="font-bold text-white">Flash Sales</h4>
							<p className="text-xs text-slate-500">Limited time offers</p>
						</div>
					</div>
					<ChevronRight className="w-5 h-5 text-slate-600" />
				</div>
			</div>
		</div>
	);
}
