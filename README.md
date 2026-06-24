# KrishiAgent 🌾
### A WhatsApp-Native, Multi-Agent Crop Pathology & Agricultural Advisory Pipeline

KrishiAgent is an autonomous agricultural diagnostic system designed for Indian farmers. By providing a "Zero UI" interface, farmers can simply take a photo of a diseased crop and send it over WhatsApp. In return, they receive an immediate, dialect-aware diagnostic voice note detailing the disease, spray feasibility based on real-time local weather, and a net-cost economic advisory featuring local dealer locations and active government subsidies.

## 📺 Live End-to-End Simulation Demo

![KrishiAgent Pipeline Demo](krishiagent_demo.webp)

---

## 🏗️ Architecture & Agent Pipeline

The core system is powered by FastAPI and orchestrates four specialized agents to process queries in a fast, concurrent pipeline:

```mermaid
graph TD
    Farmer[Farmer on WhatsApp] -->|Sends image / location| Webhook[FastAPI Webhook /webhook]
    
    subgraph Parallel Stage
        Webhook -->|Image URL| VisionAgent[Vision Agent: Pathologist]
        Webhook -->|Lat, Lon| ClimateAgent[Climate Agent: Meteorologist]
    end
    
    VisionAgent -->|Disease & treatment keywords| EconAgent[Economic Agent: Market Advisor]
    ClimateAgent -->|Weather safety check| EconAgent
    
    EconAgent -->|Net cost & dealer info| VoiceAgent[Voice Agent: Linguist]
    
    VoiceAgent -->|TTS Generation .ogg| AudioUpload[Audio Upload Cloudinary/Local]
    AudioUpload -->|Public URL| WhatsAppAPI[Meta WhatsApp API]
    
    WhatsAppAPI -->|Voice Note & Text Advisory| Farmer
    Webhook -->|Saves telemetry| DB[(SQLite / Supabase DB)]
    DB -->|Polled updates| Dash[Next.js Dashboard Feed]
```

### The 4 Autonomous Agents:
1. **Vision Agent (Crop Pathologist):** Leverages `gemini-1.5-flash` to identify crop type, pathogen, severity level, affected area percentage, and active ingredients needed for treatment.
2. **Climate Agent (Meteorologist):** Interacts with the Open-Meteo API to check wind speed, rain, and humidity. It determines if it is safe to spray chemicals (e.g., wind $< 15\text{ km/h}$ to prevent drift, no immediate rain to prevent runoff) and flags fungal-favorable humidity levels.
3. **Economic Agent (Market Advisor):** Queries the local database (SQLite/Supabase) to cross-reference required chemicals with government subsidies (such as PM-Pranam or state schemes) and maps the closest agricultural dealer listings to estimate net cost and travel distance.
4. **Voice Agent (Agri-Linguist):** Renders the synthesized advisory, translates it into local dialects (like Marwari, Gujarati, or Bhojpuri) using dialect-attuned LLM prompts, and outputs Hindi-friendly audio notes using gTTS or Bhashini.

---

## 🛠️ Technology Stack & AI Alignment

KrishiAgent is built with a decoupled, state-of-the-art tech stack matching the criteria:

* **LLM Core / Gemini:** Uses **Gemini 1.5 Flash** for rapid, cost-effective multimodal crop pathology analysis, dialect-accurate translation (Hindi, Marwari, Bhojpuri, Gujarati), and voice-friendly text construction.
* **Agent Frameworks / CrewAI & Custom Orchestration:** Features **Custom AI Agents** written in Python using Asyncio for parallel execution of diagnostic and environmental pipelines. Includes built-in **CrewAI compatibility wrappers** (`get_crewai_agent()`) for enterprise multi-agent execution.
* **Programming & UI:** Built end-to-end with **Python** (FastAPI backend) and **JavaScript / TypeScript** (Next.js 14 frontend dashboard & interactive map).
* **APIs & Automation Platforms:** Automatically integrates:
  * **Meta WhatsApp Cloud Business API Webhooks** for a Zero-UI messaging pipeline.
  * **Open-Meteo API** for weather-feasibility validation loops.
  * **Nominatim OpenStreetMap API** for reverse geocoding.
  * **Cloudinary Media API** for automatic CDN-based public audio note hosting.
* **Database & Vector Fallbacks:** Uses PostgreSQL (via Supabase) or local SQLite databases for storing farmer profiles, local supplier inventories, and government subsidy knowledge bases.

---

## 🚀 Getting Started

### 1. Pre-requisites & Environment Setup
Create a `.env` file in the root directory:

```env
# Google Gemini Credentials (required for vision analysis & translation)
GEMINI_API_KEY=your_gemini_api_key

# Supabase (optional, defaults to local SQLite db 'local.db')
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Audio Hosting (optional, required for sending real voice notes to Meta WhatsApp API)
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Meta WhatsApp Cloud API (optional, falls back to local CLI mock logs)
WHATSAPP_TOKEN=your_meta_access_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=krishi_verify_token
```

### 2. Backend Setup & Run
Create a virtual environment, install dependencies, seed the database, and start the FastAPI server:

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# Install requirements
pip install -r backend/requirements.txt

# Seed the local SQLite database with default crops, schemes, and dealers
python scripts/seed_knowledge_base.py

# Test the multi-agent pipeline standalone in your console
python scripts/test_pipeline_local.py

# Run the FastAPI server
python backend/main.py
```
The FastAPI documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup & Run
Install npm modules and start the development server:

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to interact with the dashboard and WhatsApp Sandbox simulator.

---

## 🔌 API Endpoints Reference

### `GET /health`
Returns the status of the backend service.

### `POST /webhook`
Handles verification requests and incoming message payloads from Meta's WhatsApp Webhooks.
* **Verification (GET):** Verifies the subscription using `hub.verify_token` matching `WHATSAPP_VERIFY_TOKEN`.
* **Incoming Payloads (POST):** Parses incoming image and location messages, executing the agent loop asynchronously.

### `POST /api/simulator`
Simulates a WhatsApp pipeline run directly from the frontend dashboard.
* **Payload:**
  ```json
  {
    "phone": "+91-94140-55555",
    "name": "Ram Singh",
    "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b",
    "latitude": 27.7011,
    "longitude": 74.4712,
    "dialect": "marwari"
  }
  ```
* **Response:** Returns the structured database record of the generated diagnosis, including vision analysis, climate telemetry, economic net costs, and voice note URLs.

### `GET /api/cases`
Retrieves a history of agricultural diagnosis cases logged in the database.

---

## 🎯 Production Webhook & WhatsApp Live Setup

To connect KrishiAgent to a live phone number:

1. **Expose the Server:** Deploy your FastAPI backend to a hosting provider or expose it locally using an HTTPS tunnel:
   ```bash
   ngrok http 8000
   ```
2. **Configure Meta Webhooks:** 
   * Navigate to the **Meta Developer Portal** → Your App → **WhatsApp** → **Configuration**.
   * Under **Webhooks**, set the Callback URL to `https://<your-public-url>/webhook` and enter your verify token.
   * Subscribe to **`messages`** under Webhook Fields.
3. **Register Live Credentials:** Populate `WHATSAPP_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` in your environment variables. 
4. **Test:** Text a picture of a crop disease to your registered WhatsApp business number and receive the diagnosis directly on your phone!
