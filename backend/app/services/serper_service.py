import httpx
from typing import Dict, Any, List, Optional
from app.utils.config import settings
from app.utils.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

class SerperService:
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    async def _search(self, query: str) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("Serper API key not configured. Skipping search.")
            return {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json={"q": query, "num": 5}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error during Serper search for '{query}': {e}")
            return {}

    async def search_company_details(self, company_name: str) -> Dict[str, Any]:
        """
        Performs ONE search to get website, knowledge graph info, search snippets, and external urls.
        """
        query = f"{company_name}"
        data = await self._search(query)
        
        result = {
            "official_website": None,
            "info": {},
            "snippets": [],
            "external_urls": []
        }
        
        # 1. Try to get website from Knowledge Graph first
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            if "website" in kg:
                result["official_website"] = kg["website"]
            if "website" in kg.get("attributes", {}):
                result["official_website"] = kg["attributes"]["website"]
        
        # 2. Extract organic results
        if "organic" in data and len(data["organic"]) > 0:
            # If no KG website, find the first non-social/review link
            if not result["official_website"]:
                ignore_domains = ['wikipedia.org', 'facebook.com', 'linkedin.com', 'twitter.com', 'trustpilot.com', 'g2.com', 'capterra.com', 'bloomberg.com', 'youtube.com', 'instagram.com', 'yelp.com', 'edmunds.com']
                for item in data["organic"]:
                    link = item.get("link", "")
                    if any(domain in link.lower() for domain in ignore_domains):
                        continue
                    result["official_website"] = link
                    break
                
                # If still none, fallback to the very first link
                if not result["official_website"]:
                    result["official_website"] = data["organic"][0].get("link")
            
            # Use other organic links as external URLs
            ignore_domain = None
            if result["official_website"]:
                from urllib.parse import urlparse
                parsed = urlparse(result["official_website"])
                ignore_domain = parsed.netloc.replace("www.", "")
                
            for item in data["organic"]:
                link = item.get("link", "")
                snippet = item.get("snippet", "")
                if snippet:
                    result["snippets"].append(f"{item.get('title')}: {snippet}")
                    
                if link and ignore_domain and ignore_domain not in link:
                    if link not in result["external_urls"]:
                        result["external_urls"].append(link)
                        
            result["external_urls"] = result["external_urls"][:5]
            
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            if "attributes" in kg:
                for attr, value in kg["attributes"].items():
                    if "address" in attr.lower():
                        result["info"]["address"] = value
                    elif "phone" in attr.lower():
                        result["info"]["phone_number"] = value
                        
        return result

serper_service = SerperService()
