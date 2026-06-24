import os
import sys
import json
import asyncio

# Add backend directory to sys.path so we can import modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from db.queries import upsert_disease, upsert_subsidy

async def seed():
    print("Starting database seeding...")
    
    # 1. Seed Diseases
    diseases_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "backend", "knowledge_base", "crop_diseases.json"
    )
    if os.path.exists(diseases_file):
        with open(diseases_file, "r", encoding="utf-8") as f:
            diseases = json.load(f)
            for d in diseases:
                await upsert_disease(d)
                print(f"Seeded disease: {d['crop']} - {d['disease_name']}")
    else:
        print("crop_diseases.json not found!")

    # 2. Seed Subsidies
    subsidies_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "backend", "knowledge_base", "subsidy_schemes.json"
    )
    if os.path.exists(subsidies_file):
        with open(subsidies_file, "r", encoding="utf-8") as f:
            subsidies = json.load(f)
            for s in subsidies:
                await upsert_subsidy(s)
                print(f"Seeded subsidy: {s['scheme_name']}")
    else:
        print("subsidy_schemes.json not found!")

    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
