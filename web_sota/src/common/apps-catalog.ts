import { Activity, Bot, LayoutGrid, MonitorPlay } from "lucide-react";
import type { ElementType } from "react";

export interface AppEntry {
	id: string;
	label: string;
	description: string;
	icon: ElementType;
	url: string; // Absolute URL for cross-app navigation
	port: number;
	tags: string[];
}

// SOTA App Catalog - Centralized Registry for Fleet Navigation
export const APPS_CATALOG: AppEntry[] = [
	{
		id: "blender-mcp",
		label: "Blender Control",
		description: "3D visualization and geometry orchestration.",
		icon: Activity,
		url: "http://localhost:10848",
		port: 10848,
		tags: ["creative", "3d"],
	},
	{
		id: "avatar-mcp",
		label: "Avatar Control",
		description: "VRM avatar management and animation orchestration.",
		icon: Bot,
		url: "http://localhost:10792",
		port: 10792,
		tags: ["creative", "avatar"],
	},
	{
		id: "alexa-mcp",
		label: "Alexa Control",
		description: "Acoustic bridge and voice command orchestration.",
		icon: Activity,
		url: "http://localhost:10800",
		port: 10800,
		tags: ["control", "voice"],
	},
	{
		id: "vienna-live-mcp",
		label: "Vienna Live MCP",
		description: "Transit and location-aware services in Vienna.",
		icon: LayoutGrid,
		url: "http://localhost:10878",
		port: 10878,
		tags: ["transit", "vienna"],
	},
	{
		id: "handbrake-mcp",
		label: "Handbrake MCP",
		description: "Automated media transcoding and pipeline management.",
		icon: MonitorPlay,
		url: "http://localhost:10874",
		port: 10874,
		tags: ["media", "video"],
	},
	{
		id: "virtualdj-mcp",
		label: "VirtualDJ MCP",
		description: "SOTA VJing and audio orchestration.",
		icon: Activity,
		url: "http://localhost:10876",
		port: 10876,
		tags: ["media", "audio"],
	},
	{
		id: "mcp-central-docs",
		label: "Docs MCP",
		description: "Standardized MCP documentation and fleet registry.",
		icon: Activity,
		url: "http://localhost:10794",
		port: 10794,
		tags: ["knowledge", "admin"],
	},
	{
		id: "openfang",
		label: "OpenFang",
		description: "Fleet supervisor and modular agentic node controller.",
		icon: LayoutGrid,
		url: "http://localhost:10956",
		port: 10956,
		tags: ["infra", "admin"],
	},
];
