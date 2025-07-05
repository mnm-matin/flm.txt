"""
Handles the AI-based description generation ("enhancing" the crawled data) using OpenAI.
"""
import asyncio
import logging
from typing import List, Optional
from .data_models import Page
import os

logger = logging.getLogger(__name__)

class AIEnhancer:
    """
    Takes a list of Page objects and populates their description field using OpenAI.
    """

    async def enhance_pages(self, pages: List[Page]) -> List[Page]:
        """
        Processes a list of pages in parallel to generate descriptions using OpenAI.

        Args:
            pages: The list of Page objects to enhance.

        Returns:
            The list of Page objects with descriptions populated.
        """
        semaphore = asyncio.Semaphore(5)
        tasks = []
        for page in pages:
            task = asyncio.create_task(self._enhance_single_page(page, semaphore))
            tasks.append(task)
        
        enhanced_pages = await asyncio.gather(*tasks)
        return [p for p in enhanced_pages if p]

    async def _enhance_single_page(self, page: Page, semaphore: asyncio.Semaphore) -> Optional[Page]:
        """Generates a description for a single page using OpenAI."""
        async with semaphore:
            prompt = self._create_prompt(page)
            try:
                description = await self._generate_with_openai(prompt)
                page.description = description.strip() if description else "AI description could not be generated."
                return page
            except Exception as e:
                logger.error(f"Failed to enhance page {page.url}: {e}")
                page.description = "AI enhancement failed due to an error."
                return page

    def _create_prompt(self, page: Page) -> str:
        """Creates a standardized prompt for the LLM."""
        content_snippet = (page.content[:2000] + '...') if len(page.content) > 2000 else page.content
        return f"""
        Analyze the following webpage content and generate a concise, one-sentence description.
        Focus on the main purpose or key takeaway of the page. Do not use phrases like "This page is about".

        **Page Title:** "{page.title}"
        **Page Content Snippet:**
        ---
        {content_snippet}
        ---
        
        **Concise one-sentence description:**
        """

    async def _generate_with_openai(self, prompt: str) -> str:
        """Generates content using the OpenAI API."""
        try:
            import openai
        except ImportError:
            logger.error("openai is not installed. Please run: pip install openai")
            return ""
        import os

        api_key = os.getenv("OPENAI_API_KEY")
        model = "gpt-3.5-turbo"
        if not api_key:
            logger.error("OpenAI API key not found in environment variable.")
            return ""
        openai.api_key = api_key

        # Use openai's async API if available, else run in thread
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes web pages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=128,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except AttributeError:
            # Fallback for older openai versions (run in thread)
            import asyncio
            loop = asyncio.get_event_loop()
            def sync_call():
                return openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes web pages."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=128,
                    temperature=0.7,
                )
            resp = await loop.run_in_executor(None, sync_call)
            return resp.choices[0].message.content.strip()
