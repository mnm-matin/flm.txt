"""
Exports the public API for the crawl_to_llm package.
"""
from .generator import LLMSGenerator
from .data_models import Page

__all__ = ["LLMSGenerator", "Page"]
__version__ = "1.0.0"
