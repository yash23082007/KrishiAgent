"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { fetchCases } from "@/lib/api";
import { Case } from "@/lib/types";
import { ShieldAlert, RefreshCw } from "lucide-react";

const DiseaseMap = dynamic(() => import("@/components/map/DiseaseMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-center text-xs text-zinc-500 animate-pulse">
      Initialising Disease Heatmap layers...
    </div>
  )
});

export default function MapPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await fetchCases();
      setCases(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Outbreak Density Map</h3>
          <p className="text-xs text-zinc-500">Spatial distribution of crop infections across operational zones</p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-zinc-300 p-2.5 rounded-xl flex items-center gap-2 text-xs font-semibold"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh Map Data
        </button>
      </div>

      {/* Map container */}
      <div className="h-[600px]">
        <DiseaseMap cases={cases} height="100%" zoom={7} center={[27.7011, 74.4712]} />
      </div>

      {/* Quick cluster statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel rounded-2xl p-5">
          <div className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Top Infected District</div>
          <div className="text-xl font-bold text-white mt-1">Churu (Rajasthan)</div>
          <div className="text-xs text-zinc-500 mt-0.5">85% of simulated records located here</div>
        </div>
        <div className="glass-panel rounded-2xl p-5">
          <div className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Primary Crop Risk</div>
          <div className="text-xl font-bold text-red-400 mt-1">Wheat (Stem Rust)</div>
          <div className="text-xs text-zinc-500 mt-0.5">Highly infectious fungal spore vector active</div>
        </div>
        <div className="glass-panel rounded-2xl p-5">
          <div className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Climate Quarantine Alert</div>
          <div className="text-xl font-bold text-yellow-400 mt-1">High Humidity Alert</div>
          <div className="text-xs text-zinc-500 mt-0.5">Conditions favor rapid spore incubation</div>
        </div>
      </div>
    </div>
  );
}
