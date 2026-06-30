import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/common/utils";
import {
	BookOpen,
	ExternalLink,
	HelpCircle,
	Info,
	MessageSquare,
	Radio,
	Wifi,
	Zap,
	Monitor,
	Headphones,
	Cpu,
} from "lucide-react";

function ExtLink({ href, label }: { href: string; label: string }) {
	return (
		<a
			href={href}
			target="_blank"
			rel="noopener noreferrer"
			className="inline-flex items-center gap-1 text-indigo-400 hover:text-indigo-300 text-xs font-bold"
		>
			{label} <ExternalLink className="h-3 w-3" />
		</a>
	);
}

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
						{ id: "protocols", label: "Protocols" },
						{ id: "vr", label: "VR &amp; Pico" },
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
