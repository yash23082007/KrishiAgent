"use client";

import { usePathname } from "next/navigation";
import { Wifi, ShieldAlert, Cpu } from "lucide-react";

export default function TopBar() {
  const pathname = usePathname();

  // Get human-readable page name
  const getPageTitle = () => {
    if (pathname === "/") return "Command Center";
    if (pathname === "/map") return "Disease Outbreak Map";
    if (pathname === "/cases") return "Farmer Cases Log";
    if (pathname.startsWith("/cases/")) return "Detailed Case Execution Trace";
    if (pathname === "/knowledge") return "Knowledge Base Manager";
    return "KrishiAgent Dashboard";
  };

  return (
    <header className="h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-30">
      <h2 className="text-lg font-semibold text-white tracking-tight">
        {getPageTitle()}
      </h2>

      {/* Integration Badges */}
      <div className="flex items-center gap-4">
        {/* API Engine Badge */}
        <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-full px-3.5 py-1.5 text-xs text-zinc-300">
          <Cpu size={14} className="text-green-500 animate-pulse" />
          <span>Agents: <span className="font-semibold text-green-500">Autonomous Core</span></span>
        </div>

        {/* Database Status */}
        <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-full px-3.5 py-1.5 text-xs text-zinc-300">
          <Wifi size={14} className="text-green-400" />
          <span>Local SQLite Mode <span className="text-[10px] text-zinc-500 font-mono">(Ready)</span></span>
        </div>

        {/* Latency Meter */}
        <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-full px-3.5 py-1.5 text-xs text-zinc-300">
          <span>Avg Latency:</span>
          <span className="font-bold text-green-400 text-[11px]">4.8s</span>
        </div>
      </div>
    </header>
  );
}
