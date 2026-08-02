import asyncio
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Set, Dict

from app.utils.logger import logger
from app.services.extractor_service import extractor_service

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class CrawlerService:
    def __init__(self, max_pages: int = 5, timeout: int = 30):
        self.max_pages = max_pages
        self.timeout = timeout
        self.ignore_paths = ["/login", "/privacy", "/terms", "/legal", "/cookie"]
        self.ignore_domains = ["youtube.com", "youtu.be", "twitter.com", "facebook.com", "instagram.com", "linkedin.com"]
        self.target_keywords = ["about", "product", "service", "solution", "pricing", "contact"]
        self.semaphore = asyncio.Semaphore(2) # Limit to 2 concurrent crawls
        
    def _is_valid_url(self, base_url: str, url: str) -> bool:
        parsed_base = urlparse(base_url)
        parsed_url = urlparse(url)
        
        if parsed_url.scheme not in ["http", "https"]:
            return False
            
        if any(domain in parsed_url.netloc for domain in self.ignore_domains):
            return False

        if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
            return False
        
        lower_path = parsed_url.path.lower()
        if any(ignore in lower_path for ignore in self.ignore_paths):
            return False
            
        return True

    async def _fetch_with_httpx(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text

    def _fetch_with_selenium(self, url: str) -> str:
        if not SELENIUM_AVAILABLE:
            return ""
        
        logger.info(f"Using Selenium fallback for {url}")
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Additional stealth execution
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            
            driver.set_page_load_timeout(self.timeout)
            driver.get(url)
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            logger.error(f"Selenium failed for {url}: {e}")
            return ""

    async def crawl_website(self, base_url: str) -> dict:
        visited: Set[str] = set([base_url])
        consolidated_text = ""
        structured_data = {"json_ld": [], "metadata": {}}
        
        logger.info(f"Crawling homepage {base_url}")
        
        # Crawl homepage first
        text, html = await self._fetch_and_clean(base_url)
        if html:
            sd = extractor_service.extract_structured_data(html)
            structured_data["json_ld"].extend(sd["json_ld"])
            structured_data["metadata"].update(sd["metadata"])
            
        consolidated_text += f"\n--- Content from {base_url} ---\n{text}\n"
        
        # Discover and score links
        scored_links = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            positive_keywords = ["about", "company", "product", "service", "solution", "platform", "technology", "contact", "pricing"]
            negative_keywords = ["login", "privacy", "terms", "careers", "jobs", "blog", "events", "press", "legal"]
            
            for a_tag in soup.find_all("a", href=True):
                link = a_tag["href"]
                full_url = urljoin(base_url, link)
                
                if self._is_valid_url(base_url, full_url) and full_url not in visited:
                    lower_url = full_url.lower()
                    score = 0
                    if any(k in lower_url for k in positive_keywords):
                        score += 1
                    if any(k in lower_url for k in negative_keywords):
                        score -= 1
                        
                    if score >= 0:
                        scored_links.append((score, full_url))
                        visited.add(full_url)
                        
            # Sort by score descending, then take top N
            scored_links.sort(key=lambda x: x[0], reverse=True)
            top_links = [url for score, url in scored_links[:self.max_pages - 1]]
            
            if top_links:
                logger.info(f"Concurrently crawling {len(top_links)} discovered internal pages.")
                tasks = [self._fetch_and_clean(url) for url in top_links]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for url, result in zip(top_links, results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to crawl {url}: {result}")
                    else:
                        page_text, page_html = result
                        consolidated_text += f"\n--- Content from {url} ---\n{page_text}\n"
                        if page_html:
                            sd = extractor_service.extract_structured_data(page_html)
                            structured_data["json_ld"].extend(sd["json_ld"])
                
        return {
            "text": consolidated_text,
            "structured_data": structured_data
        }

    async def crawl_urls_concurrently(self, urls: List[str]) -> str:
        consolidated_text = ""
        tasks = []
        for url in urls:
            tasks.append(self._crawl_single_url(url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"Failed concurrent crawl for {url}: {result}")
            elif result:
                consolidated_text += f"\n--- External Source: {url} ---\n{result}\n"
        
        return consolidated_text

    async def _fetch_and_clean(self, url: str) -> tuple[str, str]:
        async with self.semaphore:
            logger.info(f"Fetching URL {url}")
            text = ""
            html = ""
            try:
                html = await self._fetch_with_httpx(url)
                text = extractor_service.clean_html(html)
            except Exception as e:
                logger.warning(f"HTTPX failed for {url} ({e}). Falling back to Selenium...")
                
            if len(text) < 500 and SELENIUM_AVAILABLE:
                loop = asyncio.get_running_loop()
                html = await loop.run_in_executor(None, self._fetch_with_selenium, url)
                text = extractor_service.clean_html(html)
                
            return text, html

    async def _crawl_single_url(self, url: str) -> str:
        text, _ = await self._fetch_and_clean(url)
        return text

crawler_service = CrawlerService()
