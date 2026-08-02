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
You MUST respond with ONLY a valid JSON object matching exactly this schema. For each field, provide a "value", a "source" indicating where you found it (e.g. "JSON-LD", "Homepage", "Search Snippet", or "Inferred Insights" for pain points), and a "confidence" score (0.0 to 1.0).

{{
  "company_name": {{"value": "Name of the company", "source": "...", "confidence": 1.0}},
  "website": {{"value": "The official website URL (if found in context)", "source": "...", "confidence": 1.0}},
  "phone_number": {{"value": "Phone number (or null if not found)", "source": "...", "confidence": 1.0}},
  "address": {{"value": "Headquarters or primary address (or null if not found)", "source": "...", "confidence": 1.0}},
  "products_services": {{"value": ["list", "of", "products", "or", "services"], "source": "...", "confidence": 1.0}},
  "pain_points": {{"value": ["List of specific CUSTOMER PROBLEMS, FRUSTRATIONS, or NEGATIVE EXPERIENCES that exist BEFORE using this company's product. Do NOT list the company's features or solutions. Write them as negative pain points (e.g., 'Wasting time on manual data entry', 'High costs of legacy systems'). Use industry/products to infer them if needed."], "source": "Inferred Insights", "confidence": 0.8}},
  "competitors": {{"value": [
    {{
      "name": "Competitor Name",
      "website": "Competitor website (or null)",
      "description": "Brief description of how they compete based on provided context"
    }}
  ], "source": "...", "confidence": 0.9}},
  "summary": {{"value": "A brief summary of what the company does", "source": "...", "confidence": 1.0}}
}}

Never hallucinate external information. Base your answers ONLY on the provided context. If something is completely absent, output null for value. Priority for phone/address: 1. JSON-LD, 2. Contact page, 3. Search snippets.

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
        content = ""
        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                if is_cohere:
                    if not data.get("message", {}).get("content"):
                        logger.error(f"Cohere API returned unexpected format: {data}")
                    content = data.get("message", {}).get("content", [{"text": ""}])[0].get("text", "")
                else:
                    if "choices" not in data or not data["choices"]:
                        logger.error(f"OpenRouter/OpenAI API returned unexpected format: {data}")
                    content = data.get("choices", [{"message": {"content": ""}}])[0].get("message", {}).get("content", "")
                
                content = content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                start_idx = content.find("{")
                end_idx = content.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    content = content[start_idx:end_idx+1]
                    
                parsed_json = json.loads(content.strip())
                
                # Graceful fallback: If LLM outputs flat values instead of nested dicts, wrap them automatically
                for key, val in parsed_json.items():
                    if not isinstance(val, dict) or "value" not in val:
                        parsed_json[key] = {
                            "value": val,
                            "source": "AI Fallback Inference",
                            "confidence": 0.5
                        }
                        
                return parsed_json
            except httpx.HTTPStatusError as e:
                logger.error(f"AI Provider HTTP Error ({url}): {e.response.text}")
                raise e
            except Exception as e:
                import traceback
                logger.error(f"Error parsing AI response: {repr(e)}. Raw content: {content}\n{traceback.format_exc()}")
                raise e

ai_service = AIService()
