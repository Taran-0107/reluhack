import { useState, useRef, useEffect } from "react";
import { ArrowRight, Sparkles, AlertCircle, Terminal } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "./components/Sidebar";
import { CompanyCard } from "./components/CompanyCard";
import { startResearch, fetchResearch, fetchLogs } from "./services/api";
import type { ResearchResult } from "./types/api";

const STAGES = [
  "Searching...",
  "Crawling...",
  "Extracting data...",
  "AI Analysis...",
  "Generating PDF...",
];

function App() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState(0);
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [showConsole, setShowConsole] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const endOfChatRef = useRef<HTMLDivElement>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (result || loading) {
      endOfChatRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [result, loading]);

  useEffect(() => {
    if (showConsole) {
      logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, showConsole]);

  useEffect(() => {
    let logInterval: number;
    if (loading && showConsole) {
      logInterval = setInterval(() => {
        fetchLogs().then(data => setLogs(data.logs)).catch(() => {});
      }, 1000);
    }
    return () => clearInterval(logInterval);
  }, [loading, showConsole]);

  useEffect(() => {
    let interval: number;
    if (loading) {
      setStage(0);
      interval = setInterval(() => {
        setStage((prev) => (prev < 4 ? prev + 1 : prev));
      }, 4000);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const isUrl = input.includes(".") && !input.includes(" ");
    const payload: any = isUrl ? { website_url: input } : { company_name: input };

    try {
      const data = await startResearch(payload);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "An error occurred");
    } finally {
      setLoading(false);
      setStage(0);
    }
  };

  const handleSelectHistory = async (companyName: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await fetchResearch(companyName);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to load history.");
    } finally {
      setLoading(false);
      setStage(0);
    }
  };

  const handleNewResearch = () => {
    setResult(null);
    setInput("");
    setError(null);
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-200 overflow-hidden font-sans">
      <Sidebar onNewResearch={handleNewResearch} onSelectHistory={handleSelectHistory} />

      <main className="flex-1 flex flex-col relative h-full">
        {/* Top bar (mobile) */}
        <div className="p-4 flex items-center justify-between border-b border-slate-800 md:hidden">
           <h1 className="font-semibold text-slate-100">Research AI</h1>
        </div>

        {/* Canvas */}
        <div className="flex-1 overflow-y-auto w-full flex flex-col">
          {!result && !loading ? (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center max-w-2xl mx-auto mt-[-10vh]">
              <div className="text-amber-400 font-bold tracking-widest uppercase text-xs mb-6 flex items-center gap-2">
                <Sparkles size={14} /> AI-Powered Intelligence
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Know any company <br /> in minutes.
              </h1>
              <p className="text-slate-400 text-lg mb-10">
                Enter a company name or website URL to get AI-powered insights, competitor analysis, pain points, and a professional PDF report.
              </p>
              
              <div className="flex flex-wrap justify-center gap-3">
                {["stripe.com", "Tesla", "Microsoft", "OpenAI"].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="px-4 py-2 rounded-full border border-slate-700 bg-slate-800/50 hover:bg-slate-700 hover:border-slate-600 transition-colors text-sm text-slate-300"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 p-6 md:p-12 w-full max-w-6xl mx-auto space-y-8">
              {/* Timeline (Loading State) */}
              <AnimatePresence>
                {loading && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, height: 0, overflow: 'hidden' }}
                    className="w-full max-w-4xl mx-auto flex flex-col gap-4"
                  >
                    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-6 flex flex-col gap-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 text-amber-400 font-medium">
                          <div className="w-4 h-4 rounded-full border-2 border-amber-400 border-t-transparent animate-spin" />
                          {STAGES[stage]}
                        </div>
                        <button
                          onClick={() => setShowConsole(!showConsole)}
                          className="flex items-center gap-2 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium transition-colors"
                        >
                          <Terminal size={14} />
                          {showConsole ? "Hide Console" : "Show Console"}
                        </button>
                      </div>
                      
                      <div className="flex gap-2 w-full">
                        {STAGES.map((s, idx) => (
                          <div key={s} className="flex-1 h-1.5 rounded-full bg-slate-800 overflow-hidden relative">
                            <motion.div 
                              className="absolute inset-y-0 left-0 bg-amber-400"
                              initial={{ width: "0%" }}
                              animate={{ 
                                width: idx < stage ? "100%" : idx === stage ? "100%" : "0%" 
                              }}
                              transition={{ duration: idx === stage ? 4 : 0.2, ease: "linear" }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>

                    {showConsole && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="bg-black rounded-xl border border-slate-800 p-4 font-mono text-[10px] text-green-400 overflow-y-auto max-h-64 shadow-inner"
                      >
                        {logs.length === 0 ? (
                          <span className="text-slate-500">Waiting for logs...</span>
                        ) : (
                          logs.map((log, i) => (
                            <div key={i} className="mb-1 leading-tight break-all">
                              {log}
                            </div>
                          ))
                        )}
                        <div ref={logsEndRef} />
                      </motion.div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Error State */}
              {error && (
                <div className="w-full max-w-4xl mx-auto p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-start gap-3">
                  <AlertCircle size={20} className="mt-0.5 shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-1">Research Failed</h3>
                    <p className="text-sm opacity-90">{error}</p>
                  </div>
                </div>
              )}

              {/* Result State */}
              {result && <CompanyCard data={result} />}
              
              <div ref={endOfChatRef} className="h-20" />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-6 w-full max-w-4xl mx-auto absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#0f172a] via-[#0f172a] to-transparent pt-12">
          <form onSubmit={handleSubmit} className="relative group">
            <input
              disabled={loading}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter a company name (e.g. Stripe) or website URL (e.g. https://stripe.com)..."
              className="w-full bg-[#1e293b] border border-slate-700 rounded-xl py-4 pl-6 pr-32 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-amber-400/50 focus:ring-1 focus:ring-amber-400/50 transition-all shadow-xl disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2 top-2 bottom-2 px-6 bg-amber-400 hover:bg-amber-300 disabled:bg-slate-700 disabled:text-slate-500 text-slate-900 font-semibold rounded-lg flex items-center gap-2 transition-colors"
            >
              Research <ArrowRight size={16} />
            </button>
          </form>
          <div className="text-center text-[10px] text-slate-500 mt-4 uppercase tracking-widest font-semibold">
            ENTER TO RESEARCH
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
