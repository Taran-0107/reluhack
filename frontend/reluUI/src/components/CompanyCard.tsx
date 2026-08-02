import { Download, Check, Globe, MapPin, Phone, Send } from "lucide-react";
import type { ResearchResult } from "../types/api";
import { downloadPdf, sendToDiscord } from "../services/api";
import { useState } from "react";

interface CompanyCardProps {
  data: ResearchResult;
}

export function CompanyCard({ data }: CompanyCardProps) {
  const [downloading, setDownloading] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    await downloadPdf(data.company_name);
    setTimeout(() => setDownloading(false), 1500);
  };

  const handleSendToDiscord = async () => {
    const discordBotToken = localStorage.getItem("discordBotToken");
    const discordChannelId = localStorage.getItem("discordChannelId");
    
    if (!discordBotToken || !discordChannelId) {
      alert("Please configure Discord Bot Token and Channel ID in the sidebar first.");
      return;
    }

    setSending(true);
    try {
      await sendToDiscord(data.company_name, {
        discord_bot_token: discordBotToken,
        discord_channel_id: discordChannelId,
        applicant_name: localStorage.getItem("applicantName") || "",
        applicant_email: localStorage.getItem("applicantEmail") || ""
      });
      setSendSuccess(true);
      setTimeout(() => setSendSuccess(false), 3000);
    } catch (err) {
      alert("Failed to send to Discord.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-[#1e293b]/50 border border-slate-700 rounded-xl overflow-hidden shadow-2xl backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Header */}
      <div className="p-8 border-b border-slate-700 bg-slate-800/20 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">{data.company_name}</h1>
          <a
            href={data.website.startsWith('http') ? data.website : `https://${data.website}`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 text-amber-400 hover:text-amber-300 transition-colors text-sm font-medium"
          >
            <Globe size={16} />
            {data.website}
          </a>
        </div>
        <div className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-xs font-medium uppercase tracking-widest flex items-center gap-1.5">
          <Check size={14} />
          Research Complete
        </div>
      </div>

      <div className="p-8 space-y-8">
        {/* Contact Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-800">
            <div className="flex items-center gap-2 text-slate-500 mb-2 text-xs font-semibold uppercase tracking-wider">
              <Phone size={14} /> Phone
            </div>
            <p className="text-slate-200">{data.phone_number || "Not publicly listed"}</p>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-800">
            <div className="flex items-center gap-2 text-slate-500 mb-2 text-xs font-semibold uppercase tracking-wider">
              <MapPin size={14} /> Address
            </div>
            <p className="text-slate-200">{data.address || "Not publicly listed"}</p>
          </div>
        </div>

        {/* Products */}
        {data.products_services && data.products_services.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Products & Services</h3>
            <div className="flex flex-wrap gap-2">
              {data.products_services.map((product, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 rounded-lg text-sm"
                >
                  {product}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Pain Points */}
        {data.pain_points && data.pain_points.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">AI-Generated Pain Points</h3>
            <ul className="space-y-3">
              {data.pain_points.map((point, i) => (
                <li key={i} className="flex gap-3 text-slate-300 text-sm leading-relaxed">
                  <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Competitors */}
        {data.competitors && data.competitors.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Competitors</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {data.competitors.map((comp, i) => (
                <div key={i} className="p-4 bg-slate-900/50 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors group">
                  <h4 className="font-semibold text-slate-200 mb-1">{comp.name}</h4>
                  {comp.website && (
                    <a href={comp.website.startsWith('http') ? comp.website : `https://${comp.website}`} target="_blank" rel="noreferrer" className="text-xs text-slate-500 group-hover:text-amber-400 transition-colors">
                      {comp.website}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-slate-700 bg-slate-800/20 flex flex-wrap gap-4">
        <button
          onClick={handleDownload}
          className="flex items-center gap-2 px-6 py-3 bg-amber-400 hover:bg-amber-300 text-slate-900 font-semibold rounded-lg transition-colors"
        >
          <Download size={18} />
          {downloading ? "Downloading..." : "Download PDF"}
        </button>
        <button
          onClick={handleSendToDiscord}
          disabled={sending || sendSuccess}
          className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-lg transition-colors"
        >
          {sendSuccess ? <Check size={18} /> : <Send size={18} />}
          {sending ? "Sending..." : sendSuccess ? "Sent!" : "Send to Discord"}
        </button>
      </div>
    </div>
  );
}
