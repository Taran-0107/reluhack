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

    async def find_official_website(self, company_name: str) -> Optional[str]:
        query = f"{company_name} official website"
        data = await self._search(query)
        if "organic" in data and len(data["organic"]) > 0:
            return data["organic"][0].get("link")
        return None

    async def get_company_info(self, company_name: str) -> Dict[str, str]:
        """
        Uses knowledge graph and search snippets to get phone, address, etc.
        """
        query = f"{company_name} headquarters address phone number"
        data = await self._search(query)
        info = {}
        
        # Check Knowledge Graph
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            if "attributes" in kg:
                for attr, value in kg["attributes"].items():
                    if "address" in attr.lower():
                        info["address"] = value
                    elif "phone" in attr.lower():
                        info["phone_number"] = value
        
        return info

    async def search_external_sources(self, company_name: str, ignore_url: Optional[str]) -> List[str]:
        """
        Searches for third-party information like reviews and pricing,
        returning top external URLs while ignoring the official website.
        """
        queries = [
            f"{company_name} reviews OR overview",
            f"{company_name} pricing OR cost",
            f"{company_name} news OR updates"
        ]
        external_urls = []
        ignore_domain = None
        if ignore_url:
            from urllib.parse import urlparse
            parsed = urlparse(ignore_url)
            ignore_domain = parsed.netloc.replace("www.", "")

        for query in queries:
            data = await self._search(query)
            if "organic" in data:
                for item in data["organic"][:2]: # Get top 2 from each query
                    link = item.get("link", "")
                    if ignore_domain and ignore_domain in link:
                        continue
                    if link and link not in external_urls:
                        external_urls.append(link)
        
        return list(set(external_urls))[:5] # Return max 5 unique external sources

serper_service = SerperService()
