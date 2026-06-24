"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchCaseById } from "@/lib/api";
import { Case } from "@/lib/types";
import { 
  ArrowLeft, 
  Volume2, 
  MapPin, 
  Clock, 
  Activity, 
  DollarSign, 
  CloudSun,
  Camera,
  Bot
} from "lucide-react";

export default function CaseDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!params?.id) return;
      try {
        setLoading(true);
        const data = await fetchCaseById(params.id as string);
        setCaseData(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params?.id]);

  if (loading) {
    return <div className="text-center py-12 text-zinc-500">Retrieving case trace record...</div>;
  }

  if (!caseData) {
    return (
      <div className="text-center py-12 space-y-4">
        <div className="text-red-400">Case record not found.</div>
        <button onClick={() => router.push("/cases")} className="text-zinc-400 underline">
          Back to Case Logs
        </button>
      </div>
    );
  }

  const trace = caseData.agent_trace || {};

  return (
    <div className="space-y-6">
      {/* Back button */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.push("/cases")}
          className="bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 p-2.5 rounded-xl text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <ArrowLeft size={16} />
        </button>
        <div>
          <h3 className="text-xl font-bold text-white">Case Telemetry Profile</h3>
          <p className="text-xs text-zinc-500">ID: {caseData.id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Input Info & Audio (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Farmer Input Card */}
          <div className="glass-panel rounded-2xl p-6 space-y-4">
            <h4 className="font-semibold text-white border-b border-zinc-800 pb-2 flex items-center gap-2">
              <Camera size={16} className="text-zinc-400" />
              Farmer Ingest Source
            </h4>
            
            {caseData.image_url ? (
              <div className="aspect-video w-full bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden relative">
                <img 
                  src={caseData.image_url} 
                  alt="farmer upload" 
                  className="w-full h-full object-cover" 
                />
              </div>
            ) : (
              <div className="h-36 w-full bg-zinc-900 rounded-xl flex items-center justify-center text-xs text-zinc-500">
                No image registered
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-xs text-zinc-400 mt-4">
              <div>
                <span className="block text-zinc-500">Farmer Contact</span>
                <span className="font-mono text-zinc-300">{caseData.wa_phone_hash.substring(0, 12)}...</span>
              </div>
              <div>
                <span className="block text-zinc-500">Dialect Request</span>
                <span className="capitalize text-green-400 font-semibold">{caseData.dialect}</span>
              </div>
              <div>
                <span className="block text-zinc-500">Resolved Location</span>
                <span>{caseData.district}, {caseData.state}</span>
              </div>
              <div>
                <span className="block text-zinc-500">Postal Pin Code</span>
                <span className="font-mono">{caseData.location_pin}</span>
              </div>
            </div>
          </div>

          {/* Delivered Voice Note */}
          <div className="glass-panel rounded-2xl p-6 space-y-4">
            <h4 className="font-semibold text-white border-b border-zinc-800 pb-2 flex items-center gap-2">
              <Volume2 size={16} className="text-green-500" />
              Delivered Audio Advisory
            </h4>

            {caseData.audio_url ? (
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 space-y-3">
                <div className="flex items-center gap-3">
                  <div className="bg-green-500/20 text-green-400 p-2.5 rounded-full">
                    <Volume2 size={18} />
                  </div>
                  <div>
                    <div className="text-xs text-zinc-300 font-bold uppercase">Voice Note Duration</div>
                    <div className="text-xs text-zinc-500">{caseData.audio_duration} seconds</div>
                  </div>
                </div>
                <audio src={caseData.audio_url} controls className="w-full h-9 mt-2" />
              </div>
            ) : (
              <div className="text-xs text-zinc-500 italic">No audio note synthesized for this case.</div>
            )}

            {/* Translated dialect text */}
            <div className="mt-4 bg-zinc-950 p-4 rounded-xl border border-zinc-900 space-y-2">
              <div className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">Translated Dialect Transcript</div>
              <p className="text-xs text-zinc-300 leading-relaxed font-medium">
                {caseData.translated_text || "No transcript matches."}
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Agent Execution Steps (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="glass-panel rounded-2xl p-6 space-y-6">
            <h4 className="font-semibold text-white border-b border-zinc-800 pb-2 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Bot size={16} className="text-zinc-400" />
                Autonomous Agent Execution Trace
              </span>
              <span className="text-xs font-mono bg-zinc-900 border border-zinc-800 px-3 py-1 rounded text-zinc-400 flex items-center gap-1.5">
                <Clock size={12} />
                {caseData.latency_ms} ms
              </span>
            </h4>

            {/* Steps Timeline */}
            <div className="space-y-8 relative pl-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-zinc-800">
              
              {/* Step 1: Vision Pathologist */}
              <div className="relative">
                {/* Dot */}
                <div className="absolute -left-[22px] top-1 w-3 h-3 rounded-full bg-green-500 border border-zinc-950 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-white uppercase tracking-wider">Agent 1: Dr. Krishi Crop Pathologist</h5>
                    <span className="text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-zinc-500">Vision model</span>
                  </div>
                  <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 space-y-2 text-xs text-zinc-300">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-zinc-500">Detected Infection:</span>
                        <div className="font-semibold capitalize text-white">{caseData.crop} - {caseData.disease}</div>
                      </div>
                      <div>
                        <span className="text-zinc-500">Model Confidence:</span>
                        <div className="font-semibold text-white">{(caseData.confidence! * 100).toFixed(1)}%</div>
                      </div>
                    </div>
                    <div>
                      <span className="text-zinc-500">Observed Symptoms:</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {caseData.symptoms?.map(sym => (
                          <span key={sym} className="bg-zinc-950 px-2 py-0.5 rounded text-[10px] border border-zinc-800 capitalize">
                            {sym}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 2: Climate Meteorologist */}
              <div className="relative">
                {/* Dot */}
                <div className="absolute -left-[22px] top-1 w-3 h-3 rounded-full bg-blue-500 border border-zinc-950 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-white uppercase tracking-wider">Agent 2: Agri-Meteorologist</h5>
                    <span className="text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-zinc-500">Open-Meteo REST</span>
                  </div>
                  <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 space-y-2 text-xs text-zinc-300">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-zinc-500">Spray Conditions Safety:</span>
                        <div className={`font-semibold ${caseData.weather_safe ? 'text-green-400' : 'text-red-400'}`}>
                          {caseData.weather_safe ? "SAFE TO SPRAY" : "UNSAFE TO SPRAY"}
                        </div>
                      </div>
                      <div>
                        <span className="text-zinc-500">Next Recommended Window:</span>
                        <div className="font-semibold text-white">{caseData.safe_spray_window}</div>
                      </div>
                    </div>
                    <div>
                      <span className="text-zinc-500">Climate Reason:</span>
                      <p className="mt-0.5 text-zinc-400">{caseData.weather_reason}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3: Economic Market Advisor */}
              <div className="relative">
                {/* Dot */}
                <div className="absolute -left-[22px] top-1 w-3 h-3 rounded-full bg-emerald-500 border border-zinc-950 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-white uppercase tracking-wider">Agent 3: Market & subsidy advisor</h5>
                    <span className="text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-zinc-500">Subsidies RAG database</span>
                  </div>
                  <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 space-y-2 text-xs text-zinc-300">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <span className="text-zinc-500">Retail price:</span>
                        <div className="font-semibold text-white">Rs. {caseData.treatment_price}</div>
                      </div>
                      <div>
                        <span className="text-zinc-500">Govt subsidy:</span>
                        <div className="font-semibold text-green-400">- Rs. {caseData.subsidy_amount}</div>
                      </div>
                      <div>
                        <span className="text-zinc-500">Net Cost:</span>
                        <div className="font-bold text-green-400">Rs. {caseData.net_cost}</div>
                      </div>
                    </div>
                    <div className="border-t border-zinc-800/60 pt-2 mt-2 grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-zinc-500">Matched Scheme:</span>
                        <div className="font-semibold text-zinc-300">{caseData.subsidy_scheme || "No matching schemes found"}</div>
                      </div>
                      <div>
                        <span className="text-zinc-500">Nearest Dealer:</span>
                        <div className="font-semibold text-zinc-300">
                          {caseData.dealer_name} ({caseData.dealer_distance} km away)
                          <div className="text-[10px] text-zinc-500 mt-0.5 font-mono">{caseData.dealer_phone}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 4: Voice Linguist */}
              <div className="relative">
                {/* Dot */}
                <div className="absolute -left-[22px] top-1 w-3 h-3 rounded-full bg-purple-500 border border-zinc-950 shadow-[0_0_8px_rgba(168,85,247,0.6)]"></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-white uppercase tracking-wider">Agent 4: Dialect Linguist Voice Advisor</h5>
                    <span className="text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-zinc-500">Gemini + gTTS</span>
                  </div>
                  <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 space-y-2 text-xs text-zinc-300">
                    <div>
                      <span className="text-zinc-500">Dialect Translation:</span>
                      <p className="mt-1 text-zinc-400 italic">
                        &quot;{caseData.translated_text}&quot;
                      </p>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
