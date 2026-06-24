"use client";

import { useEffect, useState } from "react";
import StatCard from "@/components/dashboard/StatCard";
import LiveFeed from "@/components/dashboard/LiveFeed";
import MiniMap from "@/components/dashboard/MiniMap";
import { fetchCases, runSimulation, fetchDiseases } from "@/lib/api";
import { Case } from "@/lib/types";
import { 
  Users, 
  Activity, 
  IndianRupee, 
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
  Volume2
} from "lucide-react";
import confetti from "canvas-confetti";

// Predefined crop options for simulation
const SIMULATION_CROPS = [
  {
    name: "Wheat Rust",
    value: "wheat",
    img: "/images/wheat_rust.png",
    desc: "Orange-brown powdery pustules covering leaf stems."
  },
  {
    name: "Rice Blight",
    value: "rice",
    img: "/images/rice_blight.png",
    desc: "Yellow-white drying leaf tips and stripes."
  },
  {
    name: "Cotton Leaf Curl",
    value: "cotton",
    img: "/images/cotton_curl.png",
    desc: "Upward curling and thickening of leaf veins."
  },
  {
    name: "Sugarcane Red Rot",
    value: "sugarcane",
    img: "/images/sugarcane_redrot.png",
    desc: "Internal stem rotting with a distinct sour odor."
  },
  {
    name: "Tomato Blight",
    value: "tomato",
    img: "/images/tomato_blight.png",
    desc: "Concentric target board pattern black leaf rings."
  }
];

