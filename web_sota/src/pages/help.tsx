import { ExternalLink, ChevronDown, BookOpen, MessageSquare, Terminal, Zap, Info } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/common/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

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
    {
        q: 'How do I set up Avatar Control?',
        a: `To use the virtual joysticks, you need a ProtoFlux setup in your avatar: 1. Listen for OSC float parameters '/avatar/parameters/MoveX' and '/avatar/parameters/MoveY'. 2. Drive your character controller's lateral/forward velocity. 3. For perspective, listen to '/avatar/parameters/ThirdPerson'. See the Control page or the ProtoFlux guide for details.`,
    },
];

function AccordionItem({ q, a }: { q: string; a: string }) {
    const [open, setOpen] = useState(false);
    return (
        <div className={cn(
            "border border-border/50 bg-card/30 backdrop-blur-md glass rounded-xl overflow-hidden transition-all duration-300",
            open && "border-indigo-500/40 bg-indigo-500/[0.02]"
        )}>
            <button
                onClick={() => setOpen(p => !p)}
                aria-expanded={open ? "true" : "false"}
                title={open ? "Collapse section" : "Expand section"}
                className="w-full flex items-center justify-between p-4 text-left group transition-colors"
            >
                <span className={cn(
                    "text-sm font-bold tracking-tight transition-colors",
                    open ? "text-indigo-400" : "text-foreground group-hover:text-indigo-300"
                )}>{q}</span>
                <ChevronDown className={cn(
                    'w-4 h-4 text-muted-foreground transition-transform duration-300',
                    open ? 'rotate-180 text-indigo-400' : 'group-hover:text-indigo-300'
                )} aria-hidden="true" />
            </button>
            {open && (
                <div className="px-5 pb-5 text-xs text-muted-foreground leading-relaxed border-t border-white/[0.04] pt-4 animate-in slide-in-from-top-2 duration-300">
                    {a}
                </div>
            )}
        </div>
    );
}

export function Help() {
    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-border/30">
                <div>
                    <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
                        Neural <span className="text-indigo-400">Documentation</span>
                    </h2>
                    <p className="text-muted-foreground mt-1 flex items-center gap-2">
                        <BookOpen className="h-3 w-3 text-indigo-400" />
                        Synchronizing Intelligence • Protocol Guides
                    </p>
                </div>
                <div className="flex gap-2">
                    <div className="h-1 w-8 rounded-full bg-indigo-500" />
                    <div className="h-1 w-4 rounded-full bg-indigo-500/50" />
                    <div className="h-1 w-2 rounded-full bg-indigo-500/20" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Column: Quick Links & Quick Start */}
                <div className="lg:col-span-12 xl:col-span-7 space-y-8">
                    {/* Quick Start */}
                    <Card className="border-border/50 bg-card/30 backdrop-blur-md glass overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-4 opacity-5">
                            <Zap className="h-32 w-32 text-indigo-500" />
                        </div>
                        <CardHeader className="border-b border-border/50 bg-indigo-500/[0.03]">
                            <CardTitle className="text-xs font-black uppercase tracking-[0.2em] text-foreground flex items-center gap-2">
                                <Terminal className="h-4 w-4 text-indigo-400" />
                                Accelerated Deployment
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-6">
                            <div className="space-y-5">
                                {[
                                    { text: 'Set RESONITE_USER_ID and RESONITE_TOKEN in your environment configuration.', icon: '01' },
                                    { text: 'Initialize the MCP engine: uv run python -m resonite_mcp', icon: '02' },
                                    { text: 'Engage Resonite and enable OSC in Settings → Interface → OSC', icon: '03' },
                                    { text: 'Verify the multiplex connection via the Status dashboard', icon: '04' },
                                    { text: 'Browse Inventory for synchronized assets and synchronized worlds', icon: '05' },
                                ].map((step, i) => (
                                    <div key={i} className="flex items-start gap-4 group">
                                        <div className="flex-shrink-0 w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] flex items-center justify-center font-black group-hover:bg-indigo-500/20 group-hover:border-indigo-500/40 transition-all duration-300">
                                            {step.icon}
                                        </div>
                                        <div className="pt-1.5 flex-1">
                                            <p className="text-sm text-foreground/80 leading-snug group-hover:text-foreground transition-colors">
                                                {step.text}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Quick Resources */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 px-1">
                            <div className="h-1 w-1 rounded-full bg-indigo-500" />
                            <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/70">External Substrates</h3>
                            <div className="h-px flex-1 bg-gradient-to-r from-border/50 to-transparent" />
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {[
                                { label: 'Resonite Wiki API', href: 'https://wiki.resonite.com/API', desc: 'REST protocol specifications' },
                                { label: 'Resonite Discord', href: 'https://discord.gg/resonite', desc: 'Neural network support' },
                                { label: 'OSC Documentation', href: 'https://wiki.resonite.com/OSC', desc: 'Control interface standards' },
                                { label: 'ProtoFlux Guide', href: 'https://wiki.resonite.com/ProtoFlux', desc: 'Visual logic architectures' },
                            ].map(({ label, href, desc }) => (
                                <a
                                    key={href}
                                    href={href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="border border-border/50 bg-card/30 backdrop-blur-md glass p-5 flex items-center justify-between group hover:border-indigo-500/40 hover:bg-indigo-500/[0.02] transition-all duration-300 rounded-2xl"
                                >
                                    <div className="space-y-1">
                                        <p className="text-xs font-black uppercase tracking-[0.1em] text-foreground group-hover:text-indigo-400 transition-colors">{label}</p>
                                        <p className="text-[10px] text-muted-foreground font-medium">{desc}</p>
                                    </div>
                                    <div className="p-2 rounded-full group-hover:bg-indigo-500/10 transition-colors">
                                        <ExternalLink className="w-3.5 h-3.5 text-muted-foreground group-hover:text-indigo-400 transition-colors" aria-hidden="true" />
                                    </div>
                                </a>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: FAQ */}
                <div className="lg:col-span-12 xl:col-span-5 space-y-6">
                    <div className="flex items-center gap-3 px-1">
                        <div className="h-1 w-1 rounded-full bg-indigo-500" />
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/70">Knowledge Base</h3>
                        <div className="h-px flex-1 bg-gradient-to-r from-border/50 to-transparent" />
                    </div>

                    <div className="space-y-3">
                        {FAQ.map(({ q, a }, i) => (
                            <AccordionItem key={i} q={q} a={a} />
                        ))}
                    </div>

                    <div className="mt-8 p-6 rounded-2xl border border-indigo-500/20 bg-indigo-500/5 backdrop-blur-md">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 rounded-lg bg-indigo-500/10">
                                <MessageSquare className="h-4 w-4 text-indigo-400" />
                            </div>
                            <h4 className="text-xs font-black uppercase tracking-widest text-foreground">Need Assistance?</h4>
                        </div>
                        <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                            If you encounter anomalies in the neural link, please consult the system logs or reach out on our Discord channel for expedited support.
                        </p>
                        <div className="flex items-center gap-2 text-[10px] font-bold text-indigo-400 uppercase tracking-widest">
                            <Info className="h-3 w-3" />
                            Build V1.0.4-SOTA • Operational
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
