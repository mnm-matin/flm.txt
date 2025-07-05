"""
Defines the core Pydantic models for data structures.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Page(BaseModel):
    """Represents a single crawled web page."""
    url: str
    title: str
    content: str
    word_count: int
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CrawlResult(BaseModel):
    """Represents the complete result of a crawl operation."""
    pages: List[Page]
    metadata: Dict[str, Any] = Field(default_factory=dict)
