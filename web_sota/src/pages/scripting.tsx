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
	Trash2,
} from "lucide-react";
import { useState } from "react";

const MACRO_KEY = "resonite-script-macros";

const TEMPLATES: Record<string, string> = {
	"World Audio Duck":
		'// World Audio Duck — lower world volume while a user talks\n// target: world_audio\n\nawait resonite.spawn("AudioDuck", {\n  duckedVolume: 0.2,\n  releaseMs: 800,\n});',
	"Avatar Parameter Sync":
		'// Avatar Parameter Sync — mirror a driver value to an avatar parameter\n// target: local_avatar\n\nawait resonite.spawn("ParameterSync", {\n  source: "Voice_Volume",\n  target: "Glow_Intensity",\n});',
	"Material Pulse":
		'// Material Pulse — pulse emissive on the beat of world time\n// target: selected_slot\n\nawait resonite.spawn("MaterialPulse", {\n  periodSeconds: 2.0,\n  intensity: 1.5,\n});',
	"OSC Message Relay":
		'// OSC Message Relay — forward a Resonite event to an external OSC app\n// target: world_root\n\nawait resonite.spawn("OSCRelay", {\n  host: "127.0.0.1",\n  port: 9000,\n  address: "/resonite/event",\n});',
};

function loadMacros(): Record<string, string> {
	try {
		const raw = localStorage.getItem(MACRO_KEY);
		const parsed = raw ? (JSON.parse(raw) as Record<string, string>) : {};
		return parsed && typeof parsed === "object" ? parsed : {};
	} catch {
		return {};
	}
}

