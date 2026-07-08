import os
import json
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal

from langchain_groq import ChatGroq
from composio import Composio
from composio_langchain import LangchainProvider

load_dotenv()

# =====================================================================
# 1. ADVANCED PRODUCT STRATEGY EVALUATION SCHEMA
# =====================================================================
class AdvancedAppResearchSchema(BaseModel):
    category: str = Field(description="One line describing the category and what the app does.")
    auth_method: Literal["OAuth2", "API key", "Basic", "token", "other"]
    gated_status: Literal["self-serve", "gated"]
    api_surface: Literal["REST", "GraphQL", "gRPC", "Mixed", "None"] = Field(description="Primary API architectural style style.")
    has_mcp_server: Literal["Yes", "No", "Community-built"] = Field(description="Is there an existing Model Context Protocol (MCP) server for this?")
    
    # 🔥 Premium metrics to find clusters & patterns for Product Ops
    developer_friction: Literal["Low", "Medium", "High"] = Field(description="Low = Instant access/clear docs. Medium = Paid plan needed. High = Sales/Partnership gate.")
    target_priority: Literal["P0 (Quick Win)", "P1 (High Value)", "P2 (Strategic Outreach)"] = Field(description="P0 = Self-serve OAuth/API key with public docs. P1 = Popular but requires paid tier. P2 = Gated behind sales/partnerships.")
    
    verdict: str = Field(description="Could this be an agent toolkit today? Define main blocker if not.")
    evidence_url: str = Field(description="Direct URL to the documentation page used.")

# =====================================================================
# 2. RUNTIME BATCH ENGINE
# =====================================================================
def process_batch_pipeline():
    with open("data/apps.json", "r") as f:
        apps = json.load(f)
        
    print(f"📦 Loaded {len(apps)} apps for strategic processing.")
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=LangchainProvider())
    tools = composio.tools.get(user_id="default", toolkits=["TAVILY"])
    llm_with_tools = llm.bind_tools(tools)
    structured_extractor = llm.with_structured_output(AdvancedAppResearchSchema)
    
    final_results = []
    
    for idx, app in enumerate(apps, 1):
        app_name = app["name"]
        app_url = app["hint"]
        cat_group = app["category_group"]
        
        print(f"\n[{idx}/{len(apps)}] 🚀 Strategically Researching: {app_name}...")
        
        try:
            # Pass 1: Deep Context Gathering via Composio
            research_prompt = (
                f"Search for official developer documentation, API architecture (REST/GraphQL), MCP server status, "
                f"authentication methods, and developer account restrictions for '{app_name}' (website: {app_url})."
            )
            search_context = llm_with_tools.invoke(research_prompt)
            
            # Pass 2: Map to Advanced Schema
            extraction_prompt = f"Review these raw research text profiles for {app_name}:\n{search_context.content}\n\nTransform into structure."
            structured_data = structured_extractor.invoke(extraction_prompt)
            
            # Fixed the Pydantic warning by using model_dump() instead of dict()
            row_record = structured_data.model_dump()
            row_record["app_name"] = app_name
            row_record["category_group"] = cat_group
            final_results.append(row_record)
            
            time.sleep(1) # Stay clear of rate limits safely
            
        except Exception as e:
            print(f"⚠️ Error running {app_name}: {e}")
            final_results.append({
                "app_name": app_name,
                "category_group": cat_group,
                "category": f"API service for {app_name}",
                "auth_method": "other",
                "gated_status": "gated",
                "api_surface": "REST",
                "has_mcp_server": "No",
                "developer_friction": "High",
                "target_priority": "P2 (Strategic Outreach)",
                "verdict": "Pipeline timeout or extraction error",
                "evidence_url": app_url
            })
            
        # Save checkpoints incrementally every 5 steps
        if idx % 5 == 0:
            with open("data/raw_results.json", "w") as out_f:
                json.dump(final_results, out_f, indent=4)
            print("💾 Checkpoint saved cleanly.")

    with open("data/raw_results.json", "w") as out_f:
        json.dump(final_results, out_f, indent=4)
    print("\n✅ Batch Processing Complete! Advanced data metrics written to data/raw_results.json")

if __name__ == "__main__":
    process_batch_pipeline()