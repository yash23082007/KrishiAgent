import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import webhook
from db.queries import (
    get_all_cases, get_case, get_all_diseases, 
    upsert_disease, get_all_subsidies, upsert_subsidy
)

app = FastAPI(title="KrishiAgent — Core Backend Server")

# Configure CORS so Next.js dashboard can interact with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Vercel dashboard domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local media directory for served images/audio in local mock mode
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "audio"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount webhooks and simulator routes
app.include_router(webhook.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "krishiagent-backend"}

# CASES ENDPOINTS
@app.get("/api/cases")
async def fetch_cases(limit: int = 50):
    try:
        cases = await get_all_cases(limit)
        return cases
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/{case_id}")
async def fetch_case_by_id(case_id: str):
    try:
        case_data = await get_case(case_id)
        if not case_data:
            raise HTTPException(status_code=404, detail="Case not found")
        return case_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# KNOWLEDGE BASE: DISEASES
@app.get("/api/diseases")
async def fetch_diseases():
    try:
        diseases = await get_all_diseases()
        return diseases
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/diseases")
async def save_disease_entry(disease: dict):
    try:
        saved = await upsert_disease(disease)
        return {"status": "success", "data": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# KNOWLEDGE BASE: SUBSIDIES
@app.get("/api/subsidies")
async def fetch_subsidies():
    try:
        subsidies = await get_all_subsidies()
        return subsidies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/subsidies")
async def save_subsidy_entry(subsidy: dict):
    try:
        saved = await upsert_subsidy(subsidy)
        return {"status": "success", "data": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
