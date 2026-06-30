import { cn } from "@/common/utils";
import { Card } from "@/components/ui/card";
import { apiUrl } from "@/lib/api-base";
import { useQuery } from "@tanstack/react-query";
import {
	ChevronDown,
	ChevronRight,
	Cpu,
	Info,
	Search,
	Wrench,
} from "lucide-react";
import { useMemo, useState } from "react";

interface ToolParam {
	type: string;
	description?: string;
}

interface Tool {
	name: string;
	description: string;
	parameters?: Record<string, ToolParam>;
}

async function fetchTools(): Promise<Tool[]> {
	try {
		const r = await fetch(apiUrl("/api/system"));
		if (!r.ok) throw new Error("Failed to load tools");
		const data = (await r.json()) as { result?: { tools?: Tool[] } };
		// Handle different API response structures
		const toolsList =
			(data as { tools?: Tool[] }).tools || data.result?.tools || [];
		return toolsList;
	} catch (err) {
		console.error("Tool fetch error:", err);
		return [];
	}
}

export function Tools() {
	const {
		data: tools,
		isLoading,
		isError,
	} = useQuery({
		queryKey: ["tools"],
		queryFn: fetchTools,
	});

	const [expanded, setExpanded] = useState<string | null>(null);
	const [searchQuery, setSearchQuery] = useState("");

	const categories = useMemo(() => {
		if (!tools) return {};
		const filtered = tools.filter(
			(t) =>
				t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				t.description.toLowerCase().includes(searchQuery.toLowerCase()),
		);
		return groupByPrefix(filtered);
	}, [tools, searchQuery]);

	const totalTools = tools?.length || 0;

	return (
		<div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
			<div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
				<div>
					<h2 className="text-3xl font-extrabold tracking-tight text-foreground">
						Neural <span className="text-indigo-400">Toolkit</span>
					</h2>
					<p className="text-muted-foreground mt-1 flex items-center gap-2">
						<Cpu className="h-3 w-3 text-indigo-400" />
						{totalTools} Registered MCP Toolchains • FastMCP Pro
					</p>
				</div>

				<div className="relative group w-full md:w-80">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-indigo-400 transition-colors" />
					<input
						type="text"
						placeholder="Filter toolchain..."
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						className="w-full bg-muted/30 border border-border/50 rounded-xl py-2.5 pl-10 pr-4 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/40 transition-all glass"
					/>
				</div>
			</div>

			{isLoading && (
				<div className="grid gap-4">
					{[1, 2, 3].map((i) => (
						<div
							key={i}
							className="h-20 bg-muted/20 animate-pulse rounded-2xl glass border border-border/30"
						/>
					))}
				</div>
			)}

			{isError && (
				<div className="p-8 text-center bg-red-500/5 border border-red-500/20 rounded-2xl">
					<Wrench className="h-8 w-8 text-red-500/40 mx-auto mb-3" />
					<p className="text-sm font-bold text-red-400 uppercase tracking-widest">
						Protocol Retrieval Failed
					</p>
					<p className="text-xs text-muted-foreground mt-1">
						Unable to fetch tool metadata from the MCP gateway.
					</p>
				</div>
			)}

			{Object.entries(categories).length === 0 && !isLoading && !isError && (
				<div className="p-16 text-center">
					<Search className="h-10 w-10 text-muted-foreground/20 mx-auto mb-4" />
					<p className="text-sm text-muted-foreground italic">
						No tools matching your query found in the neural cache.
					</p>
				</div>
			)}

			<div className="space-y-10">
				{Object.entries(categories).map(([cat, catTools]) => (
					<div key={cat} className="space-y-4">
						<div className="flex items-center gap-3 px-1">
							<div className="h-1 w-1 rounded-full bg-indigo-500" />
							<h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/70">
								{cat} Systems
							</h3>
							<div className="h-px flex-1 bg-gradient-to-r from-border/50 to-transparent" />
						</div>

						<div className="grid gap-3">
							{catTools.map((tool) => (
								<Card
									key={tool.name}
									className={cn(
										"border-border/50 bg-card/30 backdrop-blur-md glass transition-all duration-300 hover:border-indigo-500/30 overflow-hidden",
										expanded === tool.name &&
											"border-indigo-500/40 bg-indigo-500/[0.02]",
									)}
								>
									<button
										onClick={() =>
											setExpanded((e) => (e === tool.name ? null : tool.name))
										}
										aria-expanded={expanded === tool.name ? "true" : "false"}
										aria-controls={`tool-${tool.name}`}
										className="w-full flex items-center justify-between p-4 text-left group"
									>
										<div className="flex items-start gap-4">
											<div
												className={cn(
													"p-2 rounded-lg bg-muted/40 border border-border/50 transition-colors duration-300",
													expanded === tool.name
														? "bg-indigo-500/10 border-indigo-500/30 text-indigo-400"
														: "group-hover:bg-muted",
												)}
											>
												<Wrench className="h-3.5 w-3.5" />
											</div>
											<div className="space-y-1">
												<code className="text-sm font-bold text-foreground tracking-tight group-hover:text-indigo-400 transition-colors">
													{tool.name}
												</code>
												<p className="text-xs text-muted-foreground line-clamp-1 opacity-70">
													{tool.description}
												</p>
											</div>
										</div>
										<div className="flex items-center gap-3">
											{tool.parameters && (
												<span className="hidden sm:inline-block text-[9px] font-bold px-2 py-0.5 rounded bg-muted/50 text-muted-foreground uppercase tracking-widest">
													{Object.keys(tool.parameters).length} Args
												</span>
											)}
											{expanded === tool.name ? (
												<ChevronDown className="w-4 h-4 text-indigo-400 transition-transform" />
											) : (
												<ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-indigo-400 transition-colors" />
											)}
										</div>
									</button>

									{expanded === tool.name && (
										<div
											id={`tool-${tool.name}`}
											className="px-6 pb-6 pt-2 animate-in slide-in-from-top-2 duration-300"
										>
											<div className="p-4 rounded-xl bg-black/20 border border-white/[0.03] space-y-4">
												<div className="flex items-center gap-2 text-[10px] font-bold text-indigo-400/80 uppercase tracking-widest">
													<Info className="h-3 w-3" />
													Detailed Manifest
												</div>
												<p className="text-xs text-foreground/80 leading-relaxed">
													{tool.description}
												</p>

												{tool.parameters && (
													<div className="space-y-3 pt-2">
														<div className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-2">
															Parameters
														</div>
														<div className="grid gap-2">
															{Object.entries(tool.parameters).map(
																([pname, param]) => (
																	<div
																		key={pname}
																		className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 p-3 rounded-lg bg-muted/20 border border-white/[0.02]"
																	>
																		<code className="text-xs font-bold text-indigo-300 w-full sm:w-40 flex-shrink-0">
																			{pname}
																		</code>
																		<div className="flex items-center gap-3 flex-1">
																			<span className="text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground font-mono uppercase font-black">
																				{param.type}
																			</span>
																			<span className="text-xs text-muted-foreground italic shrink">
																				{param.description ||
																					"No documentation provided."}
																			</span>
																		</div>
																	</div>
																),
															)}
														</div>
													</div>
												)}
											</div>
										</div>
									)}
								</Card>
							))}
						</div>
					</div>
				))}
			</div>
		</div>
	);
}

function groupByPrefix(tools: Tool[]): Record<string, Tool[]> {
	const out: Record<string, Tool[]> = {};
	for (const t of tools) {
		const parts = t.name.split("_");
		let prefix = "";

		if (parts[0] === "resonite") {
			prefix = parts.slice(0, 2).join("_");
		} else {
			prefix = parts[0];
		}

		const cat = prefix.replace("resonite_", "").replace("_", " ");
		const label = cat.charAt(0).toUpperCase() + cat.slice(1);
		if (!out[label]) out[label] = [];
		out[label].push(t);
	}
	return out;
}
