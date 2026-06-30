import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";
import { useQuery } from "@tanstack/react-query";
import {
	Globe2,
	MessageCircle,
	Search,
	UserCheck,
	UserX,
	Users,
} from "lucide-react";
import { useState } from "react";

interface Contact {
	id: string;
	contactUsername?: string;
	contactStatus?: string;
	isAccepted?: boolean;
	latestMessageTime?: string;
	profile?: {
		iconUrl?: string;
	};
	userStatus?: {
		onlineStatus?: string;
		currentSessionId?: string;
		currentSessionAccessLevel?: string;
	};
}

async function fetchContacts(): Promise<Contact[]> {
	const r = await fetch(apiUrl("/api/contacts"));
	if (!r.ok) throw new Error(`${r.status}: ${r.statusText}`);
	return r.json() as Promise<Contact[]>;
}

function statusColor(status?: string) {
	switch (status?.toLowerCase()) {
		case "online":
			return "bg-emerald-400";
		case "away":
			return "bg-amber-400";
		case "busy":
			return "bg-red-400";
		default:
			return "bg-slate-600";
	}
}

export function Contacts() {
	const [search, setSearch] = useState("");
	const [tab, setTab] = useState<"all" | "online">("all");

	const { data, isLoading, isError, error } = useQuery({
		queryKey: ["contacts"],
		queryFn: fetchContacts,
		refetchInterval: 60_000,
	});

	const contacts = (data ?? []).filter(
		(c) =>
			(tab === "all" ||
				c.userStatus?.onlineStatus?.toLowerCase() === "online") &&
			(c.contactUsername ?? "").toLowerCase().includes(search.toLowerCase()),
	);

	return (
		<div className="space-y-6 page-enter">
			<div className="flex items-center gap-3">
				<Users className="w-5 h-5 text-indigo-400" aria-hidden="true" />
				<div>
					<h2 className="text-lg font-bold gradient-text">Contacts</h2>
					<p className="text-sm text-slate-500">
						Your Resonite friends &amp; social connections
					</p>
				</div>
			</div>

			{/* Filter bar */}
			<div className="glass-card p-3 flex flex-wrap gap-2 items-center">
				<div className="flex gap-1 bg-black/20 rounded-lg p-1">
					{(["all", "online"] as const).map((t) => (
						<button
							key={t}
							onClick={() => setTab(t)}
							aria-pressed={tab === t ? "true" : "false"}
							className={cn(
								"px-3 py-1 rounded-md text-xs font-medium capitalize transition-all",
								tab === t
									? "bg-indigo-600 text-white"
									: "text-slate-500 hover:text-slate-300",
							)}
						>
							{t}
						</button>
					))}
				</div>
				<div className="flex items-center gap-1.5 flex-1 min-w-[10rem] bg-white/[0.04] border border-white/[0.08] rounded-lg px-2.5 py-1.5">
					<Search className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
					<input
						type="search"
						value={search}
						onChange={(e) => setSearch(e.target.value)}
						placeholder="Search contacts…"
						className="bg-transparent text-xs text-slate-200 outline-none placeholder-slate-600 flex-1"
						aria-label="Search contacts"
					/>
				</div>
			</div>

			{/* Auth error */}
			{isError && (
				<div className="glass-card p-4 border border-amber-500/20 bg-amber-500/10">
					<p className="text-sm text-amber-300">
						{String(error).includes("401") || String(error).includes("403")
							? "Authentication required. Set RESONITE_USER_ID + RESONITE_TOKEN or call resonite_rest_login."
							: `Error loading contacts: ${String(error)}`}
					</p>
				</div>
			)}

			{isLoading && <p className="text-sm text-slate-600">Loading contacts…</p>}

			{/* Contacts list */}
			<div className="space-y-2">
				{contacts.map((c) => {
					const online = c.userStatus?.onlineStatus;
					const inSession = !!c.userStatus?.currentSessionId;
					return (
						<div key={c.id} className="glass-card p-3 flex items-center gap-3">
							{/* Avatar */}
							<div className="relative flex-shrink-0">
								{c.profile?.iconUrl ? (
									<img
										src={c.profile.iconUrl}
										alt={c.contactUsername ?? "contact"}
										className="w-10 h-10 rounded-full object-cover"
									/>
								) : (
									<div className="w-10 h-10 rounded-full bg-indigo-900/50 flex items-center justify-center text-indigo-300 text-sm font-bold">
										{(c.contactUsername ?? "?").charAt(0).toUpperCase()}
									</div>
								)}
								<span
									className={cn(
										"absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-slate-900",
										statusColor(online),
									)}
									aria-label={online ?? "offline"}
								/>
							</div>

							{/* Info */}
							<div className="flex-1 min-w-0">
								<p className="text-sm font-medium text-slate-100 truncate">
									{c.contactUsername ?? c.id}
								</p>
								<div className="flex items-center gap-2 text-xs text-slate-500">
									{inSession && (
										<>
											<Globe2
												className="w-3 h-3 text-indigo-400"
												aria-hidden="true"
											/>
											<span className="text-indigo-400">In a session</span>
										</>
									)}
									{!inSession && <span>{online ?? "Offline"}</span>}
								</div>
							</div>

							{/* Status icon */}
							<div className="flex-shrink-0">
								{c.isAccepted ? (
									<UserCheck
										className="w-4 h-4 text-emerald-500"
										aria-label="Friend"
									/>
								) : (
									<UserX
										className="w-4 h-4 text-slate-600"
										aria-label="Pending"
									/>
								)}
							</div>

							{/* Jump to session */}
							{inSession && (
								<button
									className="flex items-center gap-1 px-2 py-1 rounded-md bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/30 text-xs text-indigo-300 transition-all"
									aria-label={`Join ${c.contactUsername ?? "contact"}'s session`}
									onClick={() =>
										navigator.clipboard.writeText(
											`res-session:///${c.userStatus?.currentSessionId ?? ""}`,
										)
									}
								>
									<MessageCircle className="w-3 h-3" aria-hidden="true" />
									Copy Link
								</button>
							)}
						</div>
					);
				})}

				{contacts.length === 0 && !isLoading && !isError && (
					<div className="text-center py-12 text-slate-600">
						<Users
							className="w-10 h-10 mx-auto mb-3 opacity-30"
							aria-hidden="true"
						/>
						<p className="text-sm">
							{tab === "online"
								? "No contacts online right now"
								: "No contacts found"}
						</p>
					</div>
				)}
			</div>
		</div>
	);
}
