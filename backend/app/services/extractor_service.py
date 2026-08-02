from bs4 import BeautifulSoup
import re

class ExtractorService:
    def __init__(self):
        pass

    def clean_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove scripts, styles, header, footer, nav
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            element.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

extractor_service = ExtractorService()
