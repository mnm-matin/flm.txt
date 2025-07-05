"""
The main orchestrator class that ties everything together.
This is the primary public-facing class for the library.
"""
import time
import logging

from .crawler import WebCrawler
from .enhancer import AIEnhancer
from .formatter import TextFormatter, JsonFormatter, YamlFormatter, BaseFormatter

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMSGenerator:
    """
    Orchestrates the process of crawling, enhancing, and formatting website content.
    """
    def __init__(self):
        self.crawler = WebCrawler()
        self.enhancer = AIEnhancer()
        self.formatters = {
            "text": TextFormatter(),
            "json": JsonFormatter(),
            "yaml": YamlFormatter(),
        }

    async def run(
        self,
        url: str,
        strategy: str = "systematic",
        output_format: str = "text",
        max_pages: int = 50
    ):
        """
        Executes the full pipeline: crawl, enhance, and write output.

        Args:
            url: The base URL of the website to process.
            strategy: The crawl strategy to use ('systematic', 'comprehensive', 'sitemap').
            output_format: The desired output format ('text', 'json', 'yaml').
            max_pages: The maximum number of pages to process.
        """
        start_time = time.time()
        logger.info(f"Starting generation for {url}...")

        # 1. Crawl the website
        pages = await self.crawler.crawl(url, strategy, max_pages)
        if not pages:
            logger.warning("No pages were found during the crawl. Exiting.")
            return

        # 2. Enhance pages with AI descriptions (OpenAI only)
        enhanced_pages = await self.enhancer.enhance_pages(pages)

        # 3. Format and write the output
        formatter = self.formatters.get(output_format)
        if not formatter:
            logger.error(f"Unknown output format '{output_format}'. Defaulting to 'text'.")
            formatter = self.formatters["text"]
        
        metadata = {
            "base_url": url,
            "crawl_strategy": strategy,
            "ai_provider": "openai",
            "page_count": len(enhanced_pages),
            "site_name": formatter._get_domain(url)
        }
        formatter.write(enhanced_pages, metadata)
        
        duration = time.time() - start_time
        logger.info(f"🎉 Generation complete for {url} in {duration:.2f} seconds.")
