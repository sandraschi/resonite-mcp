import { useState } from "react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";
// import { Toaster } from '@/components/ui/toaster';

interface AppLayoutProps {
	children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
	const [collapsed, setCollapsed] = useState(() => {
		const stored = localStorage.getItem("sidebar-collapsed");
		return stored !== null ? stored === "true" : false;
	});

	const handleToggle = () => {
		const newState = !collapsed;
		setCollapsed(newState);
		localStorage.setItem("sidebar-collapsed", String(newState));
	};

	return (
		<div className="flex min-h-screen flex-col bg-background text-foreground selection:bg-indigo-500/30">
			<div className="flex flex-1 overflow-hidden">
				<Sidebar collapsed={collapsed} onToggle={handleToggle} />
				<div className="flex flex-1 flex-col overflow-hidden">
					<Topbar />
					<main className="flex-1 overflow-y-auto p-6 scroll-smooth">
						<div className="mx-auto max-w-7xl page-enter">{children}</div>
					</main>
				</div>
			</div>
			{/* <Toaster /> */}
		</div>
	);
}
