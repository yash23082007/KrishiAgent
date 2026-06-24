"use client";

import { useEffect, useState } from "react";
import { fetchDiseases, saveDisease, fetchSubsidies, saveSubsidy } from "@/lib/api";
import { Disease, Subsidy } from "@/lib/types";
import { BookOpen, Plus, Search, Tag, Sparkles } from "lucide-react";

export default function KnowledgePage() {
  const [activeTab, setActiveTab] = useState<"diseases" | "subsidies">("diseases");
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [subsidies, setSubsidies] = useState<Subsidy[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  // Form states
  const [showAddForm, setShowAddForm] = useState(false);
  
  // Disease Form States
  const [newCrop, setNewCrop] = useState("");
  const [newDiseaseName, setNewDiseaseName] = useState("");
  const [newScientific, setNewScientific] = useState("");
  const [newSymptoms, setNewSymptoms] = useState("");
  const [newTreatmentText, setNewTreatmentText] = useState("");
  const [newTreatmentName, setNewTreatmentName] = useState("");
  const [newTreatmentDose, setNewTreatmentDose] = useState("");
  const [newSource, setNewSource] = useState("");

  // Subsidy Form States
  const [newSchemeName, setNewSchemeName] = useState("");
  const [newLevel, setNewLevel] = useState<"central" | "state">("central");
  const [newSubState, setNewSubState] = useState("");
  const [newEligibleCrops, setNewEligibleCrops] = useState("");
  const [newEligibleInputs, setNewEligibleInputs] = useState("");
  const [newBenefitType, setNewBenefitType] = useState("50% cost subsidy");
  const [newAmountInr, setNewAmountInr] = useState(300);

  const loadData = async () => {
    try {
      setLoading(true);
      if (activeTab === "diseases") {
        const data = await fetchDiseases();
        setDiseases(data);
      } else {
        const data = await fetchSubsidies();
        setSubsidies(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    setShowAddForm(false);
  }, [activeTab]);

  const handleAddDisease = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCrop || !newDiseaseName || !newSymptoms || !newTreatmentText) {
      alert("Please fill in required fields.");
      return;
    }
    
    const data: Disease = {
      crop: newCrop.toLowerCase().trim(),
      disease_name: newDiseaseName.toLowerCase().trim(),
      scientific_name: newScientific.trim(),
      local_names: { hindi: "", marwari: "" },
      symptoms: newSymptoms.trim(),
      treatment_text: newTreatmentText.trim(),
      treatments: [
        {
          name: newTreatmentName.toLowerCase().trim() || "fungicide",
          dosage: newTreatmentDose.trim() || "2g per liter",
          type: "chemical"
        }
      ],
      source: newSource.trim() || "ICAR Field Advisory",
      verified: true
    };

    try {
      await saveDisease(data);
      alert("Disease entry added to knowledge base successfully!");
      setShowAddForm(false);
      
      // Reset form
      setNewCrop("");
      setNewDiseaseName("");
      setNewScientific("");
      setNewSymptoms("");
      setNewTreatmentText("");
      setNewTreatmentName("");
      setNewTreatmentDose("");
      setNewSource("");
      
      loadData();
    } catch (e) {
      alert("Failed to save disease entry.");
    }
  };

  const handleAddSubsidy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSchemeName || !newEligibleCrops || !newEligibleInputs) {
      alert("Please fill in required fields.");
      return;
    }

    const data: Subsidy = {
      scheme_name: newSchemeName.trim(),
      level: newLevel,
      state: newLevel === "state" ? newSubState.trim() : "",
      eligible_crops: newEligibleCrops.split(",").map(c => c.trim().toLowerCase()),
      eligible_inputs: newEligibleInputs.split(",").map(i => i.trim().toLowerCase()),
      benefit_type: newBenefitType.trim(),
      amount_inr: Number(newAmountInr),
      documentation: ["Aadhaar Card", "Pesticide Bill Receipt"],
      active: true
    };

    try {
      await saveSubsidy(data);
      alert("Subsidy scheme added successfully!");
      setShowAddForm(false);
      
      setNewSchemeName("");
      setNewEligibleCrops("");
      setNewEligibleInputs("");
      setNewSubState("");
      setNewAmountInr(300);
      
      loadData();
    } catch (e) {
      alert("Failed to save subsidy scheme.");
    }
  };

  // Filter local state
  const filteredDiseases = diseases.filter(d => 
    d.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.disease_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.symptoms.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredSubsidies = subsidies.filter(s => 
    s.scheme_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.benefit_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Knowledge Base Editor</h3>
          <p className="text-xs text-zinc-500">Configure agronomist pathology definitions and government financial subsidies</p>
        </div>
        
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-green-500 hover:bg-green-600 text-black px-4 py-2 rounded-xl flex items-center gap-2 text-xs font-bold shadow-[0_0_15px_rgba(34,197,94,0.15)]"
        >
          <Plus size={16} />
          {showAddForm ? "View Directory" : activeTab === "diseases" ? "Add Disease Entry" : "Add Subsidy Scheme"}
        </button>
      </div>

      {/* Tabs Menu */}
      {!showAddForm && (
        <div className="flex items-center justify-between gap-4 border-b border-zinc-800 pb-px">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab("diseases")}
              className={`pb-3 text-sm font-semibold transition-colors relative ${
                activeTab === "diseases" ? "text-green-400 border-b-2 border-green-500" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Crop Disease Dictionary ({diseases.length})
            </button>
            <button
              onClick={() => setActiveTab("subsidies")}
              className={`pb-3 text-sm font-semibold transition-colors relative ${
                activeTab === "subsidies" ? "text-green-400 border-b-2 border-green-500" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Government Subsidies Schemes ({subsidies.length})
            </button>
          </div>

          {/* Quick search input */}
          <div className="relative max-w-xs w-full pb-2">
            <Search size={14} className="absolute left-3 top-2.5 text-zinc-500" />
            <input
              type="text"
              placeholder="Filter list..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-zinc-300 placeholder-zinc-500 focus:outline-none focus:border-green-500"
            />
          </div>
        </div>
      )}

      {/* Add Form Forms */}
      {showAddForm ? (
        <div className="glass-panel rounded-2xl p-8 max-w-3xl mx-auto border border-zinc-800/80">
          <h4 className="font-bold text-white mb-6 flex items-center gap-2">
            <BookOpen size={18} className="text-green-400" />
            New {activeTab === "diseases" ? "Crop Disease Diagnosis Definition" : "Subsidy Scheme Profile"}
          </h4>

          {activeTab === "diseases" ? (
            <form onSubmit={handleAddDisease} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Crop (e.g. Wheat, Rice)*</label>
                  <input
                    type="text"
                    required
                    value={newCrop}
                    onChange={e => setNewCrop(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Disease Name (e.g. Stem Rust)*</label>
                  <input
                    type="text"
                    required
                    value={newDiseaseName}
                    onChange={e => setNewDiseaseName(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-zinc-400 mb-1">Scientific Classification Name (Optional)</label>
                <input
                  type="text"
                  value={newScientific}
                  onChange={e => setNewScientific(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs text-zinc-400 mb-1">Pathogen Symptoms Description*</label>
                <textarea
                  required
                  rows={2}
                  value={newSymptoms}
                  onChange={e => setNewSymptoms(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                  placeholder="Visually observable patterns such as colored pustules, vein discoloration, spots..."
                />
              </div>

              <div className="border-t border-zinc-800 pt-4 space-y-4">
                <h5 className="text-xs font-bold text-green-400 uppercase tracking-wider">Recommended Medicine (Ingest Tool matching)</h5>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-zinc-400 mb-1">Active Ingredient Name (e.g. propiconazole)*</label>
                    <input
                      type="text"
                      value={newTreatmentName}
                      onChange={e => setNewTreatmentName(e.target.value)}
                      className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-zinc-400 mb-1">Application Dosage (e.g. 2 ml per liter)*</label>
                    <input
                      type="text"
                      value={newTreatmentDose}
                      onChange={e => setNewTreatmentDose(e.target.value)}
                      className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Treatment/Mixing Guidelines*</label>
                  <textarea
                    required
                    rows={2}
                    value={newTreatmentText}
                    onChange={e => setNewTreatmentText(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                    placeholder="Steps for dissolving, spraying ratios, and acre application instructions..."
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Research Source Agency (e.g. IARI)</label>
                  <input
                    type="text"
                    value={newSource}
                    onChange={e => setNewSource(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex gap-4 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 border border-zinc-800 rounded-xl text-xs text-zinc-400 hover:text-zinc-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-green-500 hover:bg-green-600 text-black px-4 py-2 rounded-xl text-xs font-bold"
                >
                  Save Disease Entry
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleAddSubsidy} className="space-y-4">
              <div>
                <label className="block text-xs text-zinc-400 mb-1">Scheme Name (e.g. PM-KISAN, RKVY)*</label>
                <input
                  type="text"
                  required
                  value={newSchemeName}
                  onChange={e => setNewSchemeName(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Administrative Level</label>
                  <select
                    value={newLevel}
                    onChange={e => setNewLevel(e.target.value as any)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                  >
                    <option value="central">Central Government Scheme</option>
                    <option value="state">State Government Scheme</option>
                  </select>
                </div>
                {newLevel === "state" && (
                  <div>
                    <label className="block text-xs text-zinc-400 mb-1">State Scope (e.g. Rajasthan)*</label>
                    <input
                      type="text"
                      required
                      value={newSubState}
                      onChange={e => setNewSubState(e.target.value)}
                      className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                    />
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Eligible Crops (comma-separated)*</label>
                  <input
                    type="text"
                    required
                    placeholder="wheat, rice, pulses"
                    value={newEligibleCrops}
                    onChange={e => setNewEligibleCrops(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Eligible Pesticides/Inputs (comma-separated)*</label>
                  <input
                    type="text"
                    required
                    placeholder="propiconazole, tebuconazole, fungicide"
                    value={newEligibleInputs}
                    onChange={e => setNewEligibleInputs(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Benefit Calculation Formula*</label>
                  <input
                    type="text"
                    required
                    placeholder="50% cost subsidy"
                    value={newBenefitType}
                    onChange={e => setNewBenefitType(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Max Benefit Amount (INR)*</label>
                  <input
                    type="number"
                    required
                    value={newAmountInr}
                    onChange={e => setNewAmountInr(Number(e.target.value))}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex gap-4 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 border border-zinc-800 rounded-xl text-xs text-zinc-400 hover:text-zinc-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-green-500 hover:bg-green-600 text-black px-4 py-2 rounded-xl text-xs font-bold"
                >
                  Save Subsidy Scheme
                </button>
              </div>
            </form>
          )}
        </div>
      ) : (
        /* Directory listings */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {activeTab === "diseases" ? (
            filteredDiseases.map((d, index) => (
              <div key={index} className="glass-panel rounded-2xl p-6 border border-zinc-800 space-y-4 hover:border-zinc-700 transition-colors">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded-md font-bold uppercase tracking-wider text-green-400">
                      {d.crop}
                    </span>
                    <span className="text-zinc-500 text-xs font-mono italic">{d.scientific_name}</span>
                  </div>
                  <h4 className="text-base font-bold text-white capitalize mt-1.5">{d.disease_name}</h4>
                </div>

                <div className="text-xs text-zinc-400 leading-relaxed bg-zinc-950 p-4 rounded-xl border border-zinc-900">
                  <span className="block font-bold text-white text-[10px] uppercase tracking-wider mb-1">Symptoms description</span>
                  {d.symptoms}
                </div>

                <div className="text-xs text-zinc-400 space-y-2">
                  <div>
                    <span className="font-semibold text-zinc-500">Target Ingredient: </span>
                    <span className="bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded font-mono text-[10px] text-zinc-300 capitalize">
                      {d.treatments?.[0]?.name}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-zinc-500">Treatment Advice: </span>
                    <p className="mt-1 text-zinc-300">{d.treatment_text}</p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            filteredSubsidies.map((s, index) => (
              <div key={index} className="glass-panel rounded-2xl p-6 border border-zinc-800 space-y-4 hover:border-zinc-700 transition-colors">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded-md font-bold uppercase tracking-wider text-emerald-400">
                      {s.level} scheme {s.state ? `• ${s.state}` : ""}
                    </span>
                    <h4 className="text-base font-bold text-white mt-1.5">{s.scheme_name}</h4>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Max benefit</span>
                    <div className="text-base font-bold text-green-400">Rs. {s.amount_inr}</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="block font-semibold text-zinc-500">Eligible Crops</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {s.eligible_crops.map(c => (
                        <span key={c} className="bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded text-[9px] text-zinc-300 capitalize">
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="block font-semibold text-zinc-500">Covered Pesticides</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {s.eligible_inputs.map(i => (
                        <span key={i} className="bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded text-[9px] text-zinc-300 capitalize">
                          {i}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="text-xs border-t border-zinc-900 pt-3 flex items-center justify-between text-zinc-400">
                  <span>Benefit: <span className="text-green-400 font-semibold">{s.benefit_type}</span></span>
                  <a href={s.application_url || "#"} target="_blank" className="text-[10px] text-blue-400 font-bold hover:underline">
                    Portal Link &rarr;
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
