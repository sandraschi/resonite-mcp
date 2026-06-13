import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings as SettingsIcon, Shield, Globe, Zap, Save, RefreshCw } from 'lucide-react';
import { useState, useEffect } from 'react';

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    const [status, setStatus] = useState<"loading"|"ready"|"error">("loading");
    useEffect(() => {
        fetch("/api/llm/providers").then(r => r.json()).then(d => {
            setProviders(d);
            const savedP = localStorage.getItem("llm_provider") || "ollama";
            const savedM = localStorage.getItem("llm_model") || "";
            setSelectedProvider(savedP);
            const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
            setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
            setStatus(models.length > 0 ? "ready" : "error");
        }).catch(() => {
            setProviders({ ollama: [{name:"llama3.2:3b"}] });
            setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
            setStatus("ready");
        });
    }, []);
    const save = (p:string, m:string) => { localStorage.setItem("llm_provider", p); localStorage.setItem("llm_model", m); };
    const models = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
    return (
        <Card className="border-border/50 bg-card/30 backdrop-blur-md glass overflow-hidden border-t-indigo-500/30">
            <CardHeader className="bg-gradient-to-b from-indigo-500/[0.05] to-transparent border-b border-border/50">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-indigo-500/10">
                        <Zap className="h-4 w-4 text-indigo-400" />
                    </div>
                    <div>
                        <CardTitle className="text-sm font-black uppercase tracking-widest text-foreground">Local LLM</CardTitle>
                        <CardDescription className="text-[10px] text-muted-foreground uppercase font-bold tracking-tighter opacity-70">Provider &amp; Model Selection</CardDescription>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
                <div className="space-y-2">
                    <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Provider</Label>
                    <select className="w-full bg-muted/30 border border-border/50 text-foreground rounded-xl h-11 px-4 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/40 transition-all appearance-none cursor-pointer"
                        value={selectedProvider} onChange={(e) => { setSelectedProvider(e.target.value); save(e.target.value, ""); }}>
                        <option value="ollama">Ollama</option>
                        <option value="lm_studio">LM Studio</option>
                    </select>
                </div>
                <div className="space-y-2">
                    <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Model</Label>
                    <select className="w-full bg-muted/30 border border-border/50 text-foreground rounded-xl h-11 px-4 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/40 transition-all appearance-none cursor-pointer"
                        value={selectedModel} onChange={(e) => { setSelectedModel(e.target.value); save(selectedProvider, e.target.value); }}>
                        {models.map((m) => <option key={m.name} value={m.name}>{m.name}</option>)}
                    </select>
                </div>
            </CardContent>
        </Card>
    );
}

