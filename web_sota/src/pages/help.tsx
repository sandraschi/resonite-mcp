import { HelpCircle, ExternalLink, ChevronDown } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/common/utils';

const FAQ = [
    {
        q: 'How do I authenticate with the Resonite API?',
        a: `Use the resonite_rest_login MCP tool with your username and password. The token is stored for 30 days. Alternatively set RESONITE_USER_ID and RESONITE_TOKEN environment variables before starting the server.`,
    },
    {
        q: 'How do I import a World Labs world into Resonite?',
        a: `Generate a world via worldlabs-mcp. Once done, use resonite_rest_send_message to send the GLB collider URL to yourself or a contact. Inside Resonite, paste the URL into the import dialog. The Resonite MCP server also sends an OSC /worldlabs/import message if you have an in-world OSC receiver.`,
    },
    {
        q: 'How does OSC control work?',
        a: `Resonite exposes an OSC interface on localhost:9000 (send) / 9001 (receive). The MCP server uses OSC to spawn items, trigger inventory operations, and send avatar control signals. Make sure OSC is enabled in Resonite settings.`,
    },
    {
        q: 'What is ProtoFlux?',
        a: `ProtoFlux is Resonite's visual scripting system. You can create, read, and connect nodes programmatically via the MCP tools. See PROTOFLUX_GUIDE.md in the repo for complete documentation.`,
    },
    {
        q: 'Why are sessions not loading?',
        a: `Public sessions load without auth from api.resonite.com/sessions. If the page is empty, check your network connection. Private sessions require auth.`,
    },
];

function AccordionItem({ q, a }: { q: string; a: string }) {
    const [open, setOpen] = useState(false);
    return (
        <div className="glass-card overflow-hidden">
            <button
                onClick={() => setOpen(p => !p)}
                aria-expanded={open}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-white/[0.02] transition-colors"
            >
                <span className="text-sm font-medium text-slate-200">{q}</span>
                <ChevronDown className={cn('w-4 h-4 text-slate-500 transition-transform flex-shrink-0', open && 'rotate-180')} aria-hidden="true" />
            </button>
            {open && (
                <div className="px-4 pb-4 text-sm text-slate-400 leading-relaxed border-t border-white/[0.04] pt-3">
                    {a}
                </div>
            )}
        </div>
    );
}

export function Help() {
    return (
        <div className="space-y-8 page-enter">
            <div className="flex items-center gap-3">
                <HelpCircle className="w-5 h-5 text-indigo-400" aria-hidden="true" />
                <div>
                    <h2 className="text-lg font-bold gradient-text">Help &amp; Documentation</h2>
                    <p className="text-sm text-slate-500">Getting started with Resonite MCP</p>
                </div>
            </div>

            {/* Quick links */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                    { label: 'Resonite Wiki API', href: 'https://wiki.resonite.com/API', desc: 'Official REST API reference' },
                    { label: 'Resonite Discord', href: 'https://discord.gg/resonite', desc: 'Community support' },
                    { label: 'OSC Documentation', href: 'https://wiki.resonite.com/OSC', desc: 'OSC control interface' },
                    { label: 'ProtoFlux Guide', href: 'https://wiki.resonite.com/ProtoFlux', desc: 'Visual scripting system' },
                ].map(({ label, href, desc }) => (
                    <a
                        key={href}
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="glass-card p-4 flex items-center justify-between group hover:border-indigo-500/30 transition-all"
                    >
                        <div>
                            <p className="text-sm font-medium text-slate-200 group-hover:text-indigo-300 transition-colors">{label}</p>
                            <p className="text-xs text-slate-500">{desc}</p>
                        </div>
                        <ExternalLink className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 transition-colors" aria-hidden="true" />
                    </a>
                ))}
            </div>

            {/* Quick start */}
            <div className="glass-card p-5 space-y-3">
                <h3 className="text-sm font-semibold text-slate-300">Quick Start</h3>
                <ol className="space-y-2 text-sm text-slate-400">
                    {[
                        'Set RESONITE_USER_ID and RESONITE_TOKEN in your .env file',
                        'Start the MCP server: uv run python -m resonite_mcp',
                        'Open Resonite and enable OSC in Settings → Interface → OSC',
                        'Use Status page to verify the API connection',
                        'Browse Inventory for your saved worlds and items',
                    ].map((step, i) => (
                        <li key={i} className="flex items-start gap-2">
                            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-600/30 text-indigo-300 text-xs flex items-center justify-center font-bold">{i + 1}</span>
                            {step}
                        </li>
                    ))}
                </ol>
            </div>

            {/* FAQ */}
            <div className="space-y-2">
                <h3 className="text-sm font-semibold text-slate-400">Frequently Asked Questions</h3>
                {FAQ.map(({ q, a }) => <AccordionItem key={q} q={q} a={a} />)}
            </div>
        </div>
    );
}
