from typing import List, Dict
from app.services.serper_service import serper_service
from app.utils.logger import logger

class CompetitorService:
    async def find_competitors(self, company_name: str) -> List[Dict]:
        """
        Uses Serper to find competitors if the AI did not generate enough.
        """
        query = f"top competitors of {company_name}"
        try:
            data = await serper_service._search(query)
            competitors = []
            if "organic" in data:
                for item in data["organic"][:3]:
                    competitors.append({
                        "name": item.get("title", "").split("-")[0].strip(),
                        "website": item.get("link"),
                        "description": item.get("snippet")
                    })
            return competitors
        except Exception as e:
            logger.error(f"Error finding competitors for {company_name}: {e}")
            return []

competitor_service = CompetitorService()
