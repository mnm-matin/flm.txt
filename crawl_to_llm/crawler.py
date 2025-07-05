"""
A clean, focused wrapper around the web crawling logic.
This module abstracts the underlying crawl4ai library.
"""
import logging
import urllib.parse
from typing import List
from .data_models import Page

# Set up a logger for this module
logger = logging.getLogger(__name__)

class WebCrawler:
    """
    Crawls a website using various strategies and returns structured page data.
    """
    async def crawl(self, base_url: str, strategy: str = 'systematic', max_pages: int = 50) -> List[Page]:
        """
        The main public method to start a crawl.

        Args:
            base_url: The starting URL to crawl.
            strategy: The crawling strategy ('systematic', 'comprehensive', 'sitemap').
            max_pages: The maximum number of pages to retrieve.

        Returns:
            A list of Page objects.
        """
        logger.info(f"Starting crawl for '{base_url}' with strategy '{strategy}' (max_pages: {max_pages})")
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        except ImportError:
            logger.error("crawl4ai is not installed. Please run: pip install 'crawl4ai[all]'")
            return []

        if strategy == "sitemap":
            return await self._crawl_from_sitemap(base_url, max_pages)
        else:
            return await self._crawl_website(base_url, strategy, max_pages)

    async def _crawl_website(self, base_url: str, strategy: str, max_pages: int) -> List[Page]:
        """Performs a systematic or comprehensive crawl."""
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
            from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
            from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
            import urllib.parse

            base_domain = urllib.parse.urlparse(base_url).netloc
            is_comprehensive = strategy == 'comprehensive'

            deep_crawl_strategy = BestFirstCrawlingStrategy(
                max_depth=6 if is_comprehensive else 2,
                max_pages=max_pages * 2,  # Discover more pages than the target
                include_external=False
            )

            config = CrawlerRunConfig(
                deep_crawl_strategy=deep_crawl_strategy,
                scraping_strategy=LXMLWebScrapingStrategy(),
                word_count_threshold=50,
                page_timeout=30000
            )

            results = await AsyncWebCrawler().arun(url=base_url, config=config)
            
            # Ensure results are always in a list
            if not isinstance(results, list):
                results = [results] if results else []

            crawled_pages = self._process_crawl_results(results)
            return crawled_pages[:max_pages]

        except Exception as e:
            logger.error(f"An error occurred during website crawl: {e}", exc_info=True)
            return []

    async def _crawl_from_sitemap(self, base_url: str, max_pages: int) -> List[Page]:
        """Crawls a website using its sitemap."""
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
            from crawl4ai import SitemapCrawlingStrategy
            from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

            config = CrawlerRunConfig(
                scraping_strategy=LXMLWebScrapingStrategy(),
                word_count_threshold=50,
                page_timeout=15000,
                deep_crawl_strategy=SitemapCrawlingStrategy(
                    max_pages=max_pages
                )
            )

            results = await AsyncWebCrawler().arun(url=base_url, config=config)
            
            if not isinstance(results, list):
                results = [results] if results else []
            
            crawled_pages = self._process_crawl_results(results)
            return crawled_pages[:max_pages]

        except Exception as e:
            logger.error(f"An error occurred during sitemap crawl: {e}", exc_info=True)
            return []

    def _process_crawl_results(self, results: list) -> List[Page]:
        """Converts raw crawl4ai results into a list of Page objects."""
        pages = []
        for result in results:
            if result and result.success:
                content = ""
                if hasattr(result, 'markdown') and result.markdown:
                    content = result.markdown.raw_markdown or ""
                elif hasattr(result, 'cleaned_html') and result.cleaned_html:
                    content = result.cleaned_html

                word_count = len(content.split())
                if word_count > 0:
                    pages.append(Page(
                        url=result.url,
                        title=result.metadata.get('title', 'Untitled'),
                        content=content,
                        word_count=word_count,
                        metadata=result.metadata or {}
                    ))
        return pages
