import { Case, Disease, Subsidy } from "./types";

const API_BASE = ""; // Relative URL, proxied via Next.js rewrites in next.config.js

export async function fetchCases(): Promise<Case[]> {
  const res = await fetch(`${API_BASE}/api/cases`);
  if (!res.ok) throw new Error("Failed to fetch cases");
  return res.json();
}

export async function fetchCaseById(id: string): Promise<Case> {
  const res = await fetch(`${API_BASE}/api/cases/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch case ${id}`);
  return res.json();
}

export async function fetchDiseases(): Promise<Disease[]> {
  const res = await fetch(`${API_BASE}/api/diseases`);
  if (!res.ok) throw new Error("Failed to fetch diseases");
  return res.json();
}

export async function saveDisease(disease: Disease): Promise<{ status: string; data: Disease }> {
  const res = await fetch(`${API_BASE}/api/diseases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(disease),
  });
  if (!res.ok) throw new Error("Failed to save disease");
  return res.json();
}

export async function fetchSubsidies(): Promise<Subsidy[]> {
  const res = await fetch(`${API_BASE}/api/subsidies`);
  if (!res.ok) throw new Error("Failed to fetch subsidies");
  return res.json();
}

export async function saveSubsidy(subsidy: Subsidy): Promise<{ status: string; data: Subsidy }> {
  const res = await fetch(`${API_BASE}/api/subsidies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(subsidy),
  });
  if (!res.ok) throw new Error("Failed to save subsidy");
  return res.json();
}

export interface SimulationPayload {
  phone: string;
  name: string;
  image_url: string;
  latitude: number;
  longitude: number;
  dialect: string;
}

export async function runSimulation(payload: SimulationPayload): Promise<Case> {
  const res = await fetch(`${API_BASE}/api/simulator`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Pipeline simulation failed");
  return res.json();
}
