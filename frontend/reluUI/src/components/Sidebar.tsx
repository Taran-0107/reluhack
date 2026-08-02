import { useState, useEffect } from "react";
import { Plus, Menu, History, Clock, MessageSquare, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "../lib/utils";
import { fetchHistory } from "../services/api";

interface SidebarProps {
  onNewResearch: () => void;
  onSelectHistory: (companyName: string) => void;
  refreshTrigger: number;
  currentSearch: string | null;
}

export function Sidebar({ onNewResearch, onSelectHistory, refreshTrigger, currentSearch }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [history, setHistory] = useState<{company_name: string, website: string, created_at: string}[]>([]);

  const [botToken, setBotToken] = useState(() => localStorage.getItem("discordBotToken") || "");
  const [channelId, setChannelId] = useState(() => localStorage.getItem("discordChannelId") || "");
  const [applicantName, setApplicantName] = useState(() => localStorage.getItem("applicantName") || "");
  const [applicantEmail, setApplicantEmail] = useState(() => localStorage.getItem("applicantEmail") || "");
  const [saved, setSaved] = useState(false);
  const [showDiscord, setShowDiscord] = useState(false);

  useEffect(() => {
    fetchHistory().then(setHistory).catch(console.error);
  }, [refreshTrigger]);

  const handleSaveConfig = () => {
    localStorage.setItem("discordBotToken", botToken);
    localStorage.setItem("discordChannelId", channelId);
    localStorage.setItem("applicantName", applicantName);
    localStorage.setItem("applicantEmail", applicantEmail);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div
      className={cn(
        "flex flex-col h-screen bg-[#0f172a] border-r border-slate-800 transition-all duration-300 z-20",
        isOpen ? "w-80" : "w-16"
      )}
    >
      <div className="flex items-center justify-between p-4 border-b border-slate-800">
        {isOpen && (
          <div className="flex items-center gap-3 mb-8 px-2">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 text-slate-900 font-bold text-xl shadow-lg shadow-amber-500/20">
              S
            </div>
            <div>
              <h1 className="font-semibold text-sm leading-tight text-slate-100">Search InCorporate</h1>
              <span className="text-[10px] text-slate-400 uppercase tracking-widest">Company Intelligence</span>
            </div>
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <Menu size={20} />
        </button>
      </div>

      <div className="p-4 flex-1 overflow-y-auto">
        <button
          onClick={onNewResearch}
          className={cn(
            "w-full flex items-center gap-3 p-3 rounded-lg border border-slate-700 hover:border-slate-600 hover:bg-slate-800 transition-all group text-sm text-slate-200",
            !isOpen && "justify-center px-0"
          )}
        >
          <Plus size={18} className="text-amber-400 group-hover:text-amber-300" />
          {isOpen && <span>New Research</span>}
        </button>

        {isOpen && (
          <div className="mt-8 space-y-6">
            <div>
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Recent Research</h2>
              <div className="space-y-1">
                {currentSearch && (
                  <button 
                    onClick={() => onSelectHistory(currentSearch)}
                    className="w-full text-left px-3 py-2.5 rounded-lg flex flex-col gap-1 bg-amber-900/20 hover:bg-amber-900/30 text-amber-200/80 border border-amber-900/30 animate-pulse transition-colors"
                  >
                    <div className="flex justify-between items-center w-full">
                      <span className="font-medium text-sm truncate">{currentSearch}</span>
                      <div className="w-2 h-2 rounded-full border border-amber-400 border-t-transparent animate-spin" />
                    </div>
                    <span className="text-[10px] opacity-70">Researching...</span>
                  </button>
                )}
                {history.length === 0 && !currentSearch ? (
                  <p className="text-xs text-slate-500 italic px-2">No history yet.</p>
                ) : (
                  history.map((item, i) => (
                    <button
                      key={i}
                      onClick={() => onSelectHistory(item.company_name)}
                      className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-slate-800/80 transition-colors flex flex-col gap-1 group"
                    >
                      <div className="flex justify-between items-center w-full">
                        <span className="font-medium text-sm text-slate-300 group-hover:text-amber-400 truncate pr-2">
                          {item.company_name}
                        </span>
                        <History size={12} className="text-slate-600 group-hover:text-amber-500 shrink-0" />
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono truncate">{item.website}</span>
                    </button>
                  ))
                )}
              </div>
            </div>

            <div className="mt-8 space-y-4">
              <button 
                onClick={() => setShowDiscord(!showDiscord)}
                className="w-full flex items-center justify-between text-xs font-semibold text-slate-500 hover:text-slate-300 uppercase tracking-wider mb-1 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <MessageSquare size={14} /> Discord Bot
                </div>
                {showDiscord ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
              
              {showDiscord && (
                <div className="p-4 bg-indigo-950/30 border border-indigo-900/50 rounded-lg space-y-4 animate-in slide-in-from-top-2 fade-in duration-200">
                  <p className="text-[11px] text-indigo-200/70">
                    Configure your bot credentials here. You can manually send any report to Discord using the button on the company card.
                  </p>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-1">Bot Token</label>
                      <input
                        type="password"
                        value={botToken}
                        onChange={(e) => setBotToken(e.target.value)}
                        placeholder="Bot token..."
                        className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-1">Channel ID</label>
                      <input
                        type="text"
                        value={channelId}
                        onChange={(e) => setChannelId(e.target.value)}
                        placeholder="000000000000000000"
                        className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  </div>

                  <div className="pt-2 border-t border-indigo-900/30">
                    <h3 className="text-[10px] font-semibold text-indigo-300 uppercase tracking-wider mb-3">Applicant Details</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-[10px] font-medium text-slate-400 mb-1">Full Name</label>
                        <input
                          type="text"
                          value={applicantName}
                          onChange={(e) => setApplicantName(e.target.value)}
                          placeholder="Your full name"
                          className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-medium text-slate-400 mb-1">Email Address</label>
                        <input
                          type="email"
                          value={applicantEmail}
                          onChange={(e) => setApplicantEmail(e.target.value)}
                          placeholder="email@example.com"
                          className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                        />
                      </div>
                    </div>
                  </div>

                  <button 
                    onClick={handleSaveConfig}
                    className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium py-2.5 rounded transition-colors"
                  >
                    {saved ? "Saved ✓" : "Save Discord Config"}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {isOpen && (
        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 flex justify-between">
          <span>Relu Consultancy</span>
          <span>v1.0</span>
        </div>
      )}
    </div>
  );
}
