import { Wrench, ChevronDown, ChevronRight } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { cn } from '@/common/utils';

interface ToolParam {
    type: string;
    description?: string;
}

interface Tool {
    name: string;
    description: string;
    parameters?: Record<string, ToolParam>;
}

async function fetchTools(): Promise<Tool[]> {
    const r = await fetch('/api/system');
    if (!r.ok) throw new Error('Failed to load tools');
    const data = await r.json() as { tools?: Tool[] };
    return data.tools ?? [];
}

export function Tools() {
    const { data: tools, isLoading, isError } = useQuery({
        queryKey: ['tools'],
        queryFn: fetchTools,
    });
    const [expanded, setExpanded] = useState<string | null>(null);

    const categories = tools ? groupByPrefix(tools) : {};

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center gap-3">
                <Wrench className="w-5 h-5 text-indigo-400" aria-hidden="true" />
                <div>
                    <h2 className="text-lg font-bold gradient-text">MCP Tools</h2>
                    <p className="text-sm text-slate-500">All registered Resonite MCP tools</p>
                </div>
            </div>

            {isLoading && <p className="text-sm text-slate-600">Loading tools…</p>}
            {isError && <p className="text-sm text-red-400">Failed to load tools</p>}

            {Object.entries(categories).map(([cat, catTools]) => (
                <div key={cat} className="space-y-2">
                    <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">{cat}</h3>
                    {catTools.map(tool => (
                        <div key={tool.name} className="glass-card overflow-hidden">
                            <button
                                onClick={() => setExpanded(e => e === tool.name ? null : tool.name)}
                                aria-expanded={expanded === tool.name}
                                aria-controls={`tool-${tool.name}`}
                                className="w-full flex items-center justify-between p-4 text-left hover:bg-white/[0.02] transition-colors"
                            >
                                <div className="space-y-0.5">
                                    <code className="text-sm font-mono text-indigo-300">{tool.name}</code>
                                    <p className="text-xs text-slate-500">{tool.description}</p>
                                </div>
                                {expanded === tool.name
                                    ? <ChevronDown className="w-4 h-4 text-slate-500 flex-shrink-0" aria-hidden="true" />
                                    : <ChevronRight className="w-4 h-4 text-slate-500 flex-shrink-0" aria-hidden="true" />}
                            </button>

                            {expanded === tool.name && tool.parameters && (
                                <div id={`tool-${tool.name}`} className="px-4 pb-4 space-y-2 border-t border-white/[0.04]">
                                    <p className="text-xs text-slate-600 pt-3">Parameters</p>
                                    {Object.entries(tool.parameters).map(([pname, param]) => (
                                        <div key={pname} className="flex items-start gap-3 text-xs">
                                            <code className="text-cosmos-300 w-40 flex-shrink-0">{pname}</code>
                                            <span className="text-slate-500 font-mono w-16 flex-shrink-0">{param.type}</span>
                                            <span className="text-slate-400">{param.description ?? ''}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
}

function groupByPrefix(tools: Tool[]): Record<string, Tool[]> {
    const out: Record<string, Tool[]> = {};
    for (const t of tools) {
        const prefix = t.name.split('_').slice(0, 2).join('_');
        const cat = prefix.replace('resonite_', '').replace('_', ' ');
        const label = cat.charAt(0).toUpperCase() + cat.slice(1);
        if (!out[label]) out[label] = [];
        out[label].push(t);
    }
    return out;
}
