import { APPS_CATALOG } from "@/common/apps-catalog";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ExternalLink, HelpCircle, LayoutGrid, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

// EXPERIMENTAL light mode (invert hack). Not fleet standard — see index.css.
// Toggling `.dark` off the root flips the invert filter; persisted so the
// choice survives reloads. Delete this + the CSS block to revert.
const THEME_KEY = "resonite-light-mode";

function useExperimentalTheme() {
	const [light, setLight] = useState(() => {
		try {
			return localStorage.getItem(THEME_KEY) === "1";
		} catch {
			return false;
		}
	});

	useEffect(() => {
		document.documentElement.classList.toggle("dark", !light);
		try {
			localStorage.setItem(THEME_KEY, light ? "1" : "0");
		} catch {
			// ignore storage errors
		}
	}, [light]);

	return { light, toggle: () => setLight((v) => !v) };
}

export function Topbar() {
	const { light, toggle } = useExperimentalTheme();
	return (
		<header className="flex h-14 items-center justify-between border-b border-border bg-background/50 px-6 backdrop-blur-xl">
			<div className="flex items-center gap-4">
				<h1 className="text-sm font-medium text-muted-foreground uppercase tracking-widest text-[10px]">
					Intelligence /{" "}
					<span className="text-foreground font-bold">Control Center</span>
				</h1>
			</div>

			<div className="flex items-center gap-2">
				<button
					type="button"
					onClick={toggle}
					className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground transition-all duration-300 glass"
					title={light ? "Switch to dark (experimental light mode)" : "Switch to light (experimental, ugly)"}
					aria-label="Toggle light mode (experimental)"
				>
					{light ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
				</button>

				{/* System Status Indicator */}
				<div className="mr-4 flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-500 border border-emerald-500/20 glass">
					<span className="relative flex h-2 w-2">
						<span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
						<span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
					</span>
					System Online
				</div>

				{/* Global Apps Navigation */}
				<DropdownMenu.Root>
					<DropdownMenu.Trigger asChild>
						<button className="flex items-center gap-2 rounded-md border border-border bg-muted/50 px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-foreground hover:bg-muted transition-all duration-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 glass">
							<LayoutGrid className="h-3.5 w-3.5" />
							Fleet
						</button>
					</DropdownMenu.Trigger>

					<DropdownMenu.Portal>
						<DropdownMenu.Content
							className="z-50 min-w-[220px] animate-in fade-in zoom-in-95 data-[side=bottom]:slide-in-from-top-2 rounded-lg border border-border bg-background p-1 shadow-2xl glass"
							sideOffset={5}
							align="end"
						>
							<DropdownMenu.Label className="px-2 py-1.5 text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] opacity-50">
								Switch Console
							</DropdownMenu.Label>

							<div className="h-px bg-border my-1" />

							{APPS_CATALOG.map((app) => (
								<DropdownMenu.Item key={app.id} asChild>
									<a
										href={app.url}
										className="flex w-full select-none items-center rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-indigo-500/10 hover:text-foreground focus:bg-indigo-500/10 focus:text-foreground outline-none cursor-pointer transition-colors duration-200"
									>
										<app.icon className="mr-2 h-4 w-4 text-muted-foreground" />
										<span>{app.label}</span>
										<ExternalLink className="ml-auto h-3 w-3 opacity-30 group-hover:opacity-100" />
									</a>
								</DropdownMenu.Item>
							))}
						</DropdownMenu.Content>
					</DropdownMenu.Portal>
				</DropdownMenu.Root>

				<button
					className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground transition-all duration-300 glass"
					title="System Help"
				>
					<HelpCircle className="h-4 w-4" />
				</button>
			</div>
		</header>
	);
}
