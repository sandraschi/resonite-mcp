import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/common/utils";
import {
	BookOpen,
	ExternalLink,
	HelpCircle,
	Info,
	Radio,
	Wifi,
	Zap,
	Monitor,
	Headphones,
	Cpu,
	Globe2,
	User,
	Wand2,
	Move,
} from "lucide-react";

function RefCard({
	title,
	desc,
	href,
}: { title: string; desc: string; href: string }) {
	return (
		<a
			href={href}
			target="_blank"
			rel="noopener noreferrer"
			className="border border-border/50 bg-card/30 glass p-4 flex items-center justify-between group hover:border-indigo-500/40 transition-all duration-300 rounded-xl"
		>
			<div className="space-y-1">
				<p className="text-xs font-bold tracking-tight text-foreground group-hover:text-indigo-400 transition-colors">
					{title}
				</p>
				<p className="text-[10px] text-muted-foreground">{desc}</p>
			</div>
			<ExternalLink className="w-3.5 h-3.5 text-muted-foreground group-hover:text-indigo-400 transition-colors" />
		</a>
	);
}

export function Help() {
	return (
		<div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
			<div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-border/30">
				<div>
					<h2 className="text-3xl font-extrabold tracking-tight text-foreground">
						Help &amp; <span className="text-indigo-400">Reference</span>
					</h2>
					<p className="text-muted-foreground mt-1 text-sm">
						Setup guide, protocol reference, FAQ, and external resources
					</p>
				</div>
			</div>

			<Tabs defaultValue="setup" className="w-full">
				<TabsList className="w-full justify-start gap-1 bg-transparent border-b border-border/30 rounded-none pb-0 mb-6 overflow-x-auto">
					{[
						{ id: "setup", label: "Setup" },
						{ id: "beginner", label: "Beginner Guide" },
						{ id: "comparison", label: "Comparison & Pipeline" },
						{ id: "protocols", label: "Protocols" },
						{ id: "vr", label: "VR & Pico" },
						{ id: "faq", label: "FAQ" },
						{ id: "links", label: "Links" },
					].map(({ id, label }) => (
						<TabsTrigger
							key={id}
							value={id}
							className={cn(
								"text-xs font-bold rounded-none border-b-2 border-transparent px-4 py-2 data-[state=active]:border-indigo-500 data-[state=active]:text-indigo-400 data-[state=active]:bg-transparent hover:text-foreground transition-colors",
							)}
						>
							{label}
						</TabsTrigger>
					))}
				</TabsList>

				{/* ── Setup Tab ──────────────────────────────────────────── */}
				<TabsContent value="setup" className="space-y-6">
					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-6">
							<div className="flex items-center gap-3">
								<Zap className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									Quick Start
								</h3>
							</div>
							<ol className="space-y-4 list-decimal list-inside text-sm text-foreground/80 marker:text-indigo-400 marker:font-black">
								<li className="pl-2">
									<span className="font-bold">Install Resonite</span>{" "}
									<span className="text-muted-foreground">
										— Free on{" "}
										<a
											href="https://store.steampowered.com/app/2519830/Resonite/"
											target="_blank"
											rel="noopener noreferrer"
											className="text-indigo-400 hover:underline"
										>
											Steam
										</a>
									</span>
								</li>
								<li className="pl-2">
									<span className="font-bold">Enable OSC</span>{" "}
									<span className="text-muted-foreground">
										— Resonite Settings → Interface → OSC → Enable Input (port
										9000), Enable Output (port 9001)
									</span>
								</li>
								<li className="pl-2">
									<span className="font-bold">Set env vars</span>{" "}
									<span className="text-muted-foreground">
										— Copy <code>.env.example</code> to <code>.env</code>{" "}
										and set <code>RESONITE_USER_ID</code> +{" "}
										<code>RESONITE_TOKEN</code> for cloud API access
									</span>
								</li>
								<li className="pl-2">
									<span className="font-bold">Start the server</span>{" "}
									<span className="text-muted-foreground">
										— Run <code>.\web_sota\start.ps1</code> or{" "}
										<code>uv run python -m resonite_mcp --port 10979</code>
									</span>
								</li>
								<li className="pl-2">
									<span className="font-bold">Launch Resonite</span>{" "}
									<span className="text-muted-foreground">
										— Use the dashboard Launch button or start Resonite via
										Steam. The MCP tools will activate once Resonite is
										running.
									</span>
								</li>
							</ol>

							<div className="p-4 rounded-lg bg-indigo-500/5 border border-indigo-500/20">
								<div className="flex items-center gap-2 mb-2">
									<Info className="h-3.5 w-3.5 text-indigo-400" />
									<p className="text-xs font-bold text-indigo-400">
										Authentication
									</p>
								</div>
								<p className="text-xs text-muted-foreground">
									For cloud API tools (inventory, friends, messages, cloud
									variables), log in with the{" "}
									<code>resonite_rest_login</code> tool or set{" "}
									<code>RESONITE_USER_ID</code> and{" "}
									<code>RESONITE_TOKEN</code> environment variables. Token
									lasts 30 days with <code>remember_me=true</code>.
								</p>
							</div>
						</CardContent>
					</Card>

					<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
						<Card className="border-border/50 bg-card/30 glass">
							<CardContent className="p-5 space-y-2">
								<Monitor className="h-4 w-4 text-indigo-400" />
								<p className="text-xs font-bold text-foreground">
									Ports
								</p>
								<p className="text-[10px] text-muted-foreground">
									Backend: 10979 (REST + MCP)
									<br />
									Frontend: 10978 (Vite dev)
									<br />
									OSC: 9000 (send), 9001 (receive)
									<br />
									ResoniteLink: 4242 (WS)
								</p>
							</CardContent>
						</Card>
						<Card className="border-border/50 bg-card/30 glass">
							<CardContent className="p-5 space-y-2">
								<Cpu className="h-4 w-4 text-purple-400" />
								<p className="text-xs font-bold text-foreground">
									Tool Count
								</p>
								<p className="text-[10px] text-muted-foreground">
									65 tools across 12 modules
									<br />
									OSC, Session, Avatar, Inventory
									<br />
									ResoniteLink, REST API, Cloud Vars
									<br />
									vBot, Prefab Cards, Fleet
								</p>
							</CardContent>
						</Card>
						<Card className="border-border/50 bg-card/30 glass">
							<CardContent className="p-5 space-y-2">
								<Radio className="h-4 w-4 text-emerald-400" />
								<p className="text-xs font-bold text-foreground">
									Transport
								</p>
								<p className="text-[10px] text-muted-foreground">
									Stdio: Claude Desktop
									<br />
									HTTP: Webapp / Tauri
									<br />
									Dual mode: auto-detect
									<br />
									Fleet bridge: MCP_BRIDGE_URLS
								</p>
							</CardContent>
						</Card>
					</div>
				</TabsContent>

				{/* ── Beginner Guide Tab ──────────────────────────────────── */}
				<TabsContent value="beginner" className="space-y-6">
					<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
						{/* Basic Controls Card */}
						<Card className="border-border/50 bg-card/30 glass">
							<CardContent className="p-6 space-y-4">
								<div className="flex items-center gap-3">
									<Move className="h-5 w-5 text-indigo-400" />
									<h3 className="text-sm font-black text-foreground">
										Basic Controls
									</h3>
								</div>
								<div className="space-y-3 text-xs text-muted-foreground leading-relaxed">
									<p>
										Resonite has two main modes of interaction depending on your setup:
									</p>
									<div className="space-y-2 font-mono text-[11px] bg-black/30 p-3 rounded-lg border border-white/[0.03]">
										<div className="flex justify-between border-b border-white/[0.05] pb-1">
											<span className="text-slate-400">W, A, S, D</span>
											<span className="text-white">Walk around</span>
										</div>
										<div className="flex justify-between border-b border-white/[0.05] pb-1">
											<span className="text-slate-400">Mouse Move</span>
											<span className="text-white">Look around</span>
										</div>
										<div className="flex justify-between border-b border-white/[0.05] pb-1">
											<span className="text-slate-400">Left-Click (Desktop)</span>
											<span className="text-white">Interact / Click / Grab</span>
										</div>
										<div className="flex justify-between border-b border-white/[0.05] pb-1">
											<span className="text-slate-400">Right-Click (Desktop)</span>
											<span className="text-white">Open Context Menu</span>
										</div>
										<div className="flex justify-between border-b border-white/[0.05] pb-1">
											<span className="text-slate-400">Tab Key (Desktop)</span>
											<span className="text-white">Toggle Dash Menu</span>
										</div>
										<div className="flex justify-between">
											<span className="text-slate-400">VR Trigger / Grip</span>
											<span className="text-white">Click / Grab in VR</span>
										</div>
									</div>
								</div>
							</CardContent>
						</Card>

						{/* Avatars & Customization */}
						<Card className="border-border/50 bg-card/30 glass">
							<CardContent className="p-6 space-y-4">
								<div className="flex items-center gap-3">
									<User className="h-5 w-5 text-indigo-400" />
									<h3 className="text-sm font-black text-foreground">
										Finding &amp; Changing Avatars
									</h3>
								</div>
								<div className="space-y-3 text-xs text-muted-foreground leading-relaxed">
									<p>
										Avatars define your virtual appearance and biometric tracking capabilities:
									</p>
									<ul className="list-disc list-inside space-y-2">
										<li>
											<span className="font-bold text-white">Default Avatars:</span> Open the <span className="font-bold text-white">Inventory</span> tab, navigate to <span className="font-bold text-white">Resonite Essentials</span>, then open <span className="font-bold text-white">Avatars</span> to spawn default public models.
										</li>
										<li>
											<span className="font-bold text-white">Equipping:</span> Point at a spawned avatar in the world, hold your controller Grip or Right-Click (desktop) to open the context radial menu, and click the T-posing <span className="font-bold text-white">Equip</span> button.
										</li>
										<li>
											<span className="font-bold text-white">Saving:</span> Once wearing an avatar, open the Dash, navigate to your personal folder in the Inventory tab, and click <span className="font-bold text-white">Save Avatar</span>.
										</li>
									</ul>
								</div>
							</CardContent>
						</Card>

						{/* Social & Voice Chat */}
						<Card className="border-border/50 bg-card/30 glass">
							<CardContent className="p-6 space-y-4">
								<div className="flex items-center gap-3">
									<Headphones className="h-5 w-5 text-indigo-400" />
									<h3 className="text-sm font-black text-foreground">
										Voice &amp; Social Connections
									</h3>
								</div>
								<div className="space-y-3 text-xs text-muted-foreground leading-relaxed">
									<p>
										Resonite is a highly interactive social platform. Here is how to speak and connect:
									</p>
									<ul className="list-disc list-inside space-y-2">
										<li>
											<span className="font-bold text-white">Microphone Mute:</span> Press <span className="font-bold text-white">F9</span> to quickly toggle your microphone mute state, or configure push-to-talk in Settings.
										</li>
										<li>
											<span className="font-bold text-white">Text Chat:</span> Press the <span className="font-bold text-white">T</span> key on desktop to open text chat bubble overlays.
										</li>
										<li>
											<span className="font-bold text-white">Contacts Page:</span> Use the <span className="font-bold text-white">Contacts</span> tab on this dashboard to see your friends list and copy links to jump directly into their active sessions.
										</li>
									</ul>
								</div>
							</CardContent>
						</Card>

						{/* Portals & Navigation */}
						<Card className="border-border/50 bg-card/30 glass">
							<CardContent className="p-6 space-y-4">
								<div className="flex items-center gap-3">
									<Globe2 className="h-5 w-5 text-indigo-400" />
									<h3 className="text-sm font-black text-foreground">
										Portals &amp; World Travel
									</h3>
								</div>
								<div className="space-y-3 text-xs text-muted-foreground leading-relaxed">
									<p>
										Resonite worlds are connected by immersive, real-time 3D portal links:
									</p>
									<ul className="list-disc list-inside space-y-2">
										<li>
											<span className="font-bold text-white">Real-Time Previews:</span> Look through portal windows to see a live view of the destination world before crossing.
										</li>
										<li>
											<span className="font-bold text-white">Spawning Portals:</span> Open the Dash, find a world or session inside the Worlds tab, and click <span className="font-bold text-white">Spawn Portal</span>.
										</li>
										<li>
											<span className="font-bold text-white">Crossing Portals:</span> Walk directly through the portal opening to trigger loading into the target world.
										</li>
									</ul>
								</div>
							</CardContent>
						</Card>
					</div>

					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-4">
							<div className="flex items-center gap-3">
								<Wand2 className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									Troubleshooting Tips
								</h3>
							</div>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground">
								<div className="space-y-1">
									<p className="font-bold text-white">I cannot move my avatar!</p>
									<p>Ensure you do not have any menus open (press Esc). If you are stuck inside an object, try jumping (Space) or crouching (Ctrl).</p>
								</div>
								<div className="space-y-1">
									<p className="font-bold text-white">People cannot hear me!</p>
									<p>Ensure you are unmuted (press F9). Check your default audio input device inside the Settings tab of your Dash menu.</p>
								</div>
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				{/* ── Comparison & Pipeline Tab ─────────────────────────── */}
				<TabsContent value="comparison" className="space-y-6">
					{/* Platform Comparison */}
					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-4">
							<div className="flex items-center gap-3">
								<Globe2 className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									VR Platforms Comparison
								</h3>
							</div>
							<div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-4">
								<div className="space-y-2 p-4 rounded-xl bg-black/20 border border-white/[0.03]">
									<div className="flex items-center gap-2 mb-2">
										<div className="w-2 h-2 rounded-full bg-indigo-400" />
										<h4 className="text-xs font-bold text-foreground">Resonite</h4>
									</div>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Focus:</span> Real-time, in-world collaborative creation and visual programming (ProtoFlux).
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Strengths:</span> Immediate asset imports, live scripting, and bi-directional OSC integration.
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Fleet Connection:</span> Handled via the Resonite-MCP server using <strong>ResoniteLink WebSocket</strong> and bi-directional OSC.
									</p>
								</div>

								<div className="space-y-2 p-4 rounded-xl bg-black/20 border border-white/[0.03]">
									<div className="flex items-center gap-2 mb-2">
										<div className="w-2 h-2 rounded-full bg-emerald-400" />
										<h4 className="text-xs font-bold text-foreground">VRChat</h4>
									</div>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Focus:</span> Massive social communities, club events, and public worlds.
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Strengths:</span> High concurrent user count and an extensive marketplace of pre-made avatars.
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Fleet Connection:</span> Passive control via unidirectional OSC parameters and offline Unity SDK build/upload automation.
									</p>
								</div>

								<div className="space-y-2 p-4 rounded-xl bg-black/20 border border-white/[0.03]">
									<div className="flex items-center gap-2 mb-2">
										<div className="w-2 h-2 rounded-full bg-amber-400" />
										<h4 className="text-xs font-bold text-foreground">Vircadia</h4>
									</div>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Focus:</span> Open-source, self-hosted, fully decentralized domain grids.
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Strengths:</span> Native JavaScript scripting engine and server-side audio mixing.
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										<span className="font-bold text-white">Fleet Connection:</span> Automated JS script injection and domain REST management connections.
									</p>
								</div>
							</div>
						</CardContent>
					</Card>

					{/* Ecosystem & Community Resources */}
					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-4">
							<div className="flex items-center gap-3">
								<BookOpen className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									Resonite Community Resources
								</h3>
							</div>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground">
								<div className="p-4 rounded-xl bg-black/20 border border-white/[0.03] space-y-2">
									<p className="font-bold text-white">Development Tools &amp; Modding</p>
									<ul className="list-disc list-inside space-y-1">
										<li><span className="font-bold text-white">Resonite Mod Loader (RML):</span> Modding framework for custom C# client DLLs.</li>
										<li><span className="font-bold text-white">Resonite Wiki:</span> Official reference guide for ProtoFlux nodes and components.</li>
										<li><span className="font-bold text-white">ResoniteLink:</span> WebSocket bridge connecting the game engine to external APIs.</li>
									</ul>
								</div>
								<div className="p-4 rounded-xl bg-black/20 border border-white/[0.03] space-y-2">
									<p className="font-bold text-white">In-World Libraries &amp; Assets</p>
									<ul className="list-disc list-inside space-y-1">
										<li><span className="font-bold text-white">Resonite Essentials:</span> Default folder featuring avatars, building tools, and prefabs.</li>
										<li><span className="font-bold text-white">Community Depots:</span> Public world storage hosting thousands of scripts and models.</li>
										<li><span className="font-bold text-white">Blender Exporters:</span> Custom plugins streamlining asset imports.</li>
									</ul>
								</div>
							</div>
						</CardContent>
					</Card>

					{/* VR Build-and-Inhabit Fleet Pipeline */}
					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-4">
							<div className="flex items-center gap-3">
								<Zap className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									VR Build-and-Inhabit Fleet Pipeline
								</h3>
							</div>
							<p className="text-xs text-muted-foreground leading-relaxed">
								The fleet pipeline automates the lifecycle of virtual assets from external design tools straight to active inhabitance inside Resonite:
							</p>
							<div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-2">
								<div className="p-3 rounded-xl bg-black/35 border border-white/[0.03] text-center space-y-1">
									<div className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Step 1</div>
									<div className="text-xs font-bold text-white">Design &amp; Export</div>
									<p className="text-[10px] text-muted-foreground mt-1">Export meshes from Blender or textures from GIMP.</p>
								</div>
								<div className="p-3 rounded-xl bg-black/35 border border-white/[0.03] text-center space-y-1">
									<div className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Step 2</div>
									<div className="text-xs font-bold text-white">Staging Cache</div>
									<p className="text-[10px] text-muted-foreground mt-1">Assets are staged in <code>~/.avatarmcp/models/</code>.</p>
								</div>
								<div className="p-3 rounded-xl bg-black/35 border border-white/[0.03] text-center space-y-1">
									<div className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Step 3</div>
									<div className="text-xs font-bold text-white">Live Spawning</div>
									<p className="text-[10px] text-muted-foreground mt-1">ResoniteLink WebSocket spawns the asset into a slot.</p>
								</div>
								<div className="p-3 rounded-xl bg-black/35 border border-white/[0.03] text-center space-y-1">
									<div className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Step 4</div>
									<div className="text-xs font-bold text-white">OSC Inhabit</div>
									<p className="text-[10px] text-muted-foreground mt-1">OSC feeds biometrics (face, voice, eyes) into the slot.</p>
								</div>
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				{/* ── Protocols Tab ────────────────────────────────────────── */}
				<TabsContent value="protocols" className="space-y-6">
					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-6">
							<div className="flex items-center gap-3">
								<Radio className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									OSC Protocol
								</h3>
							</div>
							<p className="text-xs text-muted-foreground">
								Open Sound Control (UDP) is the primary real-time control
								protocol. Resonite listens on port 9000 for input and sends
								output on port 9001.
							</p>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div className="space-y-2">
									<p className="text-[10px] font-bold text-foreground tracking-widest uppercase">
										Avatar Control
									</p>
									<code className="block text-[10px] text-muted-foreground bg-muted/50 p-2 rounded overflow-x-auto">
										/avatar/parameters/Happy 0.8
										<br />
										/avatar/parameters/MoveX 0.15
										<br />
										/avatar/parameters/MoveY 0.0
										<br />
										/avatar/parameters/ThirdPerson 1
									</code>
								</div>
								<div className="space-y-2">
									<p className="text-[10px] font-bold text-foreground tracking-widest uppercase">
										World &amp; Inventory
									</p>
									<code className="block text-[10px] text-muted-foreground bg-muted/50 p-2 rounded overflow-x-auto">
										/resonite/world/load world_path
										<br />
										/resonite/session/start id
										<br />
										/inventory/list query_params
										<br />
										/inventory/spawn item_id
									</code>
								</div>
								<div className="space-y-2">
									<p className="text-[10px] font-bold text-foreground tracking-widest uppercase">
										vBot Control
									</p>
									<code className="block text-[10px] text-muted-foreground bg-muted/50 p-2 rounded overflow-x-auto">
										/resonite/vbot/spawn id type x y z s
										<br />
										/robot/{"{id}"}/move linear angular
										<br />
										/robot/{"{id}"}/head yaw pitch
										<br />
										/robot/{"{id}"}/stop
									</code>
								</div>
								<div className="space-y-2">
									<p className="text-[10px] font-bold text-foreground tracking-widest uppercase">
										Fleet Import
									</p>
									<code className="block text-[10px] text-muted-foreground bg-muted/50 p-2 rounded overflow-x-auto">
										/resonite/fleet/import path slot
										<br />
										/worldlabs/import world_id
									</code>
								</div>
							</div>
						</CardContent>
					</Card>

					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-6">
							<div className="flex items-center gap-3">
								<Wifi className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									ResoniteLink (WebSocket)
								</h3>
							</div>
							<p className="text-xs text-muted-foreground">
								ResoniteLink is a WebSocket-based JSON protocol (v0.8.3+) for
								direct slot/component manipulation inside Resonite. Enable it
								in Resonite: Sessions → Enable ResoniteLink (default port
								4242).
							</p>
							<div className="overflow-x-auto">
								<table className="w-full text-[10px]">
									<thead>
										<tr className="border-b border-border/50 text-left">
											<th className="p-2 font-bold text-foreground">
												Operation
											</th>
											<th className="p-2 font-bold text-foreground">
												Message Type
											</th>
											<th className="p-2 font-bold text-foreground">
												Description
											</th>
										</tr>
									</thead>
									<tbody className="text-muted-foreground">
										{[
											["Read field", "ReadField", "Read value by ref ID"],
											[
												"Write field",
												"WriteField",
												"Write value by ref ID",
											],
											["Get node", "GetNode", "Get slot/component info"],
											[
												"Get children",
												"GetChildren",
												"List child slots",
											],
											[
												"Add slot",
												"AddSlot",
												"Create child slot",
											],
											[
												"Add component",
												"AddComponent",
												"Add component to slot",
											],
											[
												"Destroy slot",
												"DestroySlot",
												"Delete slot + children",
											],
											[
												"Reflect",
												"Reflect",
												"Discover types/fields (v0.8.3+)",
											],
											[
												"Batch",
												"Batch",
												"Atomic batch (v0.8.3+)",
											],
											[
												"Import file",
												"importFile",
												"Import local asset",
											],
										].map(([op, type, desc]) => (
											<tr
												key={op}
												className="border-b border-border/20 hover:bg-muted/30"
											>
												<td className="p-2 font-bold">{op}</td>
												<td className="p-2">
													<code>{type}</code>
												</td>
												<td className="p-2">{desc}</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						</CardContent>
					</Card>

					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-6">
							<div className="flex items-center gap-3">
								<BookOpen className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									REST API (api.resonite.com)
								</h3>
							</div>
							<p className="text-xs text-muted-foreground">
								Resonite's cloud API provides authentication, session
								browsing, user lookup, inventory records, messages, friends,
								and cloud variables.
							</p>
							<div className="overflow-x-auto">
								<table className="w-full text-[10px]">
									<thead>
										<tr className="border-b border-border/50 text-left">
											<th className="p-2 font-bold text-foreground">
												Endpoint
											</th>
											<th className="p-2 font-bold text-foreground">
												Method
											</th>
											<th className="p-2 font-bold text-foreground">
												Auth
											</th>
										</tr>
									</thead>
									<tbody className="text-muted-foreground">
										{[
											["/userSessions", "POST", "login"],
											["/sessions", "GET", "No"],
											["/users/{id}", "GET", "Optional"],
											["/users/{id}/records", "GET", "Yes"],
											["/users/{id}/messages", "POST", "Yes"],
											["/users/{id}/contacts", "GET", "Yes"],
											["/users/{id}/contacts/requests", "GET", "Yes"],
											["/users/{id}/presence", "GET", "Yes"],
											["/users/{id}/vars", "GET/PUT/DELETE", "Yes"],
											["/platform", "GET", "No"],
										].map(([ep, method, auth]) => (
											<tr
												key={ep}
												className="border-b border-border/20 hover:bg-muted/30"
											>
												<td className="p-2">
													<code>{ep}</code>
												</td>
												<td className="p-2 font-bold">{method}</td>
												<td className="p-2">{auth}</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				{/* ── VR & Pico Tab ────────────────────────────────────────── */}
				<TabsContent value="vr" className="space-y-6">
					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-6 space-y-6">
							<div className="flex items-center gap-3">
								<Headphones className="h-5 w-5 text-indigo-400" />
								<h3 className="text-sm font-black text-foreground">
									VR Mode &amp; Pico HMD
								</h3>
							</div>

							<div className="space-y-4">
								<div>
									<p className="text-xs font-bold text-foreground mb-1">
										How VR mode works
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										Resonite auto-detects an active SteamVR or OpenXR runtime
										on startup. When VR is detected, Resonite renders to the
										HMD at full framerate (72/90/120Hz depending on headset)
										while the desktop window shows a spectator view. All MCP
										tools work identically in VR mode — OSC and ResoniteLink
										are process-level connections, not window-level.
									</p>
								</div>

								<div>
									<p className="text-xs font-bold text-foreground mb-1">
										Pico HMD setup
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										Pico headsets (Pico 4, Pico 4 Ultra, Neo 3) connect to
										PC VR via two methods:
									</p>
									<div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
										<div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
											<p className="text-[10px] font-bold text-emerald-400 mb-1">
												Virtual Desktop (recommended)
											</p>
											<p className="text-[10px] text-muted-foreground leading-relaxed">
												Purchase Virtual Desktop on the Pico Store, install
												the free PC streamer app. Wireless, best quality,
												lowest latency. Supports SteamVR passthrough.
												Resonite auto-launches in VR mode.
											</p>
										</div>
										<div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/20">
											<p className="text-[10px] font-bold text-blue-400 mb-1">
												Pico Connect (wired)
											</p>
											<p className="text-[10px] text-muted-foreground leading-relaxed">
												Free Pico app for USB-C or WiFi connection. Good
												alternative if Virtual Desktop is unavailable.
												Install Pico Connect on PC, then enable USB
												tethering on the headset. Resonite starts in VR
												if SteamVR is running.
											</p>
										</div>
									</div>
								</div>

								<div>
									<p className="text-xs font-bold text-foreground mb-1">
										Desktop #2 (multi-monitor)
									</p>
									<p className="text-[11px] text-muted-foreground leading-relaxed">
										Resonite opens on the primary monitor by default. To
										move it to a secondary monitor on launch: use Windows
										display settings to set your preferred monitor as
										primary before launch, or use{" "}
										<code className="text-[10px] bg-muted/50 px-1 rounded">
											Shift+Win+Arrow
										</code>{" "}
										to move the window after it opens. In VR mode, the
										desktop window is a spectator view and its position is
										cosmetic — all rendering goes to the HMD.
									</p>
								</div>

								<div>
									<p className="text-xs font-bold text-foreground mb-1">
										Troubleshooting VR
									</p>
									<ul className="text-[11px] text-muted-foreground space-y-1 list-disc pl-4">
										<li>
											Make sure SteamVR is running before launching
											Resonite
										</li>
										<li>
											Check Virtual Desktop streamer shows "Connected" on
											the PC
										</li>
										<li>
											If Resonite opens in flatscreen mode, restart
											SteamVR and re-launch
										</li>
										<li>
											For Pico Connect USB: enable Developer Mode on the
											headset, then enable USB tethering in Pico Connect
											settings
										</li>
										<li>
											The MCP server is unaffected by VR mode — all OSC
											and Link tools work regardless
										</li>
									</ul>
								</div>
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				{/* ── FAQ Tab ──────────────────────────────────────────────── */}
				<TabsContent value="faq" className="space-y-4">
					{[
						{
							q: "How do I authenticate with the Resonite API?",
							a: "Use the resonite_rest_login MCP tool with your username and password. The token is stored for 30 days. Alternatively set RESONITE_USER_ID and RESONITE_TOKEN environment variables before starting the server.",
						},
						{
							q: "How do I import a World Labs world into Resonite?",
							a: "Generate a world via worldlabs-mcp. Use resonite_rest_send_message to send the GLB URL to yourself. Inside Resonite, paste the URL into the import dialog. The server also sends an OSC /worldlabs/import message if you have an in-world OSC receiver.",
						},
						{
							q: "How does OSC control work?",
							a: "Resonite exposes an OSC interface on localhost:9000 (send) and :9001 (receive). The MCP server sends OSC messages to spawn items, trigger inventory operations, and control avatars. Enable OSC in Resonite Settings → Interface → OSC.",
						},
						{
							q: "What is ProtoFlux?",
							a: "ProtoFlux is Resonite's visual scripting system. You can programmatically create and execute scripts via the resonite_protoflux_execute tool. See the ProtoFlux page or wiki.resonite.com/ProtoFlux for the full API reference.",
						},
						{
							q: "How do I set up avatar control?",
							a: "To use virtual joysticks: 1) Set up ProtoFlux nodes listening on /avatar/parameters/MoveX and /avatar/parameters/MoveY, 2) Drive your character controller velocity, 3) For perspective toggle, listen to /avatar/parameters/ThirdPerson. See the Control page for setup.",
						},
						{
							q: "What is ResoniteLink and when should I use it?",
							a: "ResoniteLink is a WebSocket JSON protocol for direct slot/component CRUD in Resonite. Use it when you need fine-grained world manipulation (create/destroy slots, read/write component fields). Enable it in Resonite: Sessions → Enable ResoniteLink, default port 4242.",
						},
						{
							q: "How do cloud variables work?",
							a: "Cloud variables are key-value pairs stored on api.resonite.com. They persist across sessions and can be shared between worlds. Use resonite_cloud_var_list/get/set/delete tools. Requires authentication via resonite_rest_login or RESONITE_TOKEN env var.",
						},
						{
							q: "What are the vBot tools?",
							a: "vBot tools control virtual robots inside Resonite via OSC. Supported types: yahboom (vBoomy wheeled), mechazilla (vMechazilla creative), bumi (biped), godzilla (kaiju scale), and custom. Build the OSC receiver ProtoFlux graph in your world (see docs/VBOT_OSC_RECEIVER.md).",
						},
						{
							q: "How do fleet integrations work?",
							a: "The resonite_fleet tool pulls assets from other MCP servers (blender-mcp, gimp-mcp, inkscape-mcp, worldlabs-mcp) and imports them into Resonite. Use the Integrations page or call resonite_fleet directly with the desired operation.",
						},
					].map(({ q, a }, i) => (
						<Card
							key={i}
							className="border-border/50 bg-card/30 glass hover:border-indigo-500/20 transition-all"
						>
							<CardContent className="p-5 space-y-2">
								<p className="text-sm font-bold text-foreground">{q}</p>
								<p className="text-xs text-muted-foreground leading-relaxed">
									{a}
								</p>
							</CardContent>
						</Card>
					))}
				</TabsContent>

				{/* ── Links Tab ────────────────────────────────────────────── */}
				<TabsContent value="links" className="space-y-4">
					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<RefCard
							title="Resonite Wiki API"
							desc="REST API endpoint reference"
							href="https://wiki.resonite.com/API"
						/>
						<RefCard
							title="Resonite Discord"
							desc="Community support and updates"
							href="https://discord.gg/resonite"
						/>
						<RefCard
							title="OSC Documentation"
							desc="OSC protocol in Resonite"
							href="https://wiki.resonite.com/OSC"
						/>
						<RefCard
							title="ProtoFlux Guide"
							desc="Visual scripting reference"
							href="https://wiki.resonite.com/ProtoFlux"
						/>
						<RefCard
							title="ResoniteLink GitHub"
							desc="WebSocket protocol source"
							href="https://github.com/Yellow-Dog-Man/ResoniteLink"
						/>
						<RefCard
							title="Resonite Steam"
							desc="Install or launch Resonite"
							href="steam://install/2519830"
						/>
						<RefCard
							title="Virtual Desktop"
							desc="Pico PC VR streaming"
							href="https://www.vrdesktop.net/"
						/>
						<RefCard
							title="Pico Connect"
							desc="Official Pico PC streaming"
							href="https://www.picoxr.com/global/software/pico-connect"
						/>
					</div>

					<Card className="border-border/50 bg-card/30 glass">
						<CardContent className="p-5 space-y-3">
							<div className="flex items-center gap-2">
								<HelpCircle className="h-4 w-4 text-indigo-400" />
								<h3 className="text-xs font-black text-foreground tracking-widest">
									Need more help?
								</h3>
							</div>
							<p className="text-xs text-muted-foreground leading-relaxed">
								Check the Resonite Discord for real-time help, or consult the
								resonite-mcp repository documentation at{" "}
								<a
									href="https://github.com/sandraschi/resonite-mcp"
									target="_blank"
									rel="noopener noreferrer"
									className="text-indigo-400 hover:underline"
								>
									github.com/sandraschi/resonite-mcp
								</a>
								. Fleet-wide standards are at{" "}
								<a
									href="https://github.com/sandraschi/mcp-central-docs"
									target="_blank"
									rel="noopener noreferrer"
									className="text-indigo-400 hover:underline"
								>
									mcp-central-docs
								</a>
								.
							</p>
						</CardContent>
					</Card>
				</TabsContent>
			</Tabs>
		</div>
	);
}
