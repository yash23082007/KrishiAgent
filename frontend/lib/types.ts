export interface AgentReasoningDetail {
  agent: string;
  thinking: string;
  action_log: string;
  validation_status: string;
  reflection: string;
  retries: number;
  latency_ms: number;
  success: boolean;
  error?: string | null;
}

export interface AgentTrace {
  vision?: AgentReasoningDetail;
  climate?: AgentReasoningDetail;
  economic?: AgentReasoningDetail;
  voice?: AgentReasoningDetail;
}

export interface Case {
  id: string;
  wa_phone_hash: string;
  wa_phone_prefix?: string;
  image_url?: string;
  location_lat?: number;
  location_lon?: number;
  location_pin?: string;
  district?: string;
  state?: string;
  dialect?: string;
  
  // Vision
  crop?: string;
  disease?: string;
  scientific_name?: string;
  severity?: string;
  confidence?: number;
  affected_area?: number;
  symptoms?: string[];
  urgency?: string;
  
  // Climate
  weather_safe?: boolean;
  weather_reason?: string;
  safe_spray_window?: string;
  
  // Economic
  treatment_name?: string;
  treatment_dose?: string;
  treatment_price?: number;
  subsidy_amount?: number;
  net_cost?: number;
  subsidy_scheme?: string;
  dealer_name?: string;
  dealer_phone?: string;
  dealer_distance?: number;
  
  // Voice
  audio_url?: string;
  audio_duration?: number;
  translated_text?: string;
  
  // Metadata
  latency_ms?: number;
  agent_trace?: AgentTrace;
  needs_review?: boolean;
  created_at: string;
}

export interface Disease {
  id?: number;
  crop: string;
  disease_name: string;
  scientific_name?: string;
  local_names: Record<string, string>;
  symptoms: string;
  treatment_text: string;
  treatments: Array<{
    name: string;
    dosage: string;
    type: "chemical" | "organic";
  }>;
  severity_scale?: string;
  image_urls?: string[];
  source?: string;
  verified?: boolean;
}

export interface Subsidy {
  id?: number;
  scheme_name: string;
  scheme_code?: string;
  level: "central" | "state" | "district";
  state?: string;
  eligible_crops: string[];
  eligible_inputs: string[];
  benefit_type: string;
  amount_inr: number;
  income_limit?: number;
  application_url?: string;
  documentation: string[];
  active?: boolean;
  valid_until?: string;
}
