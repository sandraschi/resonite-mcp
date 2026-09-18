import { apiUrl } from "@/lib/api-base";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
	AlertTriangle,
	Eye,
	Move,
	RefreshCw,
	Sliders,
	User,
} from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "../common/utils";

interface Channel {
	name: string;
	kind: "number" | "boolean";
}

interface AvatarInfo {
	status: string;
	live: boolean;
	name: string | null;
	id: string | null;
	username?: string | null;
	userCount?: number;
	isEquipped: boolean | null;
	detail?: string;
	channels: Channel[];
}

type ChannelValues = Record<string, number | boolean>;

export function AvatarPage() {
	const [values, setValues] = useState<ChannelValues>({});

	const {
		data: avatarInfo,
		isLoading,
		isError,
		refetch,
		isRefetching,
	} = useQuery({
		queryKey: ["avatar"],
		queryFn: async (): Promise<AvatarInfo> => {
			const r = await fetch(apiUrl("/api/resonite/avatar/info"));
			if (!r.ok) throw new Error(`Avatar info failed: ${r.status}`);
			return r.json();
		},
	});

	useEffect(() => {
		if (avatarInfo?.channels) {
			setValues((prev) => {
				const next = { ...prev };
				for (const c of avatarInfo.channels) {
					if (!(c.name in next)) next[c.name] = c.kind === "boolean" ? false : 0;
				}
				return next;
			});
		}
	}, [avatarInfo]);

	const setParamMutation = useMutation({
		mutationFn: async ({
			param,
			value,
		}: { param: string; value: string | number | boolean }) => {
			const r = await fetch(apiUrl("/api/resonite/avatar/set_parameter"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ parameter: param, value }),
			});
			return r.json();
		},
	});

	const resetPoseMutation = useMutation({
		mutationFn: async () => {
			const r = await fetch(apiUrl("/api/resonite/avatar/reset_pose"), {
				method: "POST",
			});
			return r.json();
		},
	});

	const locomotionMutation = useMutation({
		mutationFn: async (type: string) => {
			const r = await fetch(apiUrl("/api/resonite/avatar/locomotion"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ type }),
			});
			return r.json();
		},
	});

	const killSequencesMutation = useMutation({
		mutationFn: async () => {
			const r = await fetch(apiUrl("/api/resonite/avatar/kill_sequences"), {
				method: "POST",
			});
			return r.json();
		},
	});

	const sendChannel = (name: string, value: number | boolean) => {
		setValues((prev) => ({ ...prev, [name]: value }));
		setParamMutation.mutate({ param: name, value });
	};

	return (
		<div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
			{/* Hero: what this page actually is */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-1">
				<div className="flex items-center gap-4">
					<div className="relative">
						<div className="absolute -inset-1 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-2xl blur opacity-25 transition duration-1000" />
						<div className="relative bg-slate-900/50 p-3 rounded-2xl border border-white/10">
							<User className="w-7 h-7 text-purple-400" />
						</div>
					</div>
					<div>
						<h2 className="text-2xl font-bold text-white tracking-tight">
							Avatar
						</h2>
						<p className="text-sm text-slate-400 max-w-md">
							Send-only avatar controls for the linked session: parameter
							channels, locomotion and pose. Values are transmitted, never
							read back.
						</p>
					</div>
				</div>
				<div className="flex items-center gap-3">
					<span
						className={cn(
							"flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest px-3 py-1.5 rounded-full border",
							avatarInfo?.live
								? "text-emerald-400 border-emerald-500/30 bg-emerald-500/10"
								: "text-amber-400 border-amber-500/30 bg-amber-500/10",
						)}
						title={
							avatarInfo?.live
								? "Backend reports live avatar readings"
								: "No live readback: controls send, nothing is measured"
						}
					>
						<span
							className={cn(
								"w-1.5 h-1.5 rounded-full animate-pulse",
								avatarInfo?.live ? "bg-emerald-400" : "bg-amber-400",
							)}
						/>
						{avatarInfo?.live ? "Live" : "Send-only"}
					</span>
					<button
						onClick={() => refetch()}
						disabled={isLoading || isRefetching}
						title="Refresh Avatar Data"
						className="p-2.5 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-all border border-transparent hover:border-white/10 active:scale-95 disabled:opacity-50"
					>
						<RefreshCw
							className={cn(
								"w-5 h-5",
								(isLoading || isRefetching) && "animate-spin",
							)}
						/>
					</button>
				</div>
			</div>

			{isError && (
				<div className="glass-card p-5 rounded-3xl border-red-500/30 flex items-center gap-3 text-sm text-red-300">
					<AlertTriangle className="w-5 h-5 flex-shrink-0" />
					Could not load the avatar control surface. Is the backend running?
				</div>
			)}

			{/* Identity: honest about what is (not) known */}
			<div className="glass-card p-5 rounded-3xl border-white/10 flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
				<div className="flex items-center gap-3">
					<div className="p-2 rounded-xl bg-white/5 border border-white/10">
						<User className="w-5 h-5 text-slate-400" />
					</div>
					<div>
						<p className="text-sm font-bold text-white">
							{avatarInfo?.name ?? "Unknown avatar"}
						</p>
						<p className="text-xs text-slate-500 font-mono">
							{avatarInfo?.id ??
								(avatarInfo?.username
									? `linked user ${avatarInfo.username} · avatar object not exposed by ResoniteLink`
									: "equipped-avatar readback not implemented")}
						</p>
					</div>
				</div>
				<a
					href="/resonite-link"
					className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
				>
					Manage link →
				</a>
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
				{/* Parameter channels */}
				<div className="lg:col-span-8">
					<div className="glass-card p-1 rounded-3xl border-white/10 bg-white/[0.01]">
						<div className="p-6">
							<div className="flex items-center justify-between mb-8">
								<div className="flex items-center gap-3">
									<div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20">
										<Sliders className="w-5 h-5 text-purple-400" />
									</div>
									<div>
										<h3 className="font-bold text-white text-lg tracking-tight">
											Parameter channels
										</h3>
										<p className="text-xs text-slate-500">
											One-way sends over OSC. No delivery confirmation,
											no readback.
										</p>
									</div>
								</div>
							</div>

							<div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
								{(avatarInfo?.channels ?? []).map((channel) => {
									const value = values[channel.name] ?? (channel.kind === "boolean" ? false : 0);
									return (
										<div
											key={channel.name}
											className="relative p-5 rounded-2xl border transition-all duration-300 bg-black/40 border-white/[0.05] hover:border-white/20 hover:bg-white/[0.02]"
										>
											<div className="flex items-center justify-between mb-4">
												<div className="flex flex-col">
													<span className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-0.5">
														{channel.name}
													</span>
													<span className="text-xs font-mono text-slate-500">
														{typeof value === "boolean"
															? value
																? "ON"
																: "OFF"
															: value}
													</span>
												</div>
												{typeof value === "number" && (
													<div className="text-xs font-mono p-1 bg-purple-500/10 text-purple-400 rounded px-2 border border-purple-500/20">
														{(value * 100).toFixed(0)}%
													</div>
												)}
											</div>

											{typeof value === "number" && (
												<input
													type="range"
													min="0"
													max="1"
													step="0.01"
													value={value}
													title={`Send ${channel.name}`}
													aria-label={`Send ${channel.name}`}
													onChange={(e) =>
														sendChannel(channel.name, Number.parseFloat(e.target.value))
													}
													className="w-full h-1 bg-white/5 rounded-full appearance-none cursor-pointer accent-purple-500 hover:accent-purple-400"
												/>
											)}

											{typeof value === "boolean" && (
												<button
													onClick={() => sendChannel(channel.name, !value)}
													className={cn(
														"w-full py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border",
														value
															? "bg-purple-500/20 border-purple-500/30 text-purple-400"
															: "bg-white/5 border-white/10 text-slate-500 hover:bg-white/10",
													)}
												>
													{value ? "Send OFF" : "Send ON"}
												</button>
											)}
										</div>
									);
								})}
							</div>
						</div>
					</div>
				</div>

				{/* Locomotion, pose, sequences */}
				<div className="lg:col-span-4 space-y-6">
					<div className="glass-card p-6 space-y-5 rounded-3xl border-white/10">
						<div className="flex items-center gap-3 text-indigo-400">
							<div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
								<Move className="w-5 h-5" />
							</div>
							<h3 className="text-xs font-black uppercase tracking-[0.2em]">
								Locomotion & pose
							</h3>
						</div>
						<div className="grid grid-cols-2 gap-2">
							<button
								onClick={() => locomotionMutation.mutate("walk")}
								title="Walk mode (fire-and-forget)"
								className="bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 rounded-2xl py-3 text-xs font-bold uppercase tracking-widest text-slate-300 transition-all"
							>
								Walk
							</button>
							<button
								onClick={() => locomotionMutation.mutate("fly")}
								title="Fly mode (fire-and-forget)"
								className="bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 rounded-2xl py-3 text-xs font-bold uppercase tracking-widest text-slate-300 transition-all"
							>
								Fly
							</button>
						</div>
						<button
							onClick={() => resetPoseMutation.mutate()}
							className="w-full bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 rounded-2xl py-3 text-xs font-bold uppercase tracking-widest text-slate-300 transition-all"
						>
							Reset pose
						</button>
					</div>

					<div className="glass-card p-6 space-y-4 rounded-3xl border-white/10">
						<div className="flex items-center gap-3 text-orange-400">
							<div className="p-2 rounded-xl bg-orange-500/10 border border-orange-500/20">
								<Eye className="w-5 h-5" />
							</div>
							<h3 className="text-xs font-black uppercase tracking-[0.2em]">
								Sequences
							</h3>
						</div>
						<p className="text-xs text-slate-500">
							Stop-all command. Sent blind; the backend cannot list what is
							actually running.
						</p>
						<button
							onClick={() => killSequencesMutation.mutate()}
							className="w-full px-8 py-3 bg-white text-black rounded-2xl font-black text-xs uppercase tracking-[0.2em] hover:bg-slate-200 transition-all active:scale-95"
						>
							Kill all sequences
						</button>
					</div>
				</div>
			</div>
		</div>
	);
}
