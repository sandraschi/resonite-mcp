import { Code2, ExternalLink } from "lucide-react";
import { apiUrl } from "@/lib/api-base";

const QUICK_REF: { method: string; path: string; what: string }[] = [
	{
		method: "GET",
		path: "/api/status",
		what: "System status incl. ResoniteLink",
	},
	{ method: "GET", path: "/api/stats", what: "Dashboard KPIs (real counts)" },
	{ method: "GET", path: "/api/sessions", what: "Live public sessions" },
	{
		method: "GET",
		path: "/rl/status?autoconnect=true",
		what: "Link status + auto-discover",
	},
	{
		method: "GET",
		path: "/api/world/map-data",
		what: "Top-down world map nodes",
	},
	{
		method: "GET",
		path: "/rl/world/children/{id}",
		what: "Slot children (flattened)",
	},
	{
		method: "PATCH",
		path: "/rl/slot/{id}",
		what: "Rename / move / rescale a slot",
	},
	{ method: "GET", path: "/api/logs", what: "Log ring buffer" },
	{ method: "GET", path: "/api/llm-discovery", what: "Local LLM providers" },
];

export function ApiDocs() {
	return (
		<div className="space-y-8 animate-in fade-in duration-700">
			<div className="relative group">
				<div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000" />
				<div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6 bg-card/40 backdrop-blur-xl border border-white/10 p-6 rounded-xl glass-card">
					<div className="flex items-center gap-5">
						<div className="p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl shadow-inner">
							<Code2 className="w-8 h-8 text-cyan-400" aria-hidden="true" />
						</div>
						<div>
							<h2 className="text-3xl font-black tracking-tighter text-foreground">
								API <span className="text-cyan-400">Docs</span>
							</h2>
							<p className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1">
								Live backend reference, served by FastAPI itself
							</p>
						</div>
					</div>

					<a
						href={apiUrl("/docs")}
						target="_blank"
						rel="noreferrer"
						className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 text-cyan-300 text-xs font-bold uppercase tracking-widest transition-all"
					>
						<ExternalLink className="w-4 h-4" />
						Open in browser
					</a>
				</div>
			</div>

			<div className="glass-card border border-white/10 rounded-2xl overflow-hidden">
				<iframe
					src={apiUrl("/docs")}
					title="Backend Swagger UI"
					className="w-full h-[70vh] bg-white"
				/>
			</div>

			<div className="glass-card border border-white/10 rounded-2xl p-6">
				<h3 className="text-xs font-black uppercase tracking-[0.2em] text-slate-300 mb-4">
					Quick reference
				</h3>
				<div className="grid gap-2">
					{QUICK_REF.map((row) => (
						<div
							key={`${row.method}-${row.path}`}
							className="flex flex-col sm:flex-row sm:items-center gap-2 text-sm"
						>
							<span className="font-mono text-[10px] font-black text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 rounded px-2 py-0.5 w-16 text-center shrink-0">
								{row.method}
							</span>
							<code className="font-mono text-xs text-slate-200">
								{row.path}
							</code>
							<span className="text-xs text-slate-500 sm:ml-auto">
								{row.what}
							</span>
						</div>
					))}
				</div>
				<p className="text-xs text-slate-500 mt-4">
					ReDoc edition:{" "}
					<a
						href={apiUrl("/redoc")}
						target="_blank"
						rel="noreferrer"
						className="text-indigo-400 hover:underline"
					>
						{apiUrl("/redoc")}
					</a>
				</p>
			</div>
		</div>
	);
}
