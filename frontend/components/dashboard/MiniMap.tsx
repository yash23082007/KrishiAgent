"use client";

import dynamic from "next/dynamic";
import { Case } from "@/lib/types";
import { Maximize } from "lucide-react";
import Link from "next/link";

const DiseaseMap = dynamic(() => import("../map/DiseaseMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-zinc-900 animate-pulse rounded-2xl flex items-center justify-center text-xs text-zinc-500">
      Loading Live Map...
    </div>
  )
});

interface MiniMapProps {
  cases: Case[];
}

export default function MiniMap({ cases }: MiniMapProps) {
  return (
    <div className="glass-panel rounded-2xl p-6 flex flex-col h-full relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-white">Outbreak Geography</h3>
          <p className="text-xs text-zinc-500">Real-time disease density clusters</p>
        </div>
        <Link 
          href="/map"
          className="text-zinc-400 hover:text-green-400 transition-colors"
          title="Fullscreen Map"
        >
          <Maximize size={18} />
        </Link>
      </div>

      <div className="flex-1 min-h-[220px]">
        <DiseaseMap 
          cases={cases} 
          height="100%" 
          zoom={6} 
          center={[27.7011, 74.4712]}
        />
      </div>
    </div>
  );
}
