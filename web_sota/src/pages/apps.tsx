import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { LayoutGrid, Plus, Search } from "lucide-react";

export function Apps() {
	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold text-white">App Hub</h1>
					<p className="text-slate-400">
						Discover and manage connected Resonite-MCP extensions.
					</p>
				</div>
				<Button className="bg-indigo-600 hover:bg-indigo-700">
					<Plus className="mr-2 h-4 w-4" />
					Register App
				</Button>
			</div>

			<div className="relative">
				<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
				<Input
					placeholder="Search apps and extensions..."
					className="pl-10 border-indigo-500/20 bg-indigo-500/5 text-slate-200"
				/>
			</div>

			<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
				<Card className="border-indigo-500/20 bg-indigo-500/10 hover:border-indigo-500/40 transition-colors">
					<CardHeader className="flex flex-row items-center gap-4 pb-2 text-white">
						<div className="rounded-lg bg-indigo-500/20 p-2">
							<LayoutGrid className="h-6 w-6 text-indigo-400" />
						</div>
						<CardTitle className="text-lg">Object Spawner</CardTitle>
					</CardHeader>
					<CardContent>
						<p className="text-sm text-slate-400">
							Automated spawning tool for ProtoFlux components.
						</p>
						<div className="mt-4 flex gap-2">
							<Button
								variant="secondary"
								size="sm"
								className="bg-white/5 text-slate-200 hover:bg-white/10 border-0"
							>
								Launch
							</Button>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
