import { apiUrl } from "@/lib/api-base";
import { useMutation } from "@tanstack/react-query";
import {
	AlertTriangle,
	BookOpen,
	CheckCircle2,
	ChevronRight,
	Code2,
	Cpu,
	History,
	Play,
	Save,
	Terminal,
	Zap,
} from "lucide-react";
import { useState } from "react";

interface ScriptResult {
	status: "success" | "error";
	message: string;
	output?: string;
}

export function ScriptingPage() {
	const [script, setScript] = useState(
		'// ProtoFlux Script Template\n// target: local_avatar\n\nawait resonite.spawn("LogNode", { text: "Hello from MCP!" });',
	);
	const [logs, setLogs] = useState<
		{ type: "info" | "error" | "success"; msg: string; time: string }[]
	>([]);

	const executeMutation = useMutation({
		mutationFn: async (code: string) => {
			const r = await fetch(apiUrl("/api/resonite/scripting/execute"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ script: code }),
			});
			return r.json();
		},
		onSuccess: (data: ScriptResult) => {
			setLogs((prev) => [
				{
					type: data.status === "success" ? "success" : "error",
					msg: data.message,
					time: new Date().toLocaleTimeString(),
				},
				...prev,
			]);
		},
	});

	return (
		<div className="space-y-6 page-enter">
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div className="flex items-center gap-3">
					<div className="bg-orange-500/10 p-2.5 rounded-xl border border-orange-500/20">
						<Terminal className="w-6 h-6 text-orange-400" />
					</div>
					<div>
						<h2 className="text-xl font-bold text-white">Logic & Scripting</h2>
						<p className="text-sm text-slate-500">
							Bridge external logic to Resonite's ProtoFlux engine
						</p>
					</div>
				</div>
				<div className="flex items-center gap-2">
					<button
						title="Save as Macro"
						aria-label="Save current script as a macro"
						className="flex items-center gap-2 bg-white/[0.05] hover:bg-white/[0.1] text-white px-4 py-2 rounded-xl text-sm font-medium transition-all border border-white/[0.08]"
					>
						<Save className="w-4 h-4" />
						Save Macro
					</button>
					<button
						title="Execute Script"
						aria-label="Execute the current script in Resonite"
						onClick={() => executeMutation.mutate(script)}
						disabled={executeMutation.isPending}
						className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white px-6 py-2 rounded-xl text-sm font-bold transition-all shadow-lg shadow-orange-500/20 active:scale-95"
					>
						{executeMutation.isPending ? (
							<Zap className="w-4 h-4 animate-pulse" />
						) : (
							<Play className="w-4 h-4" />
						)}
						Execute
					</button>
				</div>
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<div className="lg:col-span-2 space-y-4">
					<div className="glass-card flex flex-col h-[500px] overflow-hidden">
						<div className="flex items-center justify-between px-4 py-2 border-b border-white/[0.05] bg-white/[0.02]">
							<div className="flex items-center gap-4">
								<div className="flex items-center gap-2">
									<div className="w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
									<span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
										Scratchpad.js
									</span>
								</div>
							</div>
							<div className="flex items-center gap-2">
								<span className="text-[10px] text-slate-600 font-mono">
									UTF-8
								</span>
								<span className="text-[10px] text-slate-600 font-mono">
									Javascript / ProtoFlux
								</span>
							</div>
						</div>
						<div className="flex-1 relative">
							<textarea
								value={script}
								title="Script Editor"
								aria-label="Write ProtoFlux script here"
								placeholder="// ProtoFlux Script Template..."
								onChange={(e) => setScript(e.target.value)}
								className="w-full h-full bg-transparent p-6 font-mono text-sm text-slate-300 focus:outline-none resize-none spellcheck-false"
								spellCheck={false}
							/>
							<div className="absolute left-0 top-0 bottom-0 w-10 bg-black/20 border-r border-white/5 flex flex-col items-center py-6 gap-2 opacity-20 select-none pointer-events-none">
								{[...Array(20)].map((_, i) => (
									<span
										key={i}
										className="text-[10px] font-mono text-slate-500"
									>
										{i + 1}
									</span>
								))}
							</div>
						</div>
						<div className="p-2 border-t border-white/[0.05] bg-black/40 flex items-center justify-between gap-4">
							<div className="flex items-center gap-4 text-xs text-slate-600">
								<span>Ln 4, Col 21</span>
								<span>Spaces: 4</span>
							</div>
							<div className="flex items-center gap-1">
								<button
									title="Format Code"
									aria-label="Auto-format script code"
									className="p-1 px-2 rounded hover:bg-white/5 text-[10px] font-bold text-slate-400 uppercase tracking-tighter transition-colors"
								>
									Format
								</button>
								<button
									title="Clear Code"
									aria-label="Clear script editor"
									className="p-1 px-2 rounded hover:bg-white/5 text-[10px] font-bold text-slate-400 uppercase tracking-tighter transition-colors"
								>
									Clear
								</button>
							</div>
						</div>
					</div>

					<div className="glass-card p-4 space-y-4">
						<div className="flex items-center gap-2 text-slate-400">
							<History className="w-4 h-4" />
							<h3 className="text-xs font-bold uppercase tracking-widest">
								Execution Logs
							</h3>
						</div>
						<div className="space-y-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
							{logs.length === 0 ? (
								<p className="text-xs text-slate-600 italic py-4 text-center">
									No logs recorded in this session
								</p>
							) : (
								logs.map((log, i) => (
									<div
										key={i}
										className={`flex items-start gap-3 p-2 rounded-lg ${log.type === "error" ? "bg-rose-500/5 text-rose-400 border border-rose-500/10" : log.type === "success" ? "bg-emerald-500/5 text-emerald-400 border border-emerald-500/10" : "bg-white/5 text-slate-400 border border-white/5"}`}
									>
										{log.type === "error" ? (
											<AlertTriangle className="w-3.5 h-3.5 mt-0.5" />
										) : log.type === "success" ? (
											<CheckCircle2 className="w-3.5 h-3.5 mt-0.5" />
										) : (
											<ChevronRight className="w-3.5 h-3.5 mt-0.5" />
										)}
										<div className="flex-1 min-w-0">
											<p className="text-xs font-mono break-all">{log.msg}</p>
											<span className="text-[9px] opacity-40 font-mono mt-0.5">
												{log.time}
											</span>
										</div>
									</div>
								))
							)}
						</div>
					</div>
				</div>

				<div className="space-y-6">
					<div className="glass-card p-4 space-y-4">
						<h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
							<Cpu className="w-3.5 h-3.5" />
							Runtime Stats
						</h3>
						<div className="grid grid-cols-2 gap-4">
							<div className="p-3 bg-white/[0.02] rounded-xl border border-white/[0.05]">
								<span className="block text-[10px] text-slate-500 uppercase font-bold">
									Latency
								</span>
								<span className="text-lg font-bold text-white">4ms</span>
							</div>
							<div className="p-3 bg-white/[0.02] rounded-xl border border-white/[0.05]">
								<span className="block text-[10px] text-slate-500 uppercase font-bold">
									Ops/Sec
								</span>
								<span className="text-lg font-bold text-white">12.4k</span>
							</div>
						</div>
					</div>

					<div className="glass-card p-4 space-y-4">
						<h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
							<BookOpen className="w-3.5 h-3.5" />
							Logic Templates
						</h3>
						<div className="space-y-2">
							{[
								"World Audio Duck",
								"Avatar Parameter Sync",
								"Material Pulse",
								"OSC Message Relay",
							].map((t) => (
								<button
									key={t}
									className="w-full text-left p-3 rounded-xl hover:bg-white/[0.05] border border-transparent hover:border-white/[0.08] transition-all group"
								>
									<span className="block text-sm font-medium text-slate-300 group-hover:text-white transition-colors">
										{t}
									</span>
									<span className="text-[10px] text-slate-600 uppercase font-bold tracking-tighter">
										Click to load
									</span>
								</button>
							))}
						</div>
					</div>

					<div className="glass-card p-4 bg-orange-500/5 border border-orange-500/10 space-y-3">
						<div className="flex items-center gap-2 text-orange-400">
							<Code2 className="w-4 h-4" />
							<h3 className="text-xs font-bold uppercase tracking-widest">
								MCP Direct Connection
							</h3>
						</div>
						<p className="text-xs text-slate-400 leading-relaxed">
							Resonite logic can trigger MCP tools directly via the{" "}
							<span className="text-orange-400 font-mono">mcp_exec</span> node.
							This allows for in-world interactions to control your local system
							or cloud services.
						</p>
						<button className="text-[10px] text-orange-400 font-bold uppercase tracking-wider hover:underline">
							Learn more in Docs
						</button>
					</div>
				</div>
			</div>
		</div>
	);
}
