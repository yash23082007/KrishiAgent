import os
import sys
import asyncio

# Add backend directory to sys.path so we can import modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from orchestrator import PipelineOrchestrator

async def main():
    print("Initializing Pipeline Orchestrator...")
    orchestrator = PipelineOrchestrator()
    
    # Simulate a farmer (Kisan Bhai) from Rajasthan sending a wheat crop image
    # We send coordinates close to Churu, Rajasthan
    phone = "+91-94140-55555" # Will match 'marwari' dialect heuristic
    name = "Ram Singh"
    crop_image = "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&q=80&w=600" # wheat crop image placeholder
    latitude = 27.7011
    longitude = 74.4712
    dialect = "marwari"
    
    print(f"\n--- Triggering Pipeline for {name} ({phone}) ---")
    print(f"Location: {latitude}, {longitude} (Dialect: {dialect})")
    print("Running 4-Agent pipeline in sequence (Vision & Weather in parallel, then Economic, then Voice)...")
    
    try:
        result = await orchestrator.run_pipeline(
            phone_hash=phone,
            phone_prefix=phone[:5],
            image_url=crop_image,
            lat=latitude,
            lon=longitude,
            dialect=dialect,
            farmer_name=name
        )
        
        print("\n=== PIPELINE EXECUTION SUCCESSFUL ===")
        print(f"Case ID: {result['id']}")
        print(f"Total Execution Latency: {result['latency_ms']} ms")
        print(f"Crop Diagnosed: {result['crop']}")
        print(f"Disease Diagnosed: {result['disease']} ({result['scientific_name']})")
        print(f"Severity: {result['severity']} (Confidence: {result['confidence']})")
        print(f"Weather Safe to Spray: {result['weather_safe']} (Reason: {result['weather_reason']})")
        print(f"Spray Window: {result['safe_spray_window']}")
        print(f"Recommended Treatment: {result['treatment_name']} (Dose: {result['treatment_dose']})")
        print(f"Pricing: Retail Rs.{result['treatment_price']} | Subsidy Rs.{result['subsidy_amount']} | Net Cost: Rs.{result['net_cost']}")
        print(f"Government Scheme: {result['subsidy_scheme']}")
        print(f"Nearest Supplier: {result['dealer_name']} ({result['dealer_distance']} km away, Ph: {result['dealer_phone']})")
        print(f"Generated Voice URL: {result['audio_url']}")
        print(f"Translated Voice advisory: {result['translated_text'].encode('utf-8', 'ignore')}")
        print("======================================")
        
    except Exception as e:
        print(f"\nPipeline run failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