export function Settings() {
    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-border/30">
                <div>
                    <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
                        Neural <span className="text-indigo-400">Configuration</span>
                    </h2>
                    <p className="text-muted-foreground mt-1 flex items-center gap-2">
                        <SettingsIcon className="h-3 w-3 text-indigo-400" />
                        System Tuning • Protocol Parameters
                    </p>
                </div>
                <div className="flex gap-2">
                    <div className="h-1 w-8 rounded-full bg-indigo-500" />
                    <div className="h-1 w-4 rounded-full bg-indigo-500/50" />
                    <div className="h-1 w-2 rounded-full bg-indigo-500/20" />
                </div>
            </div>

            <div className="grid gap-8 lg:grid-cols-2">
                {/* Connection Settings */}
                <Card className="border-border/50 bg-card/30 backdrop-blur-md glass overflow-hidden border-t-indigo-500/30">
                    <CardHeader className="bg-gradient-to-b from-indigo-500/[0.05] to-transparent border-b border-border/50">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-indigo-500/10">
                                <Globe className="h-4 w-4 text-indigo-400" />
                            </div>
                            <div>
                                <CardTitle className="text-sm font-black uppercase tracking-widest text-foreground">API Bridge</CardTitle>
                                <CardDescription className="text-[10px] text-muted-foreground uppercase font-bold tracking-tighter opacity-70">Multiplex Connection Parameters</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="p-6 space-y-6">
                        <div className="space-y-4">
                            <div className="grid gap-2">
                                <Label htmlFor="neural-host" className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Neural Host Address</Label>
                                <div className="relative group">
                                    <Input
                                        id="neural-host"
                                        aria-label="Neural Host Address"
                                        className="bg-muted/30 border-border/50 text-foreground placeholder-muted-foreground/50 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/40 transition-all h-11 pl-4"
                                        defaultValue="http://localhost:1072x"
                                    />
                                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                                        <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                        <span className="text-[8px] font-black text-emerald-500/70 tracking-tighter uppercase">ACTIVE</span>
                                    </div>
                                </div>
                                <p className="text-[10px] text-muted-foreground opacity-50 px-1">Ensure this matches your RESONITE_WEBAPP_PORT setting.</p>
                            </div>

                            <div className="grid gap-2 pt-2">
                                <Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Auth Protocol</Label>
                                <div className="p-3 rounded-xl bg-muted/20 border border-border/50 flex items-center justify-between group hover:border-indigo-500/30 transition-all cursor-not-allowed">
                                    <span className="text-xs font-bold text-foreground/60">Bearer Token (Environment)</span>
                                    <Shield className="h-3.5 w-3.5 text-muted-foreground opacity-40" />
                                </div>
                            </div>
                        </div>

                        <div className="pt-2 flex gap-3">
                            <Button variant="outline" className="flex-1 border-border/50 bg-muted/20 hover:bg-muted text-xs font-bold uppercase tracking-widest rounded-xl h-11 glass transition-all">
                                <RefreshCw className="h-3.5 w-3.5 mr-2 opacity-70" />
                                Test Link
                            </Button>
                            <Button className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-xs font-bold uppercase tracking-widest rounded-xl h-11 shadow-[0_0_20px_rgba(79,70,229,0.3)] transition-all">
                                <Save className="h-3.5 w-3.5 mr-2" />
                                Commit
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Performance & Advanced */}
                <Card className="border-border/50 bg-card/30 backdrop-blur-md glass overflow-hidden border-t-amber-500/30">
                    <CardHeader className="bg-gradient-to-b from-amber-500/[0.05] to-transparent border-b border-border/50">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-amber-500/10">
                                <Zap className="h-4 w-4 text-amber-400" />
                            </div>
                            <div>
                                <CardTitle className="text-sm font-black uppercase tracking-widest text-foreground">Performance</CardTitle>
                                <CardDescription className="text-[10px] text-muted-foreground uppercase font-bold tracking-tighter opacity-70">Latency & Optimization Tuning</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="p-6 space-y-6">
                        <div className="space-y-4">
                            <div className="grid gap-2">
                                <Label htmlFor="io-timeout" className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">I/O Timeout (ms)</Label>
                                <Input
                                    id="io-timeout"
                                    type="number"
                                    aria-label="I/O Timeout in milliseconds"
                                    className="bg-muted/30 border-border/50 text-foreground placeholder-muted-foreground/50 rounded-xl focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/40 transition-all h-11"
                                    defaultValue="5000"
                                />
                            </div>

                            <div className="grid gap-2 pt-2">
                                <Label htmlFor="log-retention" className="text-[10px] font-black uppercase tracking-widest text-muted-foreground italic">Log Retention</Label>
                                <select
                                    id="log-retention"
                                    title="Log Retention Period"
                                    aria-label="Log Retention Period"
                                    className="w-full bg-muted/30 border border-border/50 text-foreground rounded-xl h-11 px-4 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/40 transition-all appearance-none cursor-pointer"
                                >
                                    <option>Standard (1000 lines)</option>
                                    <option>Extended (5000 lines)</option>
                                    <option>Deep Trace (All Events)</option>
                                </select>
                            </div>
                        </div>

                        <div className="pt-2">
                            <Button variant="outline" className="w-full border-border/50 bg-muted/20 hover:bg-muted text-xs font-bold uppercase tracking-widest rounded-xl h-11 glass transition-all border-dashed border-2 text-amber-400/80 hover:text-amber-400 hover:border-amber-500/40">
                                <Save className="h-3.5 w-3.5 mr-2" />
                                Apply Adv. Manifest
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                <LLMSettings />
            </div>

            {/* System Integrity Notification (Mock) */}
            <div className="p-5 rounded-2xl border border-border/50 bg-muted/20 flex flex-col md:flex-row items-center gap-6">
                <div className="p-3 rounded-full bg-white/[0.03] border border-white/[0.05]">
                    <Shield className="h-6 w-6 text-indigo-400" />
                </div>
                <div className="flex-1 text-center md:text-left">
                    <h4 className="text-sm font-black uppercase tracking-widest text-foreground mb-1">Integrity Lock Active</h4>
                    <p className="text-[11px] text-muted-foreground leading-relaxed">
                        Some parameters are direct-mapped from your host environment configuration. Changes to these values require a full neural restart to successfully synchronize with the Resonite substrate.
                    </p>
                </div>
                <div className="flex gap-2 w-full md:w-auto">
                    <div className="flex-1 md:flex-none px-4 py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-black text-indigo-400 uppercase tracking-widest text-center cursor-default">
                        SOTA STANDARDS v1.4
                    </div>
                </div>
            </div>
        </div>
    );
}
