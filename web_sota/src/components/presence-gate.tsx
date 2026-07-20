import {
  AlertTriangle,
  Download,
  ExternalLink,
  Loader2,
  Play,
  RotateCcw,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiUrl } from "@/lib/api-base";

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
  const [backendStatus, setBackendStatus] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(apiUrl("/api/status"));
      const data = await res.json();
      setStatus({
        resonite_installed: data.resonite_installed,
        resonite_running: data.resonite_running,
        launch_url: data.launch_url,
      });
    } catch (error) {
      console.error("Failed to fetch presence status", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    // Poll for status changes every 5 seconds -- belt-and-suspenders
    // alongside the Tauri backend-status event listener below; the event
    // can be missed if this listener mounts after emission, so neither
    // signal alone is treated as sufficient (fleet nsis-build standard).
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  useEffect(() => {
    // Only meaningful inside the Tauri shell -- silently no-ops in a
    // plain dev browser where window.__TAURI_INTERNALS__ doesn't exist.
    let unlisten: (() => void) | undefined;
    let cancelled = false;
    import("@tauri-apps/api/event")
      .then(({ listen }) =>
        listen<string>("backend-status", (event) => {
          if (cancelled) return;
          setBackendStatus(event.payload);
          if (event.payload === "ready") {
            fetchStatus();
          }
        }),
      )
      .then((fn) => {
        if (cancelled) fn();
        else unlisten = fn;
      })
      .catch(() => {
        // Not running inside Tauri (plain browser dev mode) -- expected,
        // the HTTP poll above is the only signal available there.
      });
    return () => {
      cancelled = true;
      unlisten?.();
    };
  }, [fetchStatus]);

  const handleLaunch = async () => {
    setLaunching(true);
    try {
      await fetch(apiUrl("/api/resonite/start"), { method: "POST" });
      // Keep launching state for a bit to show feedback
      setTimeout(() => setLaunching(false), 3000);
    } catch (error) {
      console.error("Failed to launch Resonite", error);
      setLaunching(false);
    }
  };

  const handleRestartBackend = async () => {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("start_backend");
    } catch (error) {
      // Not running inside Tauri, or the command isn't available --
      // fall back to just re-checking status.
      console.error("Restart backend failed (not running in Tauri?)", error);
    } finally {
      fetchStatus();
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        <p className="text-sm text-muted-foreground animate-pulse font-bold">
          Checking Resonite status...
        </p>
      </div>
    );
  }

  // API error — show retry instead of blocking
  if (!status) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertTriangle className="h-8 w-8 text-rose-400" />
        <p className="text-sm text-muted-foreground">
          Backend unreachable — cannot check Resonite status
        </p>
        <Button variant="outline" size="sm" onClick={fetchStatus}>
          Retry
        </Button>
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
          <CardTitle className="text-2xl font-black tracking-tight text-foreground">
            Resonite <span className="text-indigo-400">Not Running</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground mt-2">
            Resonite MCP needs an active Resonite session on this machine.
          </p>
        </CardHeader>
        <CardContent className="space-y-6 pt-4">
          {status?.resonite_installed ? (
            <div className="space-y-4 animate-in slide-in-from-bottom-4 duration-700">
              <div className="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-lg text-center">
                <p className="text-xs font-bold text-emerald-400 tracking-widest">
                  Resonite found on this system
                </p>
              </div>
              <Button
                onClick={handleLaunch}
                disabled={launching}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-black py-6 rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.3)] group transition-all duration-300"
              >
                {launching ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Launching...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-5 w-5 fill-current group-hover:scale-110 transition-transform" />
                    Start Resonite
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={handleRestartBackend}
                className="w-full text-xs font-bold gap-2"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Restart Backend{backendStatus ? ` — ${backendStatus}` : ""}
              </Button>
              <p className="text-xs text-slate-400 text-center">
                Opens via Steam. MCP tools will activate once Resonite is
                running.
              </p>
            </div>
          ) : (
            <div className="space-y-4 animate-in slide-in-from-bottom-4 duration-700">
              <div className="p-4 bg-rose-500/5 border border-rose-500/20 rounded-lg text-center">
                <p className="text-xs font-bold text-rose-400 tracking-widest">
                  Resonite not found
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Not detected in Steam library or standard install paths.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  onClick={() =>
                    window.open(
                      "https://store.steampowered.com/app/2519830/Resonite/",
                      "_blank",
                    )
                  }
                  className="border-indigo-500/30 bg-indigo-500/5 hover:bg-indigo-500/10 text-indigo-300 font-bold py-5"
                >
                  <Download className="mr-2 h-4 w-4" /> Steam
                </Button>
                <Button
                  variant="outline"
                  onClick={() => window.open("https://resonite.com/", "_blank")}
                  className="border-purple-500/30 bg-purple-500/5 hover:bg-purple-500/10 text-purple-300 font-bold py-5"
                >
                  <ExternalLink className="mr-2 h-4 w-4" /> Website
                </Button>
              </div>
              <div className="pt-4 border-t border-border/50">
                <p className="text-xs font-bold text-foreground">Setup steps</p>
                <ul className="text-xs text-muted-foreground mt-2 space-y-1.5 list-disc pl-4">
                  <li>Install Resonite (Steam — free)</li>
                  <li>Log in to your Resonite account</li>
                  <li>Enable OSC input in Settings (port 9000)</li>
                  <li>Return to this dashboard to connect</li>
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