export function ScriptingPage() {
	const [script, setScript] = useState(
		'// ProtoFlux Script Template\n// target: local_avatar\n\nawait resonite.spawn("LogNode", { text: "Hello from MCP!" });',
	);
	const [logs, setLogs] = useState<
		{ type: "info" | "error" | "success"; msg: string; time: string }[]
	>([]);
	const [cursor, setCursor] = useState({ ln: 1, col: 1 });
	const [macros, setMacros] = useState<Record<string, string>>(loadMacros);

	const updateCursor = (el: HTMLTextAreaElement) => {
		const before = el.value.slice(0, el.selectionStart).split("\n");
		setCursor({
			ln: before.length,
			col: before[before.length - 1].length + 1,
		});
	};

	const addLog = (type: "info" | "error" | "success", msg: string) => {
		setLogs((prev) => [
			{ type, msg, time: new Date().toLocaleTimeString() },
			...prev,
		]);
	};

	const saveMacro = () => {
		const name = `Macro ${Object.keys(macros).length + 1}`;
		const next = { ...macros, [name]: script };
		setMacros(next);
		try {
			localStorage.setItem(MACRO_KEY, JSON.stringify(next));
		} catch {
			// ignore storage errors
		}
		addLog(
			"success",
			`Saved ${name} locally (${Object.keys(next).length} total).`,
		);
	};

	const deleteMacro = (name: string) => {
		const next = { ...macros };
		delete next[name];
		setMacros(next);
		try {
			localStorage.setItem(MACRO_KEY, JSON.stringify(next));
		} catch {
			// ignore storage errors
		}
	};

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
						title="Save current script as a local macro"
						aria-label="Save current script as a macro"
						onClick={saveMacro}
						className="flex items-center gap-2 bg-white/[0.05] hover:bg-white/[0.1] text-white px-4 py-2 rounded-xl text-sm font-medium transition-all border border-white/[0.08] active:scale-95"
					>
						<Save className="w-4 h-4" />
						Save Macro
					</button>
					<button
						title="Arbitrary script execution isn't exposed by the backend — only named ProtoFlux presets can run (see ProtoFlux page)"
						aria-label="Execute the current script in Resonite (unavailable)"
						disabled
						className="flex items-center gap-2 bg-orange-500 text-white px-6 py-2 rounded-xl text-sm font-bold transition-all shadow-lg shadow-orange-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<Play className="w-4 h-4" />
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
								onChange={(e) => {
									setScript(e.target.value);
									updateCursor(e.target);
								}}
								onSelect={(e) => updateCursor(e.currentTarget)}
								className="w-full h-full bg-transparent p-6 font-mono text-sm text-slate-300 focus:outline-none resize-none spellcheck-false"
								spellCheck={false}
							/>
							<div
								className="absolute left-0 top-0 bottom-0 w-10 bg-black/20 border-r border-white/5 flex flex-col items-center py-6 gap-2 opacity-20 select-none pointer-events-none"
								aria-hidden="true"
							>
								{Array.from({ length: 20 }, (_, n) => n + 1).map((n) => (
									<span
										key={n}
										className="text-[10px] font-mono text-slate-500"
									>
										{n}
									</span>
								))}
							</div>
						</div>
						<div className="p-2 border-t border-white/[0.05] bg-black/40 flex items-center justify-between gap-4">
							<div className="flex items-center gap-4 text-xs text-slate-600">
								<span>
									Ln {cursor.ln}, Col {cursor.col}
								</span>
								<span>Spaces: 4</span>
							</div>
							<div className="flex items-center gap-1">
								<button
									title="Clear script editor"
									aria-label="Clear script editor"
									onClick={() => {
										setScript("");
										setCursor({ ln: 1, col: 1 });
									}}
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
								logs.map((log) => (
									<div
										key={`${log.time}-${log.msg}`}
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
									Macros
								</span>
								<span className="text-lg font-bold text-white">
									{Object.keys(macros).length}
								</span>
							</div>
							<div className="p-3 bg-white/[0.02] rounded-xl border border-white/[0.05]">
								<span className="block text-[10px] text-slate-500 uppercase font-bold">
									Log entries
								</span>
								<span className="text-lg font-bold text-white">
									{logs.length}
								</span>
							</div>
						</div>
					</div>

					<div className="glass-card p-4 space-y-4">
						<h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
							<BookOpen className="w-3.5 h-3.5" />
							Logic Templates
						</h3>
						<div className="space-y-2">
							{Object.entries(TEMPLATES).map(([name]) => (
								<button
									key={name}
									title={`Load ${name} into the editor`}
									onClick={() => {
										setScript(TEMPLATES[name]);
										setCursor({ ln: 1, col: 1 });
										addLog(
											"info",
											`Loaded template "${name}" into the editor.`,
										);
									}}
									className="w-full text-left p-3 rounded-xl hover:bg-white/[0.05] border border-transparent hover:border-white/[0.08] transition-all group"
								>
									<span className="block text-sm font-medium text-slate-300 group-hover:text-white transition-colors">
										{name}
									</span>
									<span className="text-[10px] text-slate-600 uppercase font-bold tracking-tighter">
										Click to load
									</span>
								</button>
							))}
						</div>
						{Object.keys(macros).length > 0 && (
							<div className="space-y-2 pt-2 border-t border-white/[0.05]">
								<h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-1">
									Saved macros
								</h4>
								{Object.entries(macros).map(([name, body]) => (
									<div
										key={name}
										className="flex items-center gap-2 p-2 rounded-xl hover:bg-white/[0.05] border border-transparent hover:border-white/[0.08] transition-all group"
									>
										<button
											title={`Load ${name} into the editor`}
											onClick={() => {
												setScript(body);
												setCursor({ ln: 1, col: 1 });
											}}
											className="flex-1 text-left text-sm font-medium text-slate-300 group-hover:text-white transition-colors truncate"
										>
											{name}
										</button>
										<button
											title={`Delete ${name}`}
											aria-label={`Delete ${name}`}
											onClick={() => deleteMacro(name)}
											className="p-1 text-slate-600 hover:text-rose-400 transition-colors"
										>
											<Trash2 className="w-3.5 h-3.5" />
										</button>
									</div>
								))}
							</div>
						)}
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
						<a
							href="/help"
							className="text-[10px] text-orange-400 font-bold uppercase tracking-wider hover:underline"
						>
							Learn more in Docs
						</a>
					</div>
				</div>
			</div>
		</div>
	);
}
