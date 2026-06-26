import os
import sqlite3
import httpx
from typing import Optional
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()

logger = get_logger("supabase_client")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

IS_SUPABASE_CONFIGURED = bool(SUPABASE_URL and SUPABASE_KEY)

DB_PATH = os.path.join(os.path.dirname(__file__), "local.db")

def init_local_db():
    """Initializes the local SQLite database mimicking the PostgreSQL tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        wa_phone_hash TEXT NOT NULL,
        wa_phone_prefix TEXT,
        image_url TEXT,
        location_lat REAL,
        location_lon REAL,
        location_pin TEXT,
        district TEXT,
        state TEXT,
        dialect TEXT DEFAULT 'hindi',
        crop TEXT,
        disease TEXT,
        scientific_name TEXT,
        severity TEXT,
        confidence REAL,
        affected_area INTEGER,
        symptoms TEXT, -- Stored as comma-separated values or JSON string
        urgency TEXT,
        weather_safe INTEGER, -- Boolean as 0 or 1
        weather_reason TEXT,
        safe_spray_window TEXT,
        treatment_name TEXT,
        treatment_dose TEXT,
        treatment_price INTEGER,
        subsidy_amount INTEGER,
        net_cost INTEGER,
        subsidy_scheme TEXT,
        dealer_name TEXT,
        dealer_phone TEXT,
        dealer_distance REAL,
        audio_url TEXT,
        audio_duration INTEGER,
        translated_text TEXT,
        latency_ms INTEGER,
        agent_trace TEXT, -- JSON string
        needs_review INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create diseases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diseases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop TEXT NOT NULL,
        disease_name TEXT NOT NULL,
        scientific_name TEXT,
        local_names TEXT, -- JSON string
        symptoms TEXT NOT NULL,
        treatment_text TEXT NOT NULL,
        treatments TEXT NOT NULL, -- JSON string
        severity_scale TEXT,
        image_urls TEXT, -- Comma-separated or JSON
        source TEXT,
        verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(crop, disease_name)
    )
    """)
    
    # Create subsidies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subsidies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_name TEXT NOT NULL,
        scheme_code TEXT,
        level TEXT,
        state TEXT,
        eligible_crops TEXT, -- Comma-separated or JSON
        eligible_inputs TEXT, -- Comma-separated or JSON
        benefit_type TEXT,
        amount_inr INTEGER,
        income_limit INTEGER,
        application_url TEXT,
        documentation TEXT, -- Comma-separated or JSON
        active INTEGER DEFAULT 1,
        valid_until TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

# Always initialize on load
init_local_db()

class SupabaseClient:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            "apikey": self.key or "",
            "Authorization": f"Bearer {self.key}" if self.key else "",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def insert_case(self, data: dict) -> dict:
        if IS_SUPABASE_CONFIGURED:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.url}/rest/v1/cases",
                        json=data,
                        headers=self.headers
                    )
                    if response.status_code in [200, 201]:
                        return response.json()[0]
                    else:
                        logger.error(f"Supabase insert failed: {response.text}")
            except Exception as e:
                logger.error(f"Supabase insertion exception: {e}")
        
        # Local SQLite fallback
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Prepare list fields as strings
        symptoms_str = ",".join(data.get("symptoms", [])) if isinstance(data.get("symptoms"), list) else str(data.get("symptoms", ""))
        import json
        agent_trace_str = json.dumps(data.get("agent_trace", {}))
        
        cursor.execute("""
        INSERT INTO cases (
            id, wa_phone_hash, wa_phone_prefix, image_url, location_lat, location_lon,
            location_pin, district, state, dialect, crop, disease, scientific_name,
            severity, confidence, affected_area, symptoms, urgency, weather_safe,
            weather_reason, safe_spray_window, treatment_name, treatment_dose,
            treatment_price, subsidy_amount, net_cost, subsidy_scheme, dealer_name,
            dealer_phone, dealer_distance, audio_url, audio_duration, translated_text,
            latency_ms, agent_trace, needs_review
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("id"), data.get("wa_phone_hash"), data.get("wa_phone_prefix"),
            data.get("image_url"), data.get("location_lat"), data.get("location_lon"),
            data.get("location_pin"), data.get("district"), data.get("state"),
            data.get("dialect"), data.get("crop"), data.get("disease"),
            data.get("scientific_name"), data.get("severity"), data.get("confidence"),
            data.get("affected_area"), symptoms_str, data.get("urgency"),
            1 if data.get("weather_safe") else 0, data.get("weather_reason"),
            data.get("safe_spray_window"), data.get("treatment_name"), data.get("treatment_dose"),
            data.get("treatment_price"), data.get("subsidy_amount"), data.get("net_cost"),
            data.get("subsidy_scheme"), data.get("dealer_name"), data.get("dealer_phone"),
            data.get("dealer_distance"), data.get("audio_url"), data.get("audio_duration"),
            data.get("translated_text"), data.get("latency_ms"), agent_trace_str,
            1 if data.get("needs_review") else 0
        ))
        
        conn.commit()
        conn.close()
        return data

    async def get_cases(self, limit: int = 50) -> list:
        if IS_SUPABASE_CONFIGURED:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.url}/rest/v1/cases?order=created_at.desc&limit={limit}",
                        headers=self.headers
                    )
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                logger.error(f"Supabase get_cases exception: {e}")
        
        # SQLite
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            d = dict(r)
            # Reconstruct list/dict structures
            d["weather_safe"] = bool(d["weather_safe"])
            d["needs_review"] = bool(d["needs_review"])
            try:
                import json
                d["symptoms"] = d["symptoms"].split(",") if d["symptoms"] else []
                d["agent_trace"] = json.loads(d["agent_trace"]) if d["agent_trace"] else {}
            except Exception:
                pass
            result.append(d)
        
        conn.close()
        return result

    async def get_case_by_id(self, case_id: str) -> Optional[dict]:
        if IS_SUPABASE_CONFIGURED:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.url}/rest/v1/cases?id=eq.{case_id}",
                        headers=self.headers
                    )
                    if response.status_code == 200:
                        rows = response.json()
                        if rows:
                            return rows[0]
            except Exception as e:
                logger.error(f"Supabase get_case_by_id exception: {e}")
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            d = dict(row)
            d["weather_safe"] = bool(d["weather_safe"])
            d["needs_review"] = bool(d["needs_review"])
            try:
                import json
                d["symptoms"] = d["symptoms"].split(",") if d["symptoms"] else []
                d["agent_trace"] = json.loads(d["agent_trace"]) if d["agent_trace"] else {}
            except Exception:
                pass
            return d
        return None
