import asyncio
from crawl_to_llm import LLMSGenerator

async def main():
    generator = LLMSGenerator()
    await generator.run(url="https://example.com", strategy="sitemap", output_format="json")

if __name__ == "__main__":
    asyncio.run(main())
