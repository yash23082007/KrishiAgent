"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchCases } from "@/lib/api";
import { Case } from "@/lib/types";
import { Eye, FileDown, Search, Filter } from "lucide-react";

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [filteredCases, setFilteredCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [search, setSearch] = useState("");
  const [cropFilter, setCropFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await fetchCases();
      setCases(data);
      setFilteredCases(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Apply filters
  useEffect(() => {
    let result = cases;

    if (search.trim() !== "") {
      const q = search.toLowerCase();
      result = result.filter(
        c => 
          (c.crop && c.crop.toLowerCase().includes(q)) || 
          (c.disease && c.disease.toLowerCase().includes(q)) ||
          (c.district && c.district.toLowerCase().includes(q)) ||
          c.wa_phone_hash.toLowerCase().includes(q)
      );
    }

    if (cropFilter !== "all") {
      result = result.filter(c => c.crop?.toLowerCase() === cropFilter.toLowerCase());
    }

    if (severityFilter !== "all") {
      result = result.filter(c => c.severity?.toLowerCase() === severityFilter.toLowerCase());
    }

    setFilteredCases(result);
  }, [search, cropFilter, severityFilter, cases]);

  const getSeverityBadgeClass = (severity?: string) => {
    const base = "px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ";
    if (severity === "critical") return base + "bg-red-500/20 text-red-400 border border-red-500/30";
    if (severity === "high") return base + "bg-orange-500/20 text-orange-400 border border-orange-500/30";
    if (severity === "medium") return base + "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";
    return base + "bg-green-500/20 text-green-400 border border-green-500/30";
  };

  // Export to CSV helper
  const exportCSV = () => {
    if (filteredCases.length === 0) return;
    
    const headers = [
      "Case ID", "Crop", "Disease", "Severity", "Confidence", "District", 
      "State", "Pesticide", "Retail Price", "Net Cost", "Subsidy Claimed", 
      "Latency (ms)", "Created At"
    ];
    
    const rows = filteredCases.map(c => [
      c.id, c.crop || "", c.disease || "", c.severity || "", c.confidence || "",
      c.district || "", c.state || "", c.treatment_name || "", c.treatment_price || 0,
      c.net_cost || 0, c.subsidy_amount || 0, c.latency_ms || 0, c.created_at
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `krishiagent_cases_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header and export controls */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Interactive Case Logs</h3>
          <p className="text-xs text-zinc-500">Historical records of diagnosed farmer crop pathology cases</p>
        </div>
        <button
          onClick={exportCSV}
          disabled={filteredCases.length === 0}
          className="bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-zinc-300 px-4 py-2 rounded-xl flex items-center gap-2 text-xs font-semibold disabled:opacity-55"
        >
          <FileDown size={14} />
          Export CSV Record
        </button>
      </div>

      {/* Filters Area */}
      <div className="glass-panel rounded-2xl p-5 grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
        {/* Search */}
        <div className="relative md:col-span-2">
          <Search size={16} className="absolute left-3.5 top-3 text-zinc-500" />
          <input
            type="text"
            placeholder="Search crop, disease, district, phone hash..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-zinc-300 placeholder-zinc-500 focus:outline-none focus:border-green-500"
          />
        </div>

        {/* Crop Filter */}
        <div>
          <select
            value={cropFilter}
            onChange={e => setCropFilter(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3.5 py-2.5 text-xs text-zinc-300 focus:outline-none"
          >
            <option value="all">All Crops</option>
            <option value="wheat">Wheat</option>
            <option value="rice">Rice</option>
            <option value="cotton">Cotton</option>
            <option value="sugarcane">Sugarcane</option>
            <option value="tomato">Tomato</option>
          </select>
        </div>

        {/* Severity Filter */}
        <div>
          <select
            value={severityFilter}
            onChange={e => setSeverityFilter(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-3.5 py-2.5 text-xs text-zinc-300 focus:outline-none"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Table grid */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-zinc-800/80">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/30 text-zinc-400 text-xs font-semibold">
                <th className="p-4">Crop</th>
                <th className="p-4">Disease / Pathology</th>
                <th className="p-4">Severity</th>
                <th className="p-4">Confidence</th>
                <th className="p-4">Pricing (Retail &rarr; Net)</th>
                <th className="p-4">Location</th>
                <th className="p-4">Latency</th>
                <th className="p-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/50 text-xs text-zinc-300">
              {loading ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-zinc-500">
                    Querying records database...
                  </td>
                </tr>
              ) : filteredCases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-zinc-500">
                    No cases match the query criteria.
                  </td>
                </tr>
              ) : (
                filteredCases.map(c => (
                  <tr key={c.id} className="hover:bg-zinc-900/10">
                    <td className="p-4 capitalize font-semibold text-white">
                      {c.crop}
                    </td>
                    <td className="p-4">
                      <div className="capitalize">{c.disease}</div>
                      <div className="text-[10px] text-zinc-500 font-mono italic">{c.scientific_name}</div>
                    </td>
                    <td className="p-4">
                      <span className={getSeverityBadgeClass(c.severity)}>
                        {c.severity}
                      </span>
                    </td>
                    <td className="p-4 font-mono font-medium">
                      {(c.confidence! * 100).toFixed(0)}%
                    </td>
                    <td className="p-4 font-medium">
                      <div className="text-zinc-500 line-through">Rs.{c.treatment_price}</div>
                      <div className="text-green-400 font-bold">Rs.{c.net_cost}</div>
                    </td>
                    <td className="p-4">
                      <div>{c.district}</div>
                      <div className="text-[10px] text-zinc-500">{c.state}</div>
                    </td>
                    <td className="p-4 font-mono text-zinc-400">
                      {c.latency_ms} ms
                    </td>
                    <td className="p-4 text-center">
                      <Link
                        href={`/cases/${c.id}`}
                        className="inline-flex items-center gap-1.5 bg-zinc-900 hover:bg-green-500/20 border border-zinc-800 hover:border-green-500/30 text-zinc-300 hover:text-green-400 px-3 py-1.5 rounded-lg transition-all duration-200"
                      >
                        <Eye size={12} />
                        Trace
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
