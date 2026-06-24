"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Map, 
  FileSpreadsheet, 
  BookOpen, 
  Sprout 
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    { name: "Command Center", path: "/", icon: LayoutDashboard },
    { name: "Disease Map", path: "/map", icon: Map },
    { name: "Case Log", path: "/cases", icon: FileSpreadsheet },
    { name: "Knowledge Base", path: "/knowledge", icon: BookOpen },
  ];

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col h-screen sticky top-0">
      {/* Brand Logo Header */}
      <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
        <div className="bg-green-500/20 p-2 rounded-lg text-green-500 border border-green-500/30 shadow-[0_0_10px_rgba(34,197,94,0.2)]">
          <Sprout size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-1">
            Krishi<span className="text-green-500">Agent</span>
          </h1>
          <p className="text-[10px] text-zinc-500 tracking-wider font-semibold uppercase">
            Enterprise Edition
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.path;
          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500 pl-3.5"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
              }`}
            >
              <Icon size={20} className={isActive ? "text-green-400" : "text-zinc-400"} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-6 border-t border-zinc-800">
        <div className="bg-zinc-900/60 p-4 rounded-xl border border-zinc-800 text-xs text-zinc-500 text-center">
          Serves 86M+ Farmers
          <div className="text-[10px] text-green-500 font-medium mt-1">
            Active Fallbacks Active
          </div>
        </div>
      </div>
    </aside>
  );
}
