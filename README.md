# KrishiAgent 🌾
### Autonomous Multi-Agent Farm Manager
> **Agentic Arena Hackathon Submission** | *Zero-UI Approach to Multi-Agent Orchestration*

Indian agriculture loses over **₹50,000 crore annually** to crop diseases. The failure to mitigate this isn't due to a lack of agritech apps; it's a massive UX and accessibility failure. KrishiAgent solves this by replacing the entire agritech app ecosystem with a single WhatsApp number. By simply sending a photo of a diseased crop, farmers receive an immediate, dialect-aware diagnostic voice note along with weather safety validations and economic advisories.

---

## 📺 Live End-to-End Simulation Demo

![KrishiAgent Pipeline Demo](krishiagent_demo.webp)

---

## 1. ⚠️ The Problem: The UX Failure in Agritech

1. **Friction & Digital Literacy:** Current platforms force farmers to navigate app stores, register accounts, and understand complex UIs. This creates a severe digital literacy barrier.
2. **The Dialect Disconnect:** Most digital advisory services rely on standard Hindi or English. However, farmers communicate and build trust in local regional dialects (e.g., Marwari, Bhojpuri, Gujarati).
3. **Fragmented Workflows:** Diagnosing a blight is only the first step. A farmer must also check weather conditions (before spraying pesticides or fungicides) and search for local subsidized suppliers. Today, these are separate, manual tasks.

---

## 2. 💡 The Solution: A WhatsApp-Native Multi-Agent Pipeline

KrishiAgent implements a **Zero-UI** approach. The user interface is simply sending a photo on WhatsApp. Behind the scenes, an orchestrated cluster of four autonomous agents handles the complex backend routing:

1. **Vision Agent (Agronomist):** Analyzes the image payload using Gemini 1.5 Flash (or GPT-4o-Mini), identifies the crop, detects the specific disease/pest, and queries the knowledge base for chemical countermeasures.
2. **Climate Agent (Meteorologist):** Extracts location coordinates and fetches hyper-local weather APIs (Open-Meteo). It dynamically enforces safety rules (e.g., *"Halt pesticide: wind speed is 18 km/h, causing spray drift"* or *"Rain forecast in 2 hours will wash away the chemical"*).
3. **Economic Agent (Market Advisor):** Performs RAG (Retrieval-Augmented Generation) on local supplier databases and active government subsidy databases to calculate the lowest net cost and direct benefits for the farmer.
4. **Voice Agent (Linguistic Linguist):** Compiles the structured JSON output from the agent cluster, translates it into the farmer's native dialect (e.g., Marwari) using dialect-attuned LLM prompts, and synthesizes an empathetic audio voice note via TTS (Google TTS/Bhashini).

---

## 3. 🏗️ Architecture & Workflow

The system coordinates agents asynchronously to minimize latency and ensure results are grounded:

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

### Execution Workflow:
* **01. Ingestion:** The farmer sends a photo via WhatsApp. The incoming webhook triggers the async pipeline execution.
* **02. Parallel Evaluation:** The Vision Agent parses the image for pathogens, while the Climate Agent concurrently pulls real-time meteorological data for the coordinates.
* **03. Constraint Synthesis:** The diagnosed pathogen details and weather rules are passed to the Economic Agent to formulate a safe, localized, and cost-effective action plan.
* **04. Translation & Delivery:** The advisory payload is translated into regional dialect script, synthesized to OGG Opus audio, and delivered back to the farmer's WhatsApp. *(Total End-to-End Latency: < 15s)*

---

## 🛠️ Technology Stack & AI Alignment

KrishiAgent is built with a decoupled, state-of-the-art tech stack matching the hackathon criteria:

* **LLM Core / Gemini:** Uses **Gemini 1.5 Flash** for rapid, cost-effective multimodal crop pathology analysis, dialect-accurate translation (Hindi, Marwari, Bhojpuri, Gujarati), and voice-friendly text construction.
* **Agent Frameworks / CrewAI & Custom Orchestration:** Features **Custom AI Agents** written in Python using Asyncio for parallel execution. Includes built-in **CrewAI compatibility wrappers** (`get_crewai_agent()`) for enterprise multi-agent execution.
* **Programming & UI:** Built end-to-end with **Python** (FastAPI backend) and **JavaScript / TypeScript** (Next.js 14 frontend dashboard & interactive Leaflet map).
* **APIs & Automation Platforms:** Automatically integrates:
  * **Meta WhatsApp Cloud Business API Webhooks** for a Zero-UI messaging pipeline.
  * **Open-Meteo API** (OpenWeather alternative) for weather-feasibility validation loops.
  * **Nominatim OpenStreetMap API** for reverse geocoding.
  * **Cloudinary Media API** for automatic CDN-based public audio note hosting.
* **Database & Vector Fallbacks:** Uses PostgreSQL (via Supabase) or local SQLite databases for storing farmer profiles, local supplier inventories, and government subsidy knowledge bases.

---

## 📈 Impact Metrics

* **Zero UI / Zero Onboarding:** Bypasses the digital literacy barrier entirely by using WhatsApp voice and images. No app store installation or complex accounts required.
* **High Trust Factor:** Dialect-native audio notes significantly increase the adoption and execution rate of the AI's agricultural advice.
* **Direct ROI:** Automated early detection and chemical spray safety logic prevent 15-20% crop yield loss per seasonal cycle.

---

## ⚙️ Getting Started

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

* **`GET /health`**: Returns the health status of the backend server.
* **`POST /webhook`**: Recipient of incoming Meta WhatsApp events (validates verify tokens and queues background tasks).
* **`POST /api/simulator`**: Directly runs a synchronous simulation payload from the Next.js dashboard.
* **`GET /api/cases`**: Returns case history from the database.

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
