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

    async def crawl_website(self, base_url: str) -> str:
        visited: Set[str] = set()
        to_visit: List[str] = [base_url]
        consolidated_text = ""
        
        while to_visit and len(visited) < self.max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
                
            visited.add(url)
            logger.info(f"Crawling {url}")
            
            try:
                text = ""
                html = ""
                try:
                    html = await self._fetch_with_httpx(url)
                    text = extractor_service.clean_html(html)
                except Exception as e:
                    logger.warning(f"HTTPX failed for {url} ({e}). Falling back to Selenium...")
                
                if len(text) < 500 and SELENIUM_AVAILABLE:
                    # Fallback
                    loop = asyncio.get_running_loop()
                    html = await loop.run_in_executor(None, self._fetch_with_selenium, url)
                    text = extractor_service.clean_html(html)
                
                consolidated_text += f"\n--- Content from {url} ---\n{text}\n"
                
                # Extract links if we need more pages
                if len(visited) < self.max_pages and html:
                    soup = BeautifulSoup(html, "html.parser")
                    for a_tag in soup.find_all("a", href=True):
                        link = a_tag["href"]
                        full_url = urljoin(base_url, link)
                        
                        # Prioritize target keywords
                        if self._is_valid_url(base_url, full_url) and full_url not in visited:
                            lower_url = full_url.lower()
                            if any(k in lower_url for k in self.target_keywords):
                                if full_url not in to_visit:
                                    to_visit.insert(0, full_url) # Priority queue
                            else:
                                if full_url not in to_visit:
                                    to_visit.append(full_url)
                                    
            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                
        return consolidated_text

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

    async def _crawl_single_url(self, url: str) -> str:
        async with self.semaphore:
            logger.info(f"Crawling external URL {url}")
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
                
            return text

crawler_service = CrawlerService()
