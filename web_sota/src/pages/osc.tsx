import {
    Radio,
    Send,
    Square,
    Play,
    Clock,
    Terminal,
    RefreshCw,
    Database,
    Cpu,
    Zap,
    Globe,
    Monitor
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { cn } from '@/common/utils';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface OSCServerStats {
    port: number;
    server_running: boolean;
    messages_buffered: number;
    buffer_age_seconds: number;
}

interface OSCMessage {
    timestamp: number;
    address: string;
    args: (string | number | boolean)[];
}

async function fetchOSCStatus() {
    const resp = await fetch('/api/osc/status');
    if (!resp.ok) throw new Error('Failed to fetch OSC status');
    return resp.json();
}

async function fetchReceivedMessages(port: number) {
    const resp = await fetch(`/api/osc/received?port=${port}&limit=50`);
    if (!resp.ok) throw new Error('Failed to fetch messages');
    return resp.json();
}

export function OSCPage() {
    const [sendData, setSendData] = useState({ host: '127.0.0.1', port: 9000, address: '/avatar/parameters', values: '' });
    const [startData, setStartData] = useState({ port: 9001, address: '0.0.0.0' });
    const [activePort, setActivePort] = useState<number | null>(null);

    const { data: statusData, refetch: refetchStatus, isLoading: isStatusLoading } = useQuery({
        queryKey: ['osc-status'],
        queryFn: fetchOSCStatus,
        refetchInterval: 5000,
    });

    // Automatically set the first active port as the active port for log monitoring if none is selected
    useEffect(() => {
        if (statusData?.servers?.length > 0 && activePort === null) {
            setActivePort(statusData.servers[0].port);
        }
    }, [statusData, activePort]);

    const { data: receivedData } = useQuery({
        queryKey: ['osc-messages', activePort],
        queryFn: () => fetchReceivedMessages(activePort!),
        enabled: activePort !== null,
        refetchInterval: 2000,
    });

    // Derive messages from query data
    const messages = receivedData?.messages || [];

    const sendMutation = useMutation({
        mutationFn: async (payload: { host: string; port: number; address: string; values: (string | number | boolean)[] }) => {
            const resp = await fetch('/api/osc/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!resp.ok) throw new Error('Send failed');
            return resp.json();
        }
    });

    const startMutation = useMutation({
        mutationFn: async (payload: { port: number; address: string }) => {
            const resp = await fetch('/api/osc/server/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!resp.ok) throw new Error('Start failed');
            return resp.json();
        },
        onSuccess: () => refetchStatus(),
    });

    const stopMutation = useMutation({
        mutationFn: async (port: number) => {
            const resp = await fetch('/api/osc/server/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ port }),
            });
            if (!resp.ok) throw new Error('Stop failed');
            return resp.json();
        },
        onSuccess: (_data, port) => {
            refetchStatus();
            if (activePort === port) setActivePort(null);
        },
    });

    const clearMutation = useMutation({
        mutationFn: async (port: number) => {
            const resp = await fetch(`/api/osc/clear?port=${port}`, {
                method: 'POST',
            });
            if (!resp.ok) throw new Error('Clear failed');
            return resp.json();
        },
        onSuccess: () => {
            // Refetch messages to show they are cleared
            refetchStatus();
        }
    });

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault();
        const values = sendData.values.split(',').map(v => {
            const trimmed = v.trim();
            if (!isNaN(Number(trimmed)) && trimmed !== '') return Number(trimmed);
            if (trimmed === 'true') return true;
            if (trimmed === 'false') return false;
            // Remove quotes if present
            return trimmed.replace(/^['"](.*)['"]$/, '$1');
        });
        sendMutation.mutate({ ...sendData, values });
    };

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-border/30">
                <div>
                    <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
                        OSC <span className="text-indigo-400">Multiplexer</span>
                    </h2>
                    <p className="text-muted-foreground mt-1 flex items-center gap-2">
                        <Radio className="h-3 w-3 text-indigo-400 animate-pulse" />
                        Open Sound Control • {statusData?.servers?.length || 0} Port(s) Active
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="icon"
                        onClick={() => refetchStatus()}
                        className="rounded-xl border-border/50 bg-muted/20 glass"
                    >
                        <RefreshCw className={cn("h-4 w-4", isStatusLoading && "animate-spin")} />
                    </Button>
                    <div className="hidden md:flex gap-1.5 ml-2">
                        <div className="h-1 w-8 rounded-full bg-indigo-500" />
                        <div className="h-1 w-4 rounded-full bg-indigo-500/50" />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                {/* Send Matrix */}
                <div className="xl:col-span-12 2xl:col-span-5 space-y-6">
                    <Card className="border-border/50 bg-card/30 backdrop-blur-md glass overflow-hidden border-t-indigo-500/30">
                        <CardHeader className="bg-gradient-to-b from-indigo-500/[0.05] to-transparent border-b border-border/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-indigo-500/10">
                                    <Send className="h-4 w-4 text-indigo-400" />
                                </div>
                                <div>
                                    <CardTitle className="text-sm font-black uppercase tracking-widest text-foreground">Command Transmitter</CardTitle>
                                    <CardDescription className="text-[10px] text-muted-foreground uppercase font-bold tracking-tighter opacity-70">Direct Protocol Injection</CardDescription>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="p-6">
                            <form onSubmit={handleSend} className="space-y-5">
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                    <div className="sm:col-span-2 space-y-2">
                                        <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Target Hub</Label>
                                        <Input
                                            value={sendData.host}
                                            onChange={e => setSendData({ ...sendData, host: e.target.value })}
                                            className="bg-muted/30 border-border/50 rounded-xl h-11 focus:ring-2 focus:ring-indigo-500/20"
                                            placeholder="127.0.0.1"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">UDP Port</Label>
                                        <Input
                                            type="number"
                                            value={sendData.port}
                                            onChange={e => setSendData({ ...sendData, port: parseInt(e.target.value) })}
                                            className="bg-muted/30 border-border/50 rounded-xl h-11 focus:ring-2 focus:ring-indigo-500/20"
                                            placeholder="9000"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">OSC Address Pattern</Label>
                                    <div className="relative group">
                                        <Input
                                            value={sendData.address}
                                            onChange={e => setSendData({ ...sendData, address: e.target.value })}
                                            className="bg-muted/30 border-border/50 rounded-xl h-11 pl-10 focus:ring-2 focus:ring-indigo-500/20"
                                            placeholder="/avatar/parameters/Control"
                                        />
                                        <Globe className="absolute left-3.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground group-focus-within:text-indigo-400 transition-colors" />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Argument Buffer (CSV)</Label>
                                    <div className="relative group">
                                        <Input
                                            value={sendData.values}
                                            onChange={e => setSendData({ ...sendData, values: e.target.value })}
                                            className="bg-muted/30 border-border/50 rounded-xl h-11 pl-10 font-mono text-xs focus:ring-2 focus:ring-indigo-500/20"
                                            placeholder="0.85, true, 'NeuralActive'"
                                        />
                                        <Database className="absolute left-3.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground group-focus-within:text-indigo-400 transition-colors" />
                                    </div>
                                </div>

                                <Button
                                    type="submit"
                                    disabled={sendMutation.isPending}
                                    className="w-full bg-indigo-600 hover:bg-indigo-500 text-xs font-black uppercase tracking-[0.2em] rounded-xl h-12 shadow-[0_0_20px_rgba(79,70,229,0.3)] transition-all"
                                >
                                    {sendMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
                                    Execute Projection
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                </div>

                {/* Status & Orchestration */}
                <div className="xl:col-span-12 2xl:col-span-7 space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Active Servers */}
                        <Card className="border-border/50 bg-card/30 backdrop-blur-md glass overflow-hidden border-t-emerald-500/30 lg:col-span-1">
                            <CardHeader className="bg-gradient-to-b from-emerald-500/[0.05] to-transparent border-b border-border/50">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-emerald-500/10">
                                            <Monitor className="h-4 w-4 text-emerald-400" />
                                        </div>
                                        <CardTitle className="text-sm font-black uppercase tracking-widest text-foreground">Listening Hubs</CardTitle>
                                    </div>
                                    <span className="text-[9px] font-black bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-500/20">
                                        {statusData?.servers?.length || 0} ACTIVE
                                    </span>
                                </div>
                            </CardHeader>
                            <CardContent className="p-4">
                                <div className="space-y-3 max-h-[220px] overflow-y-auto pr-2 custom-scrollbar">
                                    {statusData?.servers?.map((server: OSCServerStats) => (
                                        <div
                                            key={server.port}
                                            onClick={() => setActivePort(server.port)}
                                            className={cn(
                                                "group flex items-center justify-between p-3 rounded-xl border transition-all duration-300 cursor-pointer",
                                                activePort === server.port
                                                    ? "bg-indigo-500/10 border-indigo-500/50 shadow-[0_0_15px_rgba(79,70,229,0.1)]"
                                                    : "bg-muted/20 border-border/50 hover:border-emerald-500/30"
                                            )}
                                        >
                                            <div className="flex items-center gap-4">
                                                <div className={cn("h-2 w-2 rounded-full animate-pulse", activePort === server.port ? "bg-indigo-400" : "bg-emerald-500")} />
                                                <div>
                                                    <p className="text-xs font-black text-foreground">PORT {server.port}</p>
                                                    <div className="flex items-center gap-3 mt-1 opacity-60">
                                                        <span className="text-[9px] font-bold uppercase tracking-tighter flex items-center gap-1">
                                                            <Database className="h-2.5 w-2.5" />
                                                            {server.messages_buffered} MSGS
                                                        </span>
                                                        <span className="text-[9px] font-bold uppercase tracking-tighter flex items-center gap-1">
                                                            <Clock className="h-2.5 w-2.5" />
                                                            {server.buffer_age_seconds.toFixed(1)}s AGE
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    stopMutation.mutate(server.port);
                                                }}
                                                className="h-8 w-8 rounded-lg text-red-400/50 hover:text-red-400 hover:bg-red-500/10 transition-all opacity-0 group-hover:opacity-100"
                                            >
                                                <Square className="h-3.5 w-3.5 fill-current" />
                                            </Button>
                                        </div>
                                    ))}
                                    {(!statusData?.servers || statusData.servers.length === 0) && (
                                        <div className="py-12 text-center">
                                            <Cpu className="h-8 w-8 text-muted-foreground/20 mx-auto mb-2" />
                                            <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">No Active Listeners</p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Orchestration Control */}
                        <Card className="border-border/50 bg-card/30 backdrop-blur-md glass overflow-hidden border-t-amber-500/30 lg:col-span-1">
                            <CardHeader className="bg-gradient-to-b from-amber-500/[0.05] to-transparent border-b border-border/50">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-amber-500/10">
                                        <Zap className="h-4 w-4 text-amber-400" />
                                    </div>
                                    <CardTitle className="text-sm font-black uppercase tracking-widest text-foreground">Neural Initiation</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="p-5 space-y-4">
                                <div className="space-y-4">
                                    <div className="grid gap-2">
                                        <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Target Initialization Port</Label>
                                        <div className="flex gap-2">
                                            <Input
                                                type="number"
                                                value={startData.port}
                                                onChange={e => setStartData({ ...startData, port: parseInt(e.target.value) })}
                                                className="bg-muted/30 border-border/50 rounded-xl h-11 focus:ring-2 focus:ring-amber-500/20"
                                                placeholder="9001"
                                            />
                                            <Button
                                                onClick={() => startMutation.mutate(startData)}
                                                disabled={startMutation.isPending}
                                                className="h-11 px-6 bg-amber-600 hover:bg-amber-500 text-xs font-black uppercase tracking-widest rounded-xl transition-all shadow-[0_0_15px_rgba(245,158,11,0.2)]"
                                            >
                                                {startMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                                            </Button>
                                        </div>
                                    </div>
                                    <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
                                        <p className="text-[10px] font-bold text-amber-400/80 leading-relaxed uppercase tracking-wider">
                                            Operational Tip: Use port 9001 for real-time Resonite feedback telemetry. Ensure your intra-versal OSC configuration matches.
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Stream Trace */}
                    <Card className="border-border/50 bg-black/40 backdrop-blur-xl glass overflow-hidden border-l-4 border-l-indigo-500/50">
                        <div className="bg-white/[0.03] px-5 py-3 border-b border-border/50 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Terminal className="h-4 w-4 text-indigo-400" />
                                <span className="text-[10px] font-black text-foreground uppercase tracking-[0.2em] italic">Neural Stream Analysis {activePort ? `(PORT ${activePort})` : ''}</span>
                            </div>
                            <div className="flex items-center gap-3">
                                {activePort && (
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => clearMutation.mutate(activePort)}
                                        className="h-6 text-[9px] px-2 font-black uppercase tracking-widest border-indigo-500/30 bg-indigo-500/5 hover:bg-indigo-500/10"
                                    >
                                        Clear Signal
                                    </Button>
                                )}
                                <div className="h-2 w-16 bg-white/[0.05] rounded-full overflow-hidden">
                                    <div className="h-full bg-indigo-500 animate-pulse w-3/4" />
                                </div>
                                <span className="text-[9px] font-black text-emerald-500 uppercase tracking-widest">Live Flow</span>
                            </div>
                        </div>
                        <div className="h-64 p-5 font-mono text-[10px] overflow-y-auto space-y-2 custom-scrollbar bg-gradient-to-b from-transparent to-indigo-950/20">
                            {messages.length === 0 && !statusData?.servers?.length && (
                                <div className="flex flex-col items-center justify-center h-full opacity-20">
                                    <Database className="h-12 w-12 mb-4" />
                                    <p className="uppercase tracking-[0.3em] font-black">No Active Data Signal</p>
                                </div>
                            )}
                            {messages.map((msg: OSCMessage, i: number) => (
                                <div key={i} className="flex gap-4 p-2 rounded-lg hover:bg-white/[0.03] transition-colors group border border-transparent hover:border-white/[0.05] animate-in slide-in-from-left-2 duration-300">
                                    <span className="text-muted-foreground opacity-50 min-w-[70px]">{new Date(msg.timestamp * 1000).toLocaleTimeString()}</span>
                                    <span className="text-indigo-400 font-bold group-hover:text-indigo-300 transition-colors uppercase tracking-tight">{msg.address}</span>
                                    <span className="text-foreground/80 font-medium">
                                        {msg.args.map((arg: any, idx: number) => (
                                            <span key={idx} className="mr-2 px-1.5 py-0.5 rounded bg-muted/30 text-emerald-400/80 border border-white/[0.05]">
                                                {typeof arg === 'boolean' ? (arg ? 'TRUE' : 'FALSE') : arg}
                                            </span>
                                        ))}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
