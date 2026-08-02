import { useState, useEffect } from "react";
import { Plus, Menu, History, Clock } from "lucide-react";
import { cn } from "../lib/utils";
import { fetchHistory } from "../services/api";

interface SidebarProps {
  onNewResearch: () => void;
  onSelectHistory: (companyName: string) => void;
}

export function Sidebar({ onNewResearch, onSelectHistory }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [history, setHistory] = useState<{company_name: string, website: string, created_at: string}[]>([]);

  const [botToken, setBotToken] = useState(() => localStorage.getItem("discordBotToken") || "");
  const [channelId, setChannelId] = useState(() => localStorage.getItem("discordChannelId") || "");
  const [applicantName, setApplicantName] = useState(() => localStorage.getItem("applicantName") || "");
  const [applicantEmail, setApplicantEmail] = useState(() => localStorage.getItem("applicantEmail") || "");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchHistory().then(setHistory).catch(console.error);
  }, [isOpen]); // Refresh when sidebar opens

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
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-md bg-amber-400 flex items-center justify-center font-bold text-slate-900">
              R
            </div>
            <div>
              <h1 className="font-semibold text-sm leading-tight text-slate-100">Research AI</h1>
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
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                <History size={14} /> History
              </h2>
              <div className="space-y-2">
                {history.length === 0 ? (
                  <p className="text-xs text-slate-500">No previous research found.</p>
                ) : (
                  history.map((h, i) => (
                    <button
                      key={i}
                      onClick={() => onSelectHistory(h.company_name)}
                      className="w-full text-left p-3 rounded-lg bg-slate-900/50 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 transition-colors group flex flex-col gap-1"
                    >
                      <span className="text-sm text-slate-300 font-medium group-hover:text-amber-400">{h.company_name}</span>
                      <div className="flex items-center gap-2 text-[10px] text-slate-500">
                        <Clock size={10} />
                        {new Date(h.created_at).toLocaleDateString()}
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            <div>
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Discord Bot Integration</h2>
              <div className="p-4 bg-indigo-950/30 border border-indigo-900/50 rounded-lg space-y-4">
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
