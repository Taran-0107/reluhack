from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from app.schemas.research import ResearchRequest, ResearchResult
from app.services.serper_service import serper_service
from app.services.crawler_service import crawler_service
from app.services.ai_service import ai_service
from app.services.competitor_service import competitor_service
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
    file_path = os.path.join(HISTORY_DIR, f"{result.company_name.lower()}.json")
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

    if not website and company_name:
        website = await serper_service.find_official_website(company_name)
    
    if not company_name and website:
        # Fallback if only URL is given
        company_name = website.split(".")[1].capitalize() if "." in website else "Unknown"

    if not website:
        raise ValueError(f"Could not find an official website for {company_name}")

    import asyncio
    
    # 1. Start crawling the official website
    crawl_task = asyncio.create_task(crawler_service.crawl_website(website))
    
    # 2. Get extra company info (address, phone) from Serper
    company_info_task = asyncio.create_task(serper_service.get_company_info(company_name))
    
    # 3. Find external third-party sources (reviews, pricing, etc.)
    external_urls_task = asyncio.create_task(serper_service.search_external_sources(company_name, website))
    
    # Wait for initial data fetching
    crawled_text, company_info, external_urls = await asyncio.gather(
        crawl_task, company_info_task, external_urls_task
    )
    
    # 4. Concurrently crawl the external third-party sources
    external_text = await crawler_service.crawl_urls_concurrently(external_urls)

    # Consolidate context
    context = f"Additional Info from Google: {company_info}\n\n=== Official Website Content ===\n{crawled_text}\n\n=== External Sources (Reviews, Pricing, News) ===\n{external_text}"

    # Generate summary with AI
    ai_response = await ai_service.generate_company_summary(company_name, context)

    # Add missing data if AI failed to find it
    if not ai_response.get("address"):
        ai_response["address"] = company_info.get("address")
    if not ai_response.get("phone_number"):
        ai_response["phone_number"] = company_info.get("phone_number")
    
    # Ensure competitors exist
    if not ai_response.get("competitors"):
        ai_response["competitors"] = await competitor_service.find_competitors(company_name)
    
    # Enforce website matching
    if not ai_response.get("website") or ai_response["website"] == "null":
        ai_response["website"] = website
        
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
        logger.error(f"Unexpected error in research pipeline: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the research process.")

@router.get("/history")
async def get_history():
    history = []
    if os.path.exists(HISTORY_DIR):
        for filename in os.listdir(HISTORY_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(HISTORY_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    history.append({
                        "company_name": data.get("company_name", filename.replace(".json", "")),
                        "website": data.get("website", ""),
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
