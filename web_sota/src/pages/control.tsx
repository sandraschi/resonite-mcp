import { apiUrl } from "@/lib/api-base";
import { useMutation } from "@tanstack/react-query";
import { Eye, EyeOff, Gamepad2, Info } from "lucide-react";
import nipplejs from "nipplejs";
import { useCallback, useEffect, useRef, useState } from "react";

export function Control() {
	const [viewType, setViewType] = useState<"first-person" | "third-person">(
		"first-person",
	);
	const [lastMove, setLastMove] = useState({ x: 0, y: 0 });
	const leftJoystickRef = useRef<HTMLDivElement>(null);
	const rightJoystickRef = useRef<HTMLDivElement>(null);

	const moveMutation = useMutation({
		mutationFn: async (move: { x: number; y: number }) => {
			const resp = await fetch(apiUrl("/api/control/move"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(move),
			});
			return resp.json();
		},
	});

	const viewMutation = useMutation({
		mutationFn: async (type: string) => {
			const resp = await fetch(apiUrl("/api/control/view"), {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ view_type: type }),
			});
			return resp.json();
		},
	});

	// Throttled movement sender
	const moveTimer = useRef<number | null>(null);
	const sendMove = useCallback(
		(x: number, y: number) => {
			if (moveTimer.current) return;

			moveTimer.current = window.setTimeout(() => {
				moveMutation.mutate({ x, y });
				moveTimer.current = null;
			}, 100); // 10Hz movement updates
		},
		[moveMutation],
	);

	useEffect(() => {
		if (!leftJoystickRef.current || !rightJoystickRef.current) return;

		const leftManager = nipplejs.create({
			zone: leftJoystickRef.current,
			mode: "static",
			position: { left: "50%", top: "50%" },
			color: "#6366f1",
			size: 150,
		});

		const rightManager = nipplejs.create({
			zone: rightJoystickRef.current,
			mode: "static",
			position: { left: "50%", top: "50%" },
			color: "#ec4899",
			size: 150,
		});

		leftManager.on("move", (_evt, data) => {
			const x = data.vector.x;
			const y = data.vector.y;
			setLastMove({ x, y });
			sendMove(x, y);
		});

		leftManager.on("end", () => {
			setLastMove({ x: 0, y: 0 });
			moveMutation.mutate({ x: 0, y: 0 });
		});

		// Right joystick could be for rotation/look if implemented in backend
		// For now we only use left for movement.

		return () => {
			leftManager.destroy();
			rightManager.destroy();
		};
	}, [moveMutation, sendMove]);

	const toggleView = () => {
		const next = viewType === "first-person" ? "third-person" : "first-person";
		setViewType(next);
		viewMutation.mutate(next);
	};

	return (
		<div className="space-y-6">
			<header className="flex flex-col gap-2">
				<div className="flex items-center gap-3">
					<div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 shadow-lg shadow-indigo-500/10">
						<Gamepad2 className="h-6 w-6" />
					</div>
					<div>
						<h1 className="text-2xl font-bold tracking-tight text-foreground">
							Avatar Control
						</h1>
						<p className="text-sm text-muted-foreground">
							Virtual joysticks for mobile or desktop remote control.
						</p>
					</div>
				</div>
			</header>

			<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
				{/* Information Card */}
				<div className="lg:col-span-3 rounded-2xl border border-border bg-card/30 p-4 backdrop-blur-md">
					<div className="flex items-start gap-3">
						<div className="mt-0.5 rounded-full bg-blue-500/10 p-1.5 text-blue-400">
							<Info className="h-4 w-4" />
						</div>
						<div className="space-y-1">
							<h4 className="text-sm font-semibold text-foreground">
								ProtoFlux Setup Required
							</h4>
							<p className="text-xs text-muted-foreground leading-relaxed">
								To use these controls, your avatar must have a ProtoFlux setup
								listening for 'MoveX', 'MoveY', and 'ThirdPerson' parameters.
								See the{" "}
								<a href="/help" className="text-indigo-400 hover:underline">
									Help page
								</a>{" "}
								for the circuit diagram.
							</p>
						</div>
					</div>
				</div>

				{/* Left Joystick - Movement */}
				<div className="rounded-3xl border border-border bg-card/50 p-8 flex flex-col items-center justify-center gap-6 shadow-2xl relative overflow-hidden group">
					<div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
					<h3 className="text-lg font-bold text-indigo-300">Locomotion</h3>
					<div
						ref={leftJoystickRef}
						className="h-48 w-48 rounded-full bg-black/40 border border-white/5 shadow-inner relative touch-none"
					/>
					<div className="grid grid-cols-2 gap-4 w-full">
						<div className="rounded-xl bg-black/30 p-3 border border-white/5">
							<span className="block text-[10px] uppercase tracking-wider text-muted-foreground">
								Axis X
							</span>
							<span className="text-sm font-mono text-indigo-400 font-bold">
								{lastMove.x.toFixed(2)}
							</span>
						</div>
						<div className="rounded-xl bg-black/30 p-3 border border-white/5">
							<span className="block text-[10px] uppercase tracking-wider text-muted-foreground">
								Axis Y
							</span>
							<span className="text-sm font-mono text-indigo-400 font-bold">
								{lastMove.y.toFixed(2)}
							</span>
						</div>
					</div>
				</div>

				{/* Right Joystick - Look (Placeholder) */}
				<div className="rounded-3xl border border-border bg-card/50 p-8 flex flex-col items-center justify-center gap-6 shadow-2xl relative overflow-hidden group">
					<div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
					<h3 className="text-lg font-bold text-pink-300">Vision</h3>
					<div
						ref={rightJoystickRef}
						className="h-48 w-48 rounded-full bg-black/40 border border-white/5 shadow-inner relative touch-none"
					/>
					<div className="flex flex-col gap-2 w-full">
						<button
							onClick={toggleView}
							className={`flex w-full items-center justify-center gap-2 rounded-xl py-3 px-4 font-semibold transition-all duration-300 border ${
								viewType === "third-person"
									? "bg-indigo-500 text-white border-indigo-400 shadow-lg shadow-indigo-500/25"
									: "bg-white/5 text-foreground border-white/10 hover:bg-white/10"
							}`}
						>
							{viewType === "first-person" ? (
								<Eye className="h-5 w-5" />
							) : (
								<EyeOff className="h-5 w-5" />
							)}
							{viewType === "first-person"
								? "Switch to Third Person"
								: "Switch to First Person"}
						</button>
					</div>
				</div>

				{/* Settings & Info */}
				<div className="rounded-3xl border border-border bg-card/50 p-8 flex flex-col gap-6 shadow-2xl">
					<h3 className="text-lg font-bold text-foreground">
						Control Settings
					</h3>

					<div className="space-y-4">
						<div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
							<span className="text-sm text-foreground">Deadzone</span>
							<span className="text-xs text-muted-foreground">0.10</span>
						</div>
						<div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
							<span className="text-sm text-foreground">Sensitivity</span>
							<span className="text-xs text-muted-foreground">1.0x</span>
						</div>
						<div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
							<span className="text-sm text-foreground">Invert Y-Axis</span>
							<div className="h-5 w-10 rounded-full bg-white/10 relative cursor-not-allowed">
								<div className="absolute left-1 top-1 h-3 w-3 rounded-full bg-muted" />
							</div>
						</div>
					</div>

					<div className="mt-auto space-y-2">
						<div className="text-xs text-center text-muted-foreground">
							Connected via <strong>OSC/HTTP</strong>
						</div>
						<div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
							<div className="h-full bg-green-500/50 w-full" />
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
