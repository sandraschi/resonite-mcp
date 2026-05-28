import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, Download, ExternalLink, AlertTriangle, Loader2 } from 'lucide-react';
import { apiUrl } from '@/lib/api-base';

interface PresenceStatus {
    resonite_installed: boolean;
    resonite_running: boolean;
    launch_url?: string;
}

interface PresenceGateProps {
    children: React.ReactNode;
}

export function PresenceGate({ children }: PresenceGateProps) {
    const [status, setStatus] = useState<PresenceStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [launching, setLaunching] = useState(false);

    const fetchStatus = async () => {
        try {
            const res = await fetch(apiUrl("/api/status"));
            const data = await res.json();
            setStatus({
                resonite_installed: data.resonite_installed,
                resonite_running: data.resonite_running,
                launch_url: data.launch_url
            });
        } catch (error) {
            console.error('Failed to fetch presence status', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        // Poll for status changes every 5 seconds
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleLaunch = async () => {
        setLaunching(true);
        try {
            await fetch(apiUrl("/api/resonite/launch"), { method: "POST" });
            // Keep launching state for a bit to show feedback
            setTimeout(() => setLaunching(false), 3000);
        } catch (error) {
            console.error('Failed to launch Resonite', error);
            setLaunching(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
                <p className="text-sm text-muted-foreground animate-pulse uppercase tracking-[0.2em] font-bold">Checking Grid Presence...</p>
            </div>
        );
    }

    // If Resonite is running, unlock the app
    if (status?.resonite_running) {
        return <>{children}</>;
    }

    // If not running, show the presence gate
    return (
        <div className="flex items-center justify-center min-h-[80vh] p-4 animate-in fade-in zoom-in duration-500">
            <Card className="max-w-md w-full border-border bg-card/40 backdrop-blur-xl glass border-indigo-500/20 shadow-2xl shadow-indigo-500/10">
                <CardHeader className="text-center pb-2">
                    <div className="mx-auto mb-4 p-3 bg-indigo-500/10 rounded-2xl w-fit border border-indigo-500/20">
                        <AlertTriangle className="h-8 w-8 text-indigo-400" />
                    </div>
                    <CardTitle className="text-2xl font-black tracking-tight text-foreground uppercase">
                        Resonite <span className="text-indigo-400">Not Detected</span>
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mt-2">
                        The MCP requires an active Resonite session to interface with the virtual world.
                    </p>
                </CardHeader>
                <CardContent className="space-y-6 pt-4">
                    {status?.resonite_installed ? (
                        <div className="space-y-4 animate-in slide-in-from-bottom-4 duration-700">
                            <div className="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-lg text-center">
                                <p className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Installation Verified</p>
                                <p className="text-[10px] text-muted-foreground mt-1 underline decoration-emerald-500/30">Steam Edition Found</p>
                            </div>
                            <Button
                                onClick={handleLaunch}
                                disabled={launching}
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-black py-6 rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.3)] group transition-all duration-300"
                            >
                                {launching ? (
                                    <>
                                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                        INITIATING LAUNCH...
                                    </>
                                ) : (
                                    <>
                                        <Play className="mr-2 h-5 w-5 fill-current group-hover:scale-110 transition-transform" />
                                        START RESONITE
                                    </>
                                )}
                            </Button>
                            <p className="text-[10px] text-center text-muted-foreground italic uppercase tracking-tighter opacity-50">
                                Resonite will open via Steam. The MCP will auto-bridge once the process is active.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-4 animate-in slide-in-from-bottom-4 duration-700">
                            <div className="p-4 bg-rose-500/5 border border-rose-500/20 rounded-lg text-center">
                                <p className="text-xs font-bold text-rose-400 uppercase tracking-widest">Binary Not Found</p>
                                <p className="text-[10px] text-muted-foreground mt-1">Resonite is not detected in standard system paths.</p>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <Button
                                    variant="outline"
                                    onClick={() => window.open('https://store.steampowered.com/app/2519830/Resonite/', '_blank')}
                                    className="border-indigo-500/30 bg-indigo-500/5 hover:bg-indigo-500/10 text-indigo-300 font-bold py-5"
                                >
                                    <Download className="mr-2 h-4 w-4" /> STEAM
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => window.open('https://resonite.com/', '_blank')}
                                    className="border-purple-500/30 bg-purple-500/5 hover:bg-purple-500/10 text-purple-300 font-bold py-5"
                                >
                                    <ExternalLink className="mr-2 h-4 w-4" /> STANDALONE
                                </Button>
                            </div>
                            <div className="pt-4 border-t border-border/50">
                                <p className="text-xs font-bold text-foreground">SOTA Onboarding Node</p>
                                <ul className="text-xs text-muted-foreground mt-2 space-y-1.5 list-disc pl-4 decoration-indigo-500">
                                    <li>Install Resonite (Steam recommended)</li>
                                    <li>Log in to your account</li>
                                    <li>Enable OSC in settings (Port 9000)</li>
                                    <li>Return here to bridge the interface</li>
                                </ul>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
