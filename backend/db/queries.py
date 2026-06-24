import json
import sqlite3
from typing import List, Optional
from db.supabase_client import SupabaseClient, DB_PATH, IS_SUPABASE_CONFIGURED

client = SupabaseClient()

async def create_case(case_data: dict) -> dict:
    """Inserts a new farmer case."""
    return await client.insert_case(case_data)

async def get_all_cases(limit: int = 50) -> List[dict]:
    """Returns the list of cases, ordered by creation date descending."""
    return await client.get_cases(limit)

async def get_case(case_id: str) -> Optional[dict]:
    """Retrieves a single case by ID."""
    return await client.get_case_by_id(case_id)

# Disease Knowledge Base Queries
async def get_all_diseases() -> List[dict]:
    """Retrieves all diseases from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diseases ORDER BY crop, disease_name")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["local_names"] = json.loads(d["local_names"]) if d["local_names"] else {}
            d["treatments"] = json.loads(d["treatments"]) if d["treatments"] else []
            d["image_urls"] = d["image_urls"].split(",") if d["image_urls"] else []
        except Exception:
            pass
        result.append(d)
    return result

async def get_disease(crop: str, disease_name: str) -> Optional[dict]:
    """Retrieves treatment details for a crop disease."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM diseases WHERE LOWER(crop) = LOWER(?) AND LOWER(disease_name) = LOWER(?)",
        (crop.strip(), disease_name.strip())
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        d = dict(row)
        try:
            d["local_names"] = json.loads(d["local_names"]) if d["local_names"] else {}
            d["treatments"] = json.loads(d["treatments"]) if d["treatments"] else []
            d["image_urls"] = d["image_urls"].split(",") if d["image_urls"] else []
        except Exception:
            pass
        return d
    return None

async def upsert_disease(disease_data: dict) -> dict:
    """Creates or updates a disease knowledge base entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    local_names_str = json.dumps(disease_data.get("local_names", {}))
    treatments_str = json.dumps(disease_data.get("treatments", []))
    image_urls_str = ",".join(disease_data.get("image_urls", [])) if isinstance(disease_data.get("image_urls"), list) else str(disease_data.get("image_urls", ""))
    
    cursor.execute("""
    INSERT INTO diseases (
        crop, disease_name, scientific_name, local_names, symptoms, 
        treatment_text, treatments, severity_scale, image_urls, source, verified
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(crop, disease_name) DO UPDATE SET
        scientific_name=excluded.scientific_name,
        local_names=excluded.local_names,
        symptoms=excluded.symptoms,
        treatment_text=excluded.treatment_text,
        treatments=excluded.treatments,
        severity_scale=excluded.severity_scale,
        image_urls=excluded.image_urls,
        source=excluded.source,
        verified=excluded.verified,
        updated_at=CURRENT_TIMESTAMP
    """, (
        disease_data.get("crop"), disease_data.get("disease_name"),
        disease_data.get("scientific_name"), local_names_str,
        disease_data.get("symptoms"), disease_data.get("treatment_text"),
        treatments_str, disease_data.get("severity_scale"),
        image_urls_str, disease_data.get("source"),
        1 if disease_data.get("verified") else 0
    ))
    
    conn.commit()
    conn.close()
    return disease_data

# Subsidy Schemes Queries
async def get_all_subsidies() -> List[dict]:
    """Retrieves all active government subsidy schemes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subsidies WHERE active = 1")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["eligible_crops"] = d["eligible_crops"].split(",") if d["eligible_crops"] else []
            d["eligible_inputs"] = d["eligible_inputs"].split(",") if d["eligible_inputs"] else []
            d["documentation"] = d["documentation"].split(",") if d["documentation"] else []
        except Exception:
            pass
        result.append(d)
    return result

async def upsert_subsidy(subsidy_data: dict) -> dict:
    """Inserts or updates a government subsidy scheme."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    eligible_crops_str = ",".join(subsidy_data.get("eligible_crops", [])) if isinstance(subsidy_data.get("eligible_crops"), list) else str(subsidy_data.get("eligible_crops", ""))
    eligible_inputs_str = ",".join(subsidy_data.get("eligible_inputs", [])) if isinstance(subsidy_data.get("eligible_inputs"), list) else str(subsidy_data.get("eligible_inputs", ""))
    documentation_str = ",".join(subsidy_data.get("documentation", [])) if isinstance(subsidy_data.get("documentation"), list) else str(subsidy_data.get("documentation", ""))
    
    if subsidy_data.get("id"):
        cursor.execute("""
        UPDATE subsidies SET
            scheme_name=?, scheme_code=?, level=?, state=?, eligible_crops=?,
            eligible_inputs=?, benefit_type=?, amount_inr=?, income_limit=?,
            application_url=?, documentation=?, active=?, valid_until=?
        WHERE id=?
        """, (
            subsidy_data.get("scheme_name"), subsidy_data.get("scheme_code"),
            subsidy_data.get("level"), subsidy_data.get("state"), eligible_crops_str,
            eligible_inputs_str, subsidy_data.get("benefit_type"), subsidy_data.get("amount_inr"),
            subsidy_data.get("income_limit"), subsidy_data.get("application_url"),
            documentation_str, 1 if subsidy_data.get("active", True) else 0,
            subsidy_data.get("valid_until"), subsidy_data.get("id")
        ))
    else:
        cursor.execute("""
        INSERT INTO subsidies (
            scheme_name, scheme_code, level, state, eligible_crops, eligible_inputs,
            benefit_type, amount_inr, income_limit, application_url, documentation, active, valid_until
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subsidy_data.get("scheme_name"), subsidy_data.get("scheme_code"),
            subsidy_data.get("level"), subsidy_data.get("state"), eligible_crops_str,
            eligible_inputs_str, subsidy_data.get("benefit_type"), subsidy_data.get("amount_inr"),
            subsidy_data.get("income_limit"), subsidy_data.get("application_url"),
            documentation_str, 1 if subsidy_data.get("active", True) else 0,
            subsidy_data.get("valid_until")
        ))
        subsidy_data["id"] = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return subsidy_data
