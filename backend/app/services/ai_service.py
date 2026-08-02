import json
import httpx
from typing import Dict, Any
from app.utils.config import settings
from app.utils.logger import logger

class AIService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.openrouter_model = settings.OPENROUTER_MODEL
        self.cohere_api_key = settings.COHERE_API_KEY

    async def generate_company_summary(self, company_name: str, context: str) -> Dict[str, Any]:
        prompt = f"""
You are an expert business analyst. Analyze the following company context and extract information.
You MUST respond with ONLY a valid JSON object matching exactly this schema:

{{
  "company_name": "Name of the company",
  "website": "The official website URL (if found in context)",
  "phone_number": "Phone number (or null if not found)",
  "address": "Headquarters or primary address (or null if not found)",
  "products_services": ["list", "of", "products", "or", "services"],
  "pain_points": ["List of specific CUSTOMER PROBLEMS, FRUSTRATIONS, or NEGATIVE EXPERIENCES that exist BEFORE using this company's product. Do NOT list the company's features or solutions. Write them as negative pain points (e.g., 'Wasting time on manual data entry', 'High costs of legacy systems')."],
  "competitors": [
    {{
      "name": "Competitor Name",
      "website": "Competitor website (or null)",
      "description": "Brief description of how they compete"
    }}
  ],
  "summary": "A brief summary of what the company does"
}}

Here is the context for company '{company_name}':
{context[:25000]}
"""
        if self.provider.lower() == "cohere":
            return await self._call_cohere(prompt)
        else:
            return await self._call_openrouter(prompt)

    async def _call_openrouter(self, prompt: str) -> Dict[str, Any]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Company Research Backend"
        }
        payload = {
            "model": self.openrouter_model,
            "messages": [
                {"role": "system", "content": "You are a helpful business analyst assistant that ONLY outputs valid JSON without markdown wrapping."},
                {"role": "user", "content": prompt}
            ]
        }
        return await self._execute_request(url, headers, payload, is_cohere=False)

    async def _call_cohere(self, prompt: str) -> Dict[str, Any]:
        url = "https://api.cohere.com/v2/chat"
        headers = {
            "Authorization": f"Bearer {self.cohere_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "command-r-plus-08-2024",
            "messages": [
                {"role": "system", "content": "You are a helpful business analyst assistant that ONLY outputs valid JSON without markdown wrapping."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        return await self._execute_request(url, headers, payload, is_cohere=True)

    async def _execute_request(self, url: str, headers: Dict, payload: Dict, is_cohere: bool) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                if is_cohere:
                    # Cohere V2 API response structure
                    content = data.get("message", {}).get("content", [])[0].get("text", "")
                else:
                    # OpenRouter / OpenAI response structure
                    content = data["choices"][0]["message"]["content"]
                
                # Cleanup markdown if LLM misbehaves despite instructions
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:-3]
                elif content.startswith("```"):
                    content = content[3:-3]
                    
                return json.loads(content.strip())
            except httpx.HTTPStatusError as e:
                logger.error(f"AI Provider HTTP Error ({url}): {e.response.text}")
                raise e
            except Exception as e:
                logger.error(f"Error parsing AI response: {e}")
                raise e

ai_service = AIService()
