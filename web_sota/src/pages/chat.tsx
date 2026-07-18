import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronDown, Copy, Download, Eraser, Pencil, RefreshCw, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import clsx from "clsx";

const OLLAMA = "http://localhost:11434";
const BACKEND = "";
const HISTORY_KEY = "resonite-mcp-chat-history";
const PERSONALITY_KEY = "resonite-mcp-chat-personality";

const WELCOME_MSG = "Hi! I'm your Resonite MCP assistant. Ask me to explore XR worlds, manage inventory, control avatars, or interact with the Resonite platform.";

type Msg = { role: "user" | "assistant"; content: string; ts?: string };

const PERSONALITIES = [
  { id: "xr-explorer", label: "XR Explorer", prompt: "You are an XR world exploration guide for Resonite. Help users discover worlds, navigate sessions, and understand the social VR landscape. Be concise and practical." },
  { id: "asset-manager", label: "Asset Manager", prompt: "You are a Resonite asset management specialist. Help users organize inventory, upload items, find resources, and manage their digital collection efficiently." },
  { id: "quick-summarizer", label: "Quick Summarizer", prompt: "You specialize in distilling complex Resonite topics into 3-bullet summaries: (1) what the feature does, (2) how to use it, (3) key tip." },
  { id: "custom", label: "Custom", prompt: "" },
];

const EXAMPLE_PROMPTS = [
  { group: "Worlds", prompts: ["Explore popular XR worlds in Resonite", "What sessions are active right now?", "Find worlds with multiplayer games"] },
  { group: "Assets", prompts: ["Search my inventory for furniture props", "Upload a 3D model to Resonite", "How do I share an item with friends?"] },
  { group: "XR", prompts: ["Set up a new session for avatar testing", "How do I optimize a world for performance?", "Guide me through ProtoFlux scripting basics"] },
];

function loadHistory(): Msg[] {
  try { const raw = localStorage.getItem(HISTORY_KEY); return raw ? JSON.parse(raw) : []; }
  catch { return []; }
}

function saveHistory(msgs: Msg[]) {
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(msgs.slice(-100))); }
  catch { /* quota */ }
}

function loadPersonality(): string {
  try { return localStorage.getItem(PERSONALITY_KEY) || PERSONALITIES[0].id; }
  catch { return PERSONALITIES[0].id; }
}

function savePersonality(id: string) {
  try { localStorage.setItem(PERSONALITY_KEY, id); }
  catch { /* ignore */ }
}

function formatChatTxt(msgs: Msg[]): string {
  return msgs.map((m) => {
    const ts = m.ts ? `[${new Date(m.ts).toLocaleString()}] ` : "";
    const role = m.role === "user" ? "You" : "Assistant";
    return `${ts}${role}:\n${m.content}\n`;
  }).join("\n");
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text).catch(() => {});
}

function ThinkingDots() {
  return (
    <span className="inline-flex items-center gap-0.5">
      <span className="h-1.5 w-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:0ms]" />
      <span className="h-1.5 w-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:300ms]" />
    </span>
  );
}

