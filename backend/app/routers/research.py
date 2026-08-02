from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from app.schemas.research import ResearchRequest, ResearchResult
from app.services.serper_service import serper_service
from app.services.crawler_service import crawler_service
from app.services.ai_service import ai_service
from app.services.discord_service import discord_service
from app.services.pdf_service import pdf_service
from app.utils.logger import logger

router = APIRouter(prefix="/research", tags=["Research"])

import os
import json
from datetime import datetime

# Setup history directory
HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

def save_research(result: ResearchResult):
    file_path = os.path.join(HISTORY_DIR, f"{result.company_name.value.lower()}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        # Add a timestamp so we can sort history
        data = result.model_dump()
        data["_created_at"] = datetime.now().isoformat()
        json.dump(data, f, indent=4)

def load_research(company_name: str) -> dict | None:
    file_path = os.path.join(HISTORY_DIR, f"{company_name.lower()}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

async def execute_research_pipeline(request: ResearchRequest) -> ResearchResult:
    company_name = request.company_name
    website = request.website_url

    serper_data = {}
    if website:
        # If URL provided, skip Serper
        if not company_name:
            company_name = website.split(".")[1].capitalize() if "." in website else "Unknown"
    else:
        # One single Serper search if only company name is provided
        serper_data = await serper_service.search_company_details(company_name)
        website = serper_data.get("official_website")
        if not website:
            raise ValueError(f"Could not find an official website for {company_name}")

    # 1. Crawl official website
    crawl_results = await crawler_service.crawl_website(website)
    crawled_text = crawl_results["text"]
    structured_data = crawl_results["structured_data"]
    
    # 2. Concurrently crawl external sources (if any found via Serper)
    external_urls = serper_data.get("external_urls", [])
    external_text = ""
    if external_urls:
        external_text = await crawler_service.crawl_urls_concurrently(external_urls)

    # Consolidate context
    context = f"=== Extracted Structured Data (JSON-LD, Meta) ===\n{json.dumps(structured_data, indent=2)}\n\n"
    if serper_data:
        context += f"=== Search Snippets & Knowledge Graph ===\nInfo: {serper_data.get('info')}\nSnippets: {serper_data.get('snippets')}\n\n"
        
    context += f"=== Official Website Content ===\n{crawled_text}\n\n"
    
    if external_text:
        context += f"=== External Sources (Reviews, Pricing, News) ===\n{external_text}\n"

    # Generate summary with AI (including competitors)
    ai_response = await ai_service.generate_company_summary(company_name, context)

    # Enforce website matching if AI missed it
    if not ai_response.get("website") or ai_response["website"].get("value") in [None, "null"]:
        if "website" not in ai_response:
            ai_response["website"] = {}
        ai_response["website"]["value"] = website
        ai_response["website"]["source"] = "System Fallback"
        ai_response["website"]["confidence"] = 1.0
        
    result = ResearchResult(**ai_response)
    
    # Store to local disk
    save_research(result)
    
    return result

@router.post("/", response_model=ResearchResult)
async def start_research(request: ResearchRequest):
    if not request.company_name and not request.website_url:
        raise HTTPException(status_code=400, detail="Must provide company_name or website_url")

    try:
        return await execute_research_pipeline(request)
    except ValueError as e:
        logger.error(f"Validation error in research pipeline: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error in research pipeline: {repr(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An error occurred during the research process.")

from app.utils.logger import logger, log_buffer

@router.get("/logs")
async def get_logs():
    return {"logs": list(log_buffer)}

@router.get("/history")
async def get_history():
    history = []
    if os.path.exists(HISTORY_DIR):
        for filename in os.listdir(HISTORY_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(HISTORY_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    company_data = data.get("company_name")
                    website_data = data.get("website")
                    
                    company_name = company_data.get("value") if isinstance(company_data, dict) else company_data
                    website = website_data.get("value") if isinstance(website_data, dict) else website_data
                    
                    history.append({
                        "company_name": company_name or filename.replace(".json", ""),
                        "website": website or "",
                        "created_at": data.get("_created_at", "")
                    })
    # Sort by newest first
    history.sort(key=lambda x: x["created_at"], reverse=True)
    return history

@router.get("/{company_name}", response_model=ResearchResult)
async def get_research_result(company_name: str):
    data = load_research(company_name)
    if not data:
        raise HTTPException(status_code=404, detail="Company research not found.")
    
    # Remove metadata before validating
    data.pop("_created_at", None)
    return ResearchResult(**data)
