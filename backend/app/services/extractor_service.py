from bs4 import BeautifulSoup
import re
import json

class ExtractorService:
    def __init__(self):
        pass

    def clean_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove scripts, styles, header, footer, nav
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]):
            element.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
        
    def extract_structured_data(self, html_content: str) -> dict:
        soup = BeautifulSoup(html_content, "html.parser")
        structured_data = {
            "json_ld": [],
            "metadata": {}
        }
        
        # Extract JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    structured_data["json_ld"].extend(data)
                else:
                    structured_data["json_ld"].append(data)
            except Exception:
                pass
                
        # Extract Metadata
        if soup.title:
            structured_data["metadata"]["title"] = soup.title.string
        
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            structured_data["metadata"]["description"] = meta_desc.get("content")
            
        return structured_data

extractor_service = ExtractorService()