function ChatMessage({ msg, isLast, copied, onEdit, onCopy, onRegenerate, editing, editText, setEditText, onSaveEdit, onCancelEdit }: {
  msg: Msg; isLast: boolean; copied: boolean;
  onEdit: () => void; onCopy: () => void; onRegenerate?: () => void;
  editing: boolean; editText: string; setEditText: (v: string) => void; onSaveEdit: () => void; onCancelEdit: () => void;
}) {
  const isUser = msg.role === "user";
  return (
    <div className={clsx("flex", isUser ? "justify-end" : "justify-start")}>
      <div className={clsx("group relative max-w-[88%] md:max-w-[78%]", isUser && "order-1")}>
        {editing ? (
          <div className="rounded-xl border border-border bg-background p-2 space-y-2">
            <textarea value={editText} onChange={(e) => setEditText(e.target.value)}
              className="w-full rounded-md border border-border bg-background/60 px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
              rows={3} autoFocus onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onSaveEdit(); } if (e.key === "Escape") onCancelEdit(); }} />
            <div className="flex justify-end gap-1">
              <Button size="sm" variant="ghost" onClick={onCancelEdit}>Cancel</Button>
              <Button size="sm" onClick={onSaveEdit}>Save</Button>
            </div>
          </div>
        ) : (
          <>
            <div className={clsx("rounded-xl px-4 py-2.5 text-sm leading-relaxed break-words",
              isUser ? "bg-primary/15" : "bg-muted/40 border border-border/30",
            )}>
              {isUser ? (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              ) : (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              )}
            </div>
            <div className={clsx("flex items-center gap-0.5 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity",
              isUser ? "justify-end" : "justify-start")}>
              <span className="text-[10px] text-muted-foreground/60 mr-1">
                {msg.ts ? new Date(msg.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
              </span>
              {isUser && (
                <button onClick={onEdit} className="p-0.5 rounded text-muted-foreground/40 hover:text-foreground transition-colors" title="Edit">
                  <Pencil className="h-3 w-3" />
                </button>
              )}
              <button onClick={onCopy} className="p-0.5 rounded text-muted-foreground/40 hover:text-foreground transition-colors" title="Copy">
                {copied ? <span className="text-[10px] text-green-400">Copied</span> : <Copy className="h-3 w-3" />}
              </button>
              {!isUser && isLast && onRegenerate && (
                <button onClick={onRegenerate} className="p-0.5 rounded text-muted-foreground/40 hover:text-foreground transition-colors" title="Regenerate">
                  <RefreshCw className="h-3 w-3" />
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export function Chat() {
  const [messages, setMessages] = useState<Msg[]>(() => loadHistory());
  const [input, setInput] = useState("");
  const [model, setModel] = useState("llama3.2");
  const [ollamaUp, setOllamaUp] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [personalityId, setPersonalityId] = useState(loadPersonality);
  const [customPrompt] = useState("");
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isNearBottomRef = useRef(true);

  const personality = PERSONALITIES.find((p) => p.id === personalityId) ?? PERSONALITIES[0];

  useEffect(() => { saveHistory(messages); }, [messages]);
  useEffect(() => { savePersonality(personalityId); }, [personalityId]);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${BACKEND}/api/llm/discover`);
        if (r.ok) {
          const d = await r.json();
          setOllamaUp(Boolean(d.ollama_detected));
          if (d.configured_model) setModel(d.configured_model);
        } else {
          setOllamaUp(false);
        }
      } catch { setOllamaUp(false); }
    })();
  }, []);

  const scrollToBottom = useCallback((smooth = true) => {
    bottomRef.current?.scrollIntoView({ behavior: smooth ? "smooth" : "auto" });
  }, []);

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const threshold = 150;
    const near = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
    isNearBottomRef.current = near;
    setShowScrollBtn(!near);
  }, []);

  useEffect(() => {
    if (isNearBottomRef.current) scrollToBottom(!loading);
  }, [messages, loading, scrollToBottom]);

  const systemPrompt = personalityId === "custom"
    ? (customPrompt || "You are a helpful assistant for Resonite MCP, an XR world browser and asset management server.")
    : personality.prompt;

  const send = useCallback(async (overrideMsg?: string) => {
    const text = (overrideMsg ?? input).trim();
    if (!text || loading) return;
    const user: Msg = { role: "user", content: text, ts: new Date().toISOString() };
    const next = [...messages, user];
    setMessages(next); setInput(""); setLoading(true);
    if (!overrideMsg) isNearBottomRef.current = true;
    try {
      const r = await fetch(`${OLLAMA}/api/chat`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, messages: [{ role: "system", content: systemPrompt }, ...next], stream: false }),
      });
      if (!r.ok) throw new Error(`Ollama HTTP ${r.status}`);
      const data = (await r.json()) as { message?: { content?: string } };
      setMessages((m) => [...m, { role: "assistant", content: data.message?.content ?? "(empty)", ts: new Date().toISOString() }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: `**Error:** ${e}`, ts: new Date().toISOString() }]);
    } finally { setLoading(false); }
  }, [input, loading, messages, model, systemPrompt]);

  const regenerate = useCallback(() => {
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    if (!lastUser) return;
    setMessages((m) => m.slice(0, -1));
    send(lastUser.content);
  }, [messages, send]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
    if (e.key === "Escape") { textareaRef.current?.blur(); }
  }, [send]);

  const startEdit = useCallback((idx: number, content: string) => {
    setEditingIdx(idx); setEditText(content);
  }, []);

  const saveEdit = useCallback(() => {
    if (editingIdx === null) return;
    const trimmed = editText.trim();
    if (!trimmed) return;
    setMessages((m) => {
      const next = [...m];
      next[editingIdx] = { ...next[editingIdx], content: trimmed, ts: new Date().toISOString() };
      return next.slice(0, editingIdx + 1);
    });
    setEditingIdx(null);
  }, [editingIdx, editText]);

  const clearMessages = useCallback(() => { setMessages([]); localStorage.removeItem(HISTORY_KEY); }, []);

  const exportChat = useCallback(() => {
    if (messages.length === 0) return;
    const blob = new Blob([formatChatTxt(messages)], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = `resonite-mcp-chat-${Date.now()}.txt`; a.click();
    URL.revokeObjectURL(url);
  }, [messages]);

  const handleCopy = useCallback((idx: number, content: string) => {
    copyToClipboard(content); setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 1500);
  }, []);

  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) { ta.style.height = "auto"; ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`; }
  }, [input]);

  const hasMessages = messages.length > 0;

  return (
    <div className="space-y-3 flex flex-col h-[calc(100vh-8rem)]" data-testid="chat-page">
      <div className="flex items-center justify-between gap-2 text-xs flex-wrap" data-testid="chat-controls">
        <div className="flex items-center gap-2">
          {ollamaUp === null ? <span className="text-muted-foreground">Detecting...</span>
            : ollamaUp
              ? <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-green-500" /> Ollama :11434</span>
              : <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-red-500" /> Ollama not detected</span>}
          <input value={model} onChange={(e) => setModel(e.target.value)} aria-label="Model name"
            className="rounded border border-border bg-background px-2 py-1 font-mono w-24" />
        </div>
        <div className="flex items-center gap-1.5">
          <label className="text-muted-foreground hidden sm:inline">Personality:</label>
          <select value={personalityId} onChange={(e) => setPersonalityId(e.target.value)}
            className="rounded border border-border bg-background px-2 py-1 text-xs text-foreground"
            data-testid="personality-select">
            {PERSONALITIES.map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
          </select>
          <div className="w-px h-4 bg-border/60 mx-1" />
          <button onClick={exportChat} disabled={!hasMessages}
            className="flex items-center gap-1 rounded border border-border/40 px-2 py-1 text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors disabled:opacity-40"
            data-testid="chat-export" title="Export conversation">
            <Download className="h-3 w-3" />
          </button>
          <button onClick={clearMessages} disabled={!hasMessages}
            className="flex items-center gap-1 rounded border border-border/40 px-2 py-1 text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors disabled:opacity-40"
            data-testid="chat-clear" title="Clear conversation">
            <Eraser className="h-3 w-3" />
          </button>
        </div>
      </div>

      <Card className="flex-1 flex flex-col min-h-0 overflow-hidden relative">
        <div ref={scrollRef} onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 scroll-smooth" data-testid="chat-messages">
          {!hasMessages && !loading && (
            <div className="max-w-xl mx-auto pt-8 text-center space-y-4">
              <p className="text-sm text-muted-foreground leading-relaxed">{WELCOME_MSG}</p>
              <div className="flex flex-wrap justify-center gap-2" data-testid="example-prompts">
                {EXAMPLE_PROMPTS.flatMap((g) => g.prompts.map((s) => (
                  <button key={s} onClick={() => { setInput(s); textareaRef.current?.focus(); }}
                    className="px-3 py-1.5 rounded-full text-xs bg-muted/30 border border-border/30 text-muted-foreground hover:text-foreground hover:border-primary/30 hover:bg-primary/5 transition-colors">
                    {s}
                  </button>
                )))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={`${i}-${msg.ts ?? i}`} msg={msg} isLast={i === messages.length - 1} copied={copiedIdx === i}
              editing={editingIdx === i} editText={editText} setEditText={setEditText}
              onEdit={() => startEdit(i, msg.content)}
              onCopy={() => handleCopy(i, msg.content)}
              onRegenerate={i === messages.length - 1 && msg.role === "assistant" ? regenerate : undefined}
              onSaveEdit={saveEdit} onCancelEdit={() => setEditingIdx(null)} />
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-muted/40 border border-border/30 rounded-xl px-4 py-3">
                <ThinkingDots />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {showScrollBtn && (
          <button onClick={() => scrollToBottom(true)}
            className="absolute bottom-20 right-8 z-10 h-8 w-8 rounded-full bg-primary/20 border border-primary/30 text-primary hover:bg-primary/30 transition-colors flex items-center justify-center"
            title="Scroll to bottom">
            <ChevronDown className="h-4 w-4" />
          </button>
        )}

        <div className="border-t border-border p-3 md:px-4 flex gap-2 items-end bg-background/80 backdrop-blur-sm">
          <textarea ref={textareaRef} value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            className="flex-1 rounded-lg border border-border bg-background/60 px-3 py-2 text-sm resize-none outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/60 max-h-[200px]"
            placeholder="Ask about Resonite..." data-testid="chat-input"
            disabled={loading} />
          <Button onClick={() => send()} disabled={loading || !input.trim() || !ollamaUp} data-testid="chat-send" className="shrink-0 h-10">
            {loading ? <ThinkingDots /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
      </Card>
    </div>
  );
}
