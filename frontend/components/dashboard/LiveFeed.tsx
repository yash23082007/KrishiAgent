import Link from "next/link";
import { Case } from "@/lib/types";
import { ArrowUpRight, Play, Eye } from "lucide-react";

interface LiveFeedProps {
  cases: Case[];
}

export default function LiveFeed({ cases }: LiveFeedProps) {
  const getSeverityBadgeClass = (severity?: string) => {
    const base = "px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ";
    if (severity === "critical") return base + "bg-red-500/20 text-red-400 border border-red-500/30";
    if (severity === "high") return base + "bg-orange-500/20 text-orange-400 border border-orange-500/30";
    if (severity === "medium") return base + "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";
    return base + "bg-green-500/20 text-green-400 border border-green-500/30";
  };

  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return "Just now";
    }
  };

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-6 border-b border-zinc-800 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white">Live Operations Feed</h3>
          <p className="text-xs text-zinc-500">Real-time incoming diagnostic stream</p>
        </div>
        <span className="flex h-2.5 w-2.5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
        </span>
      </div>

      <div className="flex-1 overflow-y-auto divide-y divide-zinc-800/50">
        {cases.length === 0 ? (
          <div className="p-8 text-center text-sm text-zinc-500">
            No farmer interactions registered yet. Trigger a simulation!
          </div>
        ) : (
          cases.map((c) => (
            <div 
              key={c.id} 
              className="p-5 flex items-center justify-between transition-colors duration-200 hover:bg-zinc-900/30"
            >
              <div className="flex items-center gap-4">
                {/* Visual Thumbnail */}
                <div className="w-11 h-11 bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden flex items-center justify-center text-xs text-zinc-600 relative">
                  {c.image_url ? (
                    <img 
                      src={c.image_url} 
                      alt={c.crop || "crop"} 
                      className="w-full h-full object-cover" 
                    />
                  ) : (
                    "No Img"
                  )}
                </div>

                {/* Farmer Details */}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white capitalize">
                      {c.crop || "Unknown Crop"}
                    </span>
                    <span className="text-xs text-zinc-500">•</span>
                    <span className="text-xs text-zinc-400 font-mono">
                      {c.wa_phone_hash.substring(0, 8)}...
                    </span>
                  </div>
                  <div className="mt-1 flex items-center gap-2">
                    <span className="text-xs text-zinc-400 capitalize">
                      {c.disease || "No diagnosis yet"}
                    </span>
                    <span className={getSeverityBadgeClass(c.severity)}>
                      {c.severity}
                    </span>
                  </div>
                </div>
              </div>

              {/* Timestamp & Action link */}
              <div className="flex items-center gap-4 text-right">
                <div>
                  <div className="text-xs font-semibold text-zinc-300">
                    {formatTime(c.created_at)}
                  </div>
                  <div className="text-[10px] text-zinc-500 mt-0.5">
                    {c.district}, {c.state}
                  </div>
                </div>
                
                <Link
                  href={`/cases/${c.id}`}
                  className="bg-zinc-900 hover:bg-green-500/20 border border-zinc-800 hover:border-green-500/30 text-zinc-400 hover:text-green-400 p-2 rounded-lg transition-all duration-200"
                  title="View Trace"
                >
                  <ArrowUpRight size={16} />
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
