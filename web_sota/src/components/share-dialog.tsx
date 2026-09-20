import { Loader2, Share2, X } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/common/utils";
import { apiUrl } from "@/lib/api-base";

interface ShareDialogProps {
	itemId: string;
	itemName: string;
	onClose: () => void;
}

function namesFrom(payload: unknown): string[] | null {
	// /api/contacts returns a raw friend list when authenticated, an error
	// dict otherwise. Friend objects vary; accept username/name/id.
	if (!Array.isArray(payload)) return null;
	const out: string[] = [];
	for (const entry of payload as Array<Record<string, unknown>>) {
		if (typeof entry === "string") {
			out.push(entry);
			continue;
		}
		if (entry && typeof entry === "object") {
			const name = entry.username ?? entry.name ?? entry.userName ?? entry.id;
			if (typeof name === "string" && name) out.push(name);
		}
	}
	return out;
}

export function ShareDialog({ itemId, itemName, onClose }: ShareDialogProps) {
	const [contacts, setContacts] = useState<string[] | null | undefined>(
		undefined,
	);
	const [picked, setPicked] = useState("");
	const [manual, setManual] = useState("");
	const [permission, setPermission] = useState("read");
	const [sending, setSending] = useState(false);
	const [result, setResult] = useState<{
		ok: boolean;
		message: string;
	} | null>(null);

	useEffect(() => {
		let cancelled = false;
		fetch(apiUrl("/api/contacts"))
			.then((r) => (r.ok ? r.json() : null))
			.then((data) => {
				if (!cancelled) setContacts(data ? namesFrom(data) : null);
			})
			.catch(() => {
				if (!cancelled) setContacts(null);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	const recipient = (picked || manual).trim();

	const handleShare = async () => {
		if (!recipient || sending) return;
		setSending(true);
		setResult(null);
		try {
			const res = await fetch(apiUrl("/api/resonite/inventory/share"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					item_id: itemId,
					share_with: recipient,
					permission_level: permission,
				}),
			});
			const data = (await res.json().catch(() => null)) as {
				detail?: string;
				message?: string;
			} | null;
			if (!res.ok) throw new Error(data?.detail || "Share failed");
			setResult({
				ok: true,
				message: data?.message || `Share request sent to ${recipient}.`,
			});
		} catch (error) {
			setResult({
				ok: false,
				message: error instanceof Error ? error.message : "Share failed.",
			});
		} finally {
			setSending(false);
		}
	};

	return (
		<div
			className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
			role="dialog"
			aria-modal="true"
			aria-label={`Share ${itemName}`}
			onClick={(e) => {
				if (e.target === e.currentTarget) onClose();
			}}
			onKeyDown={(e) => {
				if (e.key === "Escape") onClose();
			}}
		>
			<div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md space-y-4">
				<div className="flex items-center justify-between">
					<h3 className="text-sm font-bold text-white flex items-center gap-2">
						<Share2 className="w-4 h-4 text-indigo-400" />
						Share &ldquo;{itemName}&rdquo;
					</h3>
					<button
						onClick={onClose}
						title="Close"
						aria-label="Close share dialog"
						className="p-1 text-slate-500 hover:text-slate-300"
					>
						<X className="w-4 h-4" />
					</button>
				</div>

				{contacts === undefined ? (
					<p className="text-xs text-slate-500 flex items-center gap-2">
						<Loader2 className="w-3.5 h-3.5 animate-spin" />
						Loading contacts…
					</p>
				) : contacts && contacts.length > 0 ? (
					<div>
						<p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
							Pick a contact
						</p>
						<div className="max-h-44 overflow-y-auto space-y-1 pr-1">
							{contacts.map((name) => (
								<button
									key={name}
									onClick={() => {
										setPicked(name);
										setManual("");
									}}
									aria-pressed={picked === name}
									className={cn(
										"w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
										picked === name
											? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
											: "text-slate-300 hover:bg-white/5 border border-transparent",
									)}
								>
									{name}
								</button>
							))}
						</div>
					</div>
				) : (
					<div>
						<p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
							Contacts need login — enter a username
						</p>
						<input
							type="text"
							value={manual}
							onChange={(e) => {
								setManual(e.target.value);
								setPicked("");
							}}
							placeholder="Resonite username"
							aria-label="Resonite username to share with"
							className="w-full bg-black/20 border border-white/[0.08] rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50"
						/>
					</div>
				)}

				<div>
					<p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
						Permission
					</p>
					<div className="flex gap-2">
						{["read", "write", "admin"].map((level) => (
							<button
								key={level}
								onClick={() => setPermission(level)}
								aria-pressed={permission === level}
								className={cn(
									"flex-1 px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors border",
									permission === level
										? "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"
										: "text-slate-500 hover:text-slate-300 border-transparent hover:bg-white/5",
								)}
							>
								{level}
							</button>
						))}
					</div>
				</div>

				{result && (
					<p
						role="status"
						className={cn(
							"text-xs",
							result.ok ? "text-emerald-400" : "text-rose-400",
						)}
					>
						{result.message}
					</p>
				)}

				<div className="flex gap-3 justify-end">
					<button
						onClick={onClose}
						className="px-4 py-2 rounded-xl border border-slate-700 text-slate-400 text-sm hover:bg-slate-800"
					>
						{result?.ok ? "Done" : "Cancel"}
					</button>
					<button
						onClick={handleShare}
						disabled={!recipient || sending}
						className="px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 text-white text-sm font-bold flex items-center gap-2"
					>
						{sending && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
						{sending ? "Sharing…" : "Share"}
					</button>
				</div>
			</div>
		</div>
	);
}