export default function Page() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Simulator States
  const [simName, setSimName] = useState("Ram Singh");
  const [simPhone, setSimPhone] = useState("+91-94140-55555");
  const [simDialect, setSimDialect] = useState("marwari");
  const [simCropIdx, setSimCropIdx] = useState(0);
  const [simLat, setSimLat] = useState(27.7011);
  const [simLon, setSimLon] = useState(74.4712);
  
  // Pipeline status tracking
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [pipelineResult, setPipelineResult] = useState<Case | null>(null);

  const steps = [
    "Ingestion: Downloading image from Meta CDN...",
    "Agent 1 (Vision): Identifying leaf pathogens...",
    "Agent 2 (Climate): Open-Meteo wind & rain checks...",
    "Agent 3 (Economic): RAG database subsidy calculations...",
    "Agent 4 (Voice): Rendering local dialect translations...",
    "Done: Syncing telemetry case to SQLite database!"
  ];

  const loadData = async () => {
    try {
      const data = await fetchCases();
      setCases(data);
    } catch (e) {
      print("Failed to fetch cases", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Poll cases every 10 seconds for simulated real-time updates
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const triggerSimulation = async () => {
    if (pipelineRunning) return;
    
    setPipelineRunning(true);
    setPipelineStep(0);
    setPipelineResult(null);
    
    // Simulate multi-agent execution times
    const stepDurations = [1200, 1500, 1000, 1200, 1800, 800];
    
    for (let i = 0; i < steps.length - 1; i++) {
      await new Promise(r => setTimeout(r, stepDurations[i]));
      setPipelineStep(prev => prev + 1);
    }

    try {
      const result = await runSimulation({
        phone: simPhone,
        name: simName,
        image_url: SIMULATION_CROPS[simCropIdx].img,
        latitude: simLat,
        longitude: simLon,
        dialect: simDialect
      });
      
      await new Promise(r => setTimeout(r, stepDurations[steps.length - 1]));
      setPipelineResult(result);
      setPipelineStep(steps.length); // complete
      
      // Trigger confetti on success!
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
      
      // Refresh case log
      loadData();
    } catch (e) {
      alert("Simulation failed. Check if FastAPI backend is running on port 8000.");
    } finally {
      setPipelineRunning(false);
    }
  };

  // Stats calculation
  const totalCases = cases.length;
  const needsReviewCount = cases.filter(c => c.needs_review).length;
  const totalSubsidies = cases.reduce((acc, c) => acc + (c.subsidy_amount || 0), 0);
  const uniqueFarmers = new Set(cases.map(c => c.wa_phone_hash)).size;

  return (
    <div className="space-y-8">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Total Diagnoses"
          value={loading ? "..." : totalCases}
          icon={<Users size={20} className="text-green-400" />}
          description="cases resolved"
          trend="+12%"
        />
        <StatCard
          title="Unique Farmers"
          value={loading ? "..." : uniqueFarmers}
          icon={<Activity size={20} className="text-blue-400" />}
          description="registered contacts"
        />
        <StatCard
          title="Subsidies Unlocked"
          value={loading ? "..." : `Rs. ${totalSubsidies}`}
          icon={<IndianRupee size={20} className="text-emerald-400" />}
          description="direct farmer benefits"
          trend="+₹4.2k"
        />
        <StatCard
          title="Expert Reviews"
          value={loading ? "..." : needsReviewCount}
          icon={<AlertTriangle size={20} className="text-amber-400" />}
          description="cases below 60% confidence"
          trendColor="yellow"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Operations Feed - 7 cols */}
        <div className="lg:col-span-7 h-[500px]">
          <LiveFeed cases={cases} />
        </div>

        {/* Mini Map - 5 cols */}
        <div className="lg:col-span-5 h-[500px]">
          <MiniMap cases={cases} />
        </div>
      </div>

      {/* Simulator Section */}
      <div className="glass-panel-glow rounded-3xl p-8 border border-green-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/5 rounded-full filter blur-3xl"></div>
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="text-green-400 animate-pulse" size={24} />
          <h3 className="text-xl font-bold text-white">KrishiAgent Sandbox Simulator</h3>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Form Config - 5 cols */}
          <div className="lg:col-span-5 space-y-4">
            <h4 className="text-sm font-semibold text-zinc-400 mb-3 border-b border-zinc-800 pb-1">
              Configuration Parameters
            </h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-zinc-500 font-medium mb-1.5">Farmer Name</label>
                <input 
                  type="text" 
                  value={simName} 
                  onChange={e => setSimName(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-green-500"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-500 font-medium mb-1.5">WhatsApp Phone</label>
                <input 
                  type="text" 
                  value={simPhone} 
                  onChange={e => setSimPhone(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-green-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-zinc-500 font-medium mb-1.5">Target Dialect</label>
                <select 
                  value={simDialect}
                  onChange={e => setSimDialect(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-green-500"
                >
                  <option value="marwari">Marwari (Rajasthan)</option>
                  <option value="bhojpuri">Bhojpuri (UP/Bihar)</option>
                  <option value="gujarati">Gujarati</option>
                  <option value="hindi">Hindi Standard</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-zinc-500 font-medium mb-1.5">Latitude</label>
                  <input 
                    type="number" 
                    step="0.0001"
                    value={simLat} 
                    onChange={e => setSimLat(parseFloat(e.target.value))}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-2 py-2 text-sm text-zinc-200 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-zinc-500 font-medium mb-1.5">Longitude</label>
                  <input 
                    type="number" 
                    step="0.0001"
                    value={simLon} 
                    onChange={e => setSimLon(parseFloat(e.target.value))}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-2 py-2 text-sm text-zinc-200 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs text-zinc-500 font-medium mb-2">Select Crop Leaf Image</label>
              <div className="grid grid-cols-5 gap-2">
                {SIMULATION_CROPS.map((crop, idx) => (
                  <button
                    key={crop.name}
                    onClick={() => setSimCropIdx(idx)}
                    className={`aspect-square rounded-lg border-2 overflow-hidden flex flex-col relative ${
                      simCropIdx === idx 
                        ? "border-green-500 ring-2 ring-green-500/20" 
                        : "border-zinc-800 hover:border-zinc-700"
                    }`}
                    title={crop.desc}
                  >
                    <img src={crop.img} alt={crop.name} className="w-full h-full object-cover" />
                    <span className="absolute bottom-0 inset-x-0 bg-black/70 text-[9px] py-0.5 text-center text-zinc-300">
                      {crop.value}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={triggerSimulation}
              disabled={pipelineRunning}
              className="w-full bg-green-500 hover:bg-green-600 disabled:bg-zinc-800 text-black font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 shadow-[0_0_20px_rgba(34,197,94,0.2)] disabled:shadow-none mt-6"
            >
              <Play size={18} fill="currentColor" />
              {pipelineRunning ? "Agent Engine Working..." : "Kickoff 4-Agent Pipeline"}
            </button>
          </div>

          {/* Trace Window - 7 cols */}
          <div className="lg:col-span-7 bg-zinc-950 border border-zinc-850 rounded-2xl p-6 flex flex-col justify-between min-h-[350px]">
            <div>
              <h4 className="text-sm font-bold text-white mb-4 border-b border-zinc-900 pb-1.5 flex items-center justify-between">
                <span>Multi-Agent Live Execution Trace</span>
                {pipelineRunning && (
                  <span className="text-[10px] bg-green-500/20 text-green-400 border border-green-500/30 px-2 py-0.5 rounded-full font-mono animate-pulse">
                    Running
                  </span>
                )}
              </h4>
              
              {/* Stepper timeline */}
              <div className="space-y-4">
                {steps.map((step, idx) => {
                  const isCompleted = pipelineStep > idx;
                  const isCurrent = pipelineStep === idx;
                  const isPending = pipelineStep < idx;

                  return (
                    <div 
                      key={step} 
                      className={`flex items-center gap-3 transition-opacity duration-300 ${
                        isPending ? "opacity-30" : "opacity-100"
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                        isCompleted 
                          ? "bg-green-500 text-black" 
                          : isCurrent 
                          ? "bg-green-500/20 text-green-400 border border-green-500 animate-pulse" 
                          : "bg-zinc-900 text-zinc-600 border border-zinc-800"
                      }`}>
                        {isCompleted ? "✓" : idx + 1}
                      </div>
                      <span className={`text-xs ${isCurrent ? "text-green-400 font-semibold" : "text-zinc-400"}`}>
                        {step}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Results Display */}
            <div className="mt-6 border-t border-zinc-900 pt-6">
              {pipelineResult ? (
                <div className="bg-zinc-900/50 border border-green-500/20 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs text-zinc-400 font-medium">Diagnosis Verdict</div>
                      <div className="text-sm font-bold text-white capitalize">
                        {pipelineResult.crop} • {pipelineResult.disease}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Subsidized Cost</div>
                      <div className="text-sm font-bold text-green-400">Rs. {pipelineResult.net_cost}</div>
                    </div>
                  </div>
                  
                  {/* Generated Audio playback */}
                  <div className="flex items-center gap-3 bg-zinc-950 p-3 rounded-lg border border-zinc-800">
                    <div className="bg-green-500/20 text-green-400 p-2 rounded-full">
                      <Volume2 size={16} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider">Dialect Voice Note</div>
                      <div className="text-xs text-zinc-500 truncate mt-0.5 italic">
                        {pipelineResult.translated_text}
                      </div>
                    </div>
                    {pipelineResult.audio_url && (
                      <audio 
                        src={pipelineResult.audio_url} 
                        controls 
                        className="h-8 max-w-[200px]"
                      />
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-6 text-xs text-zinc-600 italic">
                  Awaiting agent pipeline kickoff trigger.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
