import { apiUrl } from "@/lib/api-base";
import { useQuery } from "@tanstack/react-query";
import {
	Calendar,
	ChevronLeft,
	ChevronRight,
	Image as ImageIcon,
	Info,
	Sparkles,
	Tag,
	X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "../common/utils";

interface GalleryItem {
	url: string;
	title: string;
	category: "In-Resonite" | "Webapp" | "Avatars";
	date: string;
	size: string;
	is_local: boolean;
}

export function Gallery() {
	const [activeCategory, setActiveCategory] = useState<string>("All");
	const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null);

	// Fetch gallery items from backend
	const { data, isLoading } = useQuery<{ items: GalleryItem[] }>({
		queryKey: ["gallery"],
		queryFn: async () => {
			const res = await fetch(apiUrl("/api/resonite/gallery"));
			if (!res.ok) throw new Error("Failed to load gallery items");
			return res.json();
		},
	});

	const items = data?.items || [];

	// Filter items based on active tab
	const filteredItems = items.filter((item) =>
		activeCategory === "All" ? true : item.category === activeCategory,
	);

	// Keyboard navigation for lightbox
	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent) => {
			if (selectedImageIndex === null) return;
			if (e.key === "Escape") setSelectedImageIndex(null);
			if (e.key === "ArrowRight") {
				setSelectedImageIndex((prev) =>
					prev !== null && prev < filteredItems.length - 1 ? prev + 1 : 0,
				);
			}
			if (e.key === "ArrowLeft") {
				setSelectedImageIndex((prev) =>
					prev !== null && prev > 0 ? prev - 1 : filteredItems.length - 1,
				);
			}
		};
		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [selectedImageIndex, filteredItems]);

	const categories = ["All", "In-Resonite", "Webapp", "Avatars"];

	return (
		<div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
			{/* Header Section */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-1 border-b border-white/10 pb-4">
				<div className="flex items-center gap-4">
					<div className="relative">
						<div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-25" />
						<div className="relative bg-slate-900/50 p-3 rounded-2xl border border-white/10 glass-morphism">
							<ImageIcon className="w-7 h-7 text-indigo-400" />
						</div>
					</div>
					<div>
						<h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
							Visual Gallery
							<Sparkles className="w-4 h-4 text-indigo-400 animate-pulse" />
						</h2>
						<p className="text-sm text-slate-400 max-w-md">
							In-game captures, world showcases, and dashboard interface telemetry
						</p>
					</div>
				</div>
			</div>

			{/* Filters / Tabs */}
			<div className="flex gap-2 pb-2 overflow-x-auto border-b border-white/[0.05]">
				{categories.map((cat) => (
					<button
						key={cat}
						onClick={() => {
							setActiveCategory(cat);
							setSelectedImageIndex(null);
						}}
						className={cn(
							"px-4 py-2 text-xs font-bold rounded-xl transition-all duration-300 border active:scale-95 whitespace-nowrap",
							activeCategory === cat
								? "bg-indigo-600 text-white border-indigo-500/30 shadow-lg shadow-indigo-500/20"
								: "text-slate-400 hover:text-white hover:bg-white/5 border-transparent",
						)}
					>
						{cat === "All" ? "All Captures" : cat}
					</button>
				))}
			</div>

			{/* Grid Layout */}
			{isLoading ? (
				<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
					{[...Array(4)].map((_, i) => (
						<div
							key={i}
							className="aspect-video rounded-3xl bg-white/[0.02] border border-white/[0.05] animate-pulse"
						/>
					))}
				</div>
			) : filteredItems.length === 0 ? (
				<div className="flex flex-col items-center justify-center p-12 text-center bg-white/[0.01] border border-white/[0.05] rounded-3xl">
					<ImageIcon className="w-12 h-12 text-slate-600 mb-4" />
					<p className="text-sm font-medium text-slate-400">
						No screenshots found in this category
					</p>
					<p className="text-xs text-slate-500 mt-1">
						Drag screenshots into your <code>web_sota/public/screenshots/</code> folder
						to see them here!
					</p>
				</div>
			) : (
				<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
					{filteredItems.map((item, index) => (
						<div
							key={item.url + index}
							onClick={() => setSelectedImageIndex(index)}
							className="group relative rounded-2xl overflow-hidden border border-white/10 bg-slate-950/40 glass-card aspect-video cursor-pointer hover:border-indigo-500/40 transition-all duration-500"
						>
							{/* Image */}
							<img
								src={item.url}
								alt={item.title}
								className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
							/>

							{/* Bottom Info Bar Overlay */}
							<div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end gap-1">
								<h4 className="text-xs font-bold text-white tracking-wide">
									{item.title}
								</h4>
								<div className="flex items-center justify-between text-[9px] text-slate-400 font-medium">
									<span className="flex items-center gap-1">
										<Tag className="w-2.5 h-2.5 text-indigo-400" />
										{item.category}
									</span>
									<span className="flex items-center gap-1">
										<Calendar className="w-2.5 h-2.5 text-purple-400" />
										{item.date}
									</span>
								</div>
							</div>

							{/* Local / Online Indicator */}
							<div className="absolute top-2 right-2 px-2.5 py-1 rounded-full text-[9px] font-bold uppercase tracking-wider glass-morphism border border-white/10 text-slate-300">
								{item.is_local ? "Local" : "Cloud Preset"}
							</div>
						</div>
					))}
				</div>
			)}

			{/* Lightbox / Modal */}
			{selectedImageIndex !== null && filteredItems[selectedImageIndex] && (
				<div className="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-[100] flex flex-col items-center justify-center p-4 md:p-8 animate-in fade-in duration-300">
					{/* Close button */}
					<button
						onClick={() => setSelectedImageIndex(null)}
						className="absolute top-4 right-4 p-3 text-slate-400 hover:text-white bg-white/5 border border-white/10 hover:border-white/20 rounded-full transition-all duration-300 active:scale-95"
					>
						<X className="w-5 h-5" />
					</button>

					{/* Navigation Left */}
					<button
						onClick={() =>
							setSelectedImageIndex((prev) =>
								prev !== null && prev > 0 ? prev - 1 : filteredItems.length - 1,
							)
						}
						className="absolute left-4 p-3 text-slate-400 hover:text-white bg-white/5 border border-white/10 hover:border-white/20 rounded-full transition-all duration-300 active:scale-95 hidden md:block"
					>
						<ChevronLeft className="w-5 h-5" />
					</button>

					{/* Active Image Box */}
					<div className="max-w-5xl max-h-[70vh] w-full flex items-center justify-center p-2 relative">
						<img
							src={filteredItems[selectedImageIndex].url}
							alt={filteredItems[selectedImageIndex].title}
							className="max-w-full max-h-[75vh] rounded-2xl object-contain border border-white/10 shadow-2xl shadow-black/80"
						/>
					</div>

					{/* Bottom Info Details Card */}
					<div className="mt-6 max-w-xl w-full p-5 rounded-2xl bg-slate-900/50 border border-white/10 glass-morphism text-center space-y-3">
						<h3 className="text-base font-bold text-white">
							{filteredItems[selectedImageIndex].title}
						</h3>
						<div className="flex items-center justify-center gap-6 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
							<span className="flex items-center gap-1.5">
								<Tag className="w-3 h-3 text-indigo-400" />
								{filteredItems[selectedImageIndex].category}
							</span>
							<span className="flex items-center gap-1.5 border-x border-white/10 px-6">
								<Calendar className="w-3 h-3 text-purple-400" />
								{filteredItems[selectedImageIndex].date}
							</span>
							<span>{filteredItems[selectedImageIndex].size}</span>
						</div>

						{/* Quick Tips for Noobs */}
						{filteredItems[selectedImageIndex].category === "In-Resonite" && (
							<div className="p-3 rounded-xl bg-indigo-500/5 border border-indigo-500/10 text-left flex items-start gap-2.5">
								<Info className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
								<p className="text-[10px] text-slate-400 leading-relaxed">
									<span className="font-bold text-indigo-400">Pro-Tip for Beginners:</span> You
									can join this world inside Resonite by searching for its title
									in the <span className="text-white">Worlds</span> tab of your in-game Dash
									menu. Double-click it to visit or spawn a portal.
								</p>
							</div>
						)}
					</div>

					{/* Navigation Right */}
					<button
						onClick={() =>
							setSelectedImageIndex((prev) =>
								prev !== null && prev < filteredItems.length - 1 ? prev + 1 : 0,
							)
						}
						className="absolute right-4 p-3 text-slate-400 hover:text-white bg-white/5 border border-white/10 hover:border-white/20 rounded-full transition-all duration-300 active:scale-95 hidden md:block"
					>
						<ChevronRight className="w-5 h-5" />
					</button>

					{/* Keyboard helper hint */}
					<span className="absolute bottom-4 text-[9px] text-slate-500 tracking-widest uppercase">
						Use Arrow Keys ← → to navigate · Esc to close
					</span>
				</div>
			)}
		</div>
	);
}
