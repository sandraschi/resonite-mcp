import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search as SearchIcon, FileText, ExternalLink, Loader2 } from "lucide-react";
import { apiUrl } from "@/lib/api-base";

interface SearchResult {
    text: string;
    title: string;
    filename: string;
    score: number;
}

export function SearchPage() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            // In a real SOTA setup, we'd use the MCP tool, but for the webapp 
            // we expose a dedicated endpoint or wrap the tool call.
            // For now, we mock the search behavior through a direct API feel.
            const response = await fetch(apiUrl(`/api/search?q=${encodeURIComponent(query)}`));
            const data = await response.json();
            setResults(data.results || []);
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="max-w-2xl">
                <h2 className="text-3xl font-extrabold tracking-tight text-foreground">
                    Semantic <span className="text-indigo-400">Search</span>
                </h2>
                <p className="text-muted-foreground mt-2">
                    Query the Resonite knowledge base using natural language.
                    Powered by FastMCP 3.1 & LanceDB.
                </p>
            </div>

            <Card className="border-border bg-card/40 backdrop-blur-md glass">
                <CardContent className="pt-6">
                    <form onSubmit={handleSearch} className="flex gap-3">
                        <div className="relative flex-1">
                            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="e.g. How do I create a ProtoFlux script for avatar tracking?"
                                className="pl-10 bg-background/50 border-indigo-500/20 focus:border-indigo-500/50 transition-all"
                            />
                        </div>
                        <Button type="submit" disabled={loading} className="bg-indigo-600 hover:bg-indigo-500 text-white gap-2">
                            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <SearchIcon className="h-4 w-4" />}
                            Analyze
                        </Button>
                    </form>
                </CardContent>
            </Card>

            <div className="space-y-4">
                {results.length > 0 ? (
                    results.map((result, i) => (
                        <Card key={i} className="border-border bg-card/20 hover:bg-card/40 transition-all duration-300 group">
                            <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <FileText className="h-4 w-4 text-indigo-400" />
                                        <CardTitle className="text-sm font-bold text-foreground">{result.title}</CardTitle>
                                    </div>
                                    <span className="text-[10px] font-mono text-muted-foreground uppercase bg-muted px-2 py-0.5 rounded">
                                        Relevance: {Math.round((1 - result.score) * 100)}%
                                    </span>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
                                    {result.text}
                                </p>
                                <div className="mt-4 flex items-center justify-between text-[10px] font-bold uppercase tracking-wider">
                                    <span className="text-indigo-400/70">{result.filename}</span>
                                    <Button variant="ghost" size="sm" className="h-7 text-[10px] gap-1 hover:text-indigo-300">
                                        View Resource <ExternalLink className="h-3 w-3" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                ) : !loading && query && (
                    <div className="text-center py-12 text-muted-foreground">
                        <p className="italic">No direct matches found in current neural index.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
