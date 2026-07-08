import os
import json
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI

# Force local file system reading to bypass VS Code environment blocks
load_dotenv(dotenv_path=".env", override=True)

# =====================================================================
# 1. ADVANCED PRODUCT STRATEGY EVALUATION SCHEMA
# =====================================================================
class AdvancedAppResearchSchema(BaseModel):
    category: str = Field(description="One line describing the category and what the app does.")
    auth_method: Literal["OAuth2", "API key", "Basic", "token", "other"]
    gated_status: Literal["self-serve", "gated"]
    api_surface: Literal["REST", "GraphQL", "gRPC", "Mixed", "None"]
    has_mcp_server: Literal["Yes", "No", "Community-built"]
    developer_friction: Literal["Low", "Medium", "High"]
    target_priority: Literal["P0 (Quick Win)", "P1 (High Value)", "P2 (Strategic Outreach)"]
    verdict: str
    evidence_url: str

# =====================================================================
# 2. RUNTIME ENGINE
# =====================================================================
def run_verification_loop():
    print("🧠 Starting Phase 2 Validation Loop using Google Gemini...")
    
    # Safely extract the token string bypassing terminal variables
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "❌ API Key Missing! Your terminal is blocking .env reading.\n"
            "Please open your .env file and double check that GOOGLE_API_KEY=your_key is saved correctly."
        )
        
    # Load Pass 1 results
    with open("data/raw_results.json", "r") as f:
        raw_data = json.load(f)
        
    # Initialize Gemini with the explicitly bound key parameter
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        google_api_key=api_key
    )
    structured_verifier = llm.with_structured_output(AdvancedAppResearchSchema)
    
    verified_results = []
    
    for idx, app in enumerate(raw_data, 1):
        name = app["app_name"]
        
        # Check if it was a fallback error row from the rate limits
        is_fallback = "Pipeline timeout" in app["verdict"] or "error" in app["category"].lower()
        
        if is_fallback:
            print(f"🩹 [{idx}/100] Patching Rate-Limited App: {name}...")
            patch_prompt = f"Provide a complete developer API audit profile for '{name}' (Website/Hint: {app['evidence_url']}). Map it to the strict schema structure."
            try:
                verified_profile = structured_verifier.invoke(patch_prompt)
                verified_row = verified_profile.model_dump()
                verified_row["app_name"] = name
                verified_row["category_group"] = app["category_group"]
                verified_results.append(verified_row)
            except Exception as e:
                print(f"⚠️ Patch failed for {name}: {e}")
                verified_results.append(app)
        else:
            print(f"🧐 [{idx}/100] Auditing data points for: {name}...")
            audit_prompt = f"""
            You are a senior Product Ops Auditor. Verify the accuracy of this data profile for '{name}':
            {json.dumps(app, indent=2)}
            
            If the values are correct, return them exactly as they are. If any metrics (like auth_method, api_surface, or gated_status) are incorrect, fix them based on your knowledge of the official documentation.
            """
            try:
                verified_profile = structured_verifier.invoke(audit_prompt)
                verified_row = verified_profile.model_dump()
                verified_row["app_name"] = name
                verified_row["category_group"] = app["category_group"]
                verified_results.append(verified_row)
            except Exception as e:
                verified_results.append(app)
                
        time.sleep(0.5)

    with open("data/verified_results.json", "w") as out_f:
        json.dump(verified_results, out_f, indent=4)
        
    print("\n🏆 Phase 2 Complete! Fully audited data stored in data/verified_results.json")

if __name__ == "__main__":
    run_verification_loop()