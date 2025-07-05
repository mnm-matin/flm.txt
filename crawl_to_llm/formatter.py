"""
Handles formatting the output into various file types (llms.txt, JSON, YAML).
This module uses a strategy pattern for different formatters.
"""
import os
import json
import yaml
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from urllib.parse import urlparse

from .data_models import Page

logger = logging.getLogger(__name__)

class BaseFormatter(ABC):
    """Abstract base class for all formatters."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @abstractmethod
    def write(self, pages: List[Page], metadata: Dict[str, Any]):
        """Writes the formatted data to a file."""
        pass

    def _get_domain(self, url: str) -> str:
        """Extracts the domain name from a URL for file naming."""
        return urlparse(url).netloc.replace("www.", "")

class TextFormatter(BaseFormatter):
    """Formats output into llms.txt and llms-full.txt."""

    def write(self, pages: List[Page], metadata: Dict[str, Any]):
        base_url = metadata.get("base_url", "")
        domain = self._get_domain(base_url)
        
        # --- llms.txt (Descriptions) ---
        llms_path = os.path.join(self.output_dir, f"{domain}-llms.txt")
        with open(llms_path, "w", encoding="utf-8") as f:
            f.write(f"# {metadata.get('site_name', domain)}\n\n")
            f.write(f"> Generated from {len(pages)} pages.\n\n")
            for page in pages:
                f.write(f"- [{page.title}]({page.url}): {page.description or 'No description generated.'}\n")
        logger.info(f"Successfully wrote llms.txt to {llms_path}")

        # --- llms-full.txt (Full Content) ---
        full_path = os.path.join(self.output_dir, f"{domain}-llms-full.txt")
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"# Full Content for {base_url}\n")
            f.write(f"# Total pages: {len(pages)}\n\n")
            for i, page in enumerate(pages, 1):
                f.write(f"---\n## Page {i}: {page.title}\n**URL:** {page.url}\n\n")
                f.write(page.content)
                f.write("\n\n")
        logger.info(f"Successfully wrote llms-full.txt to {full_path}")


class JsonFormatter(BaseFormatter):
    """Formats output into a JSON file."""

    def write(self, pages: List[Page], metadata: Dict[str, Any]):
        domain = self._get_domain(metadata.get("base_url", ""))
        filepath = os.path.join(self.output_dir, f"{domain}.json")
        
        output_data = {
            "metadata": metadata,
            "pages": [page.model_dump() for page in pages]
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"Successfully wrote JSON output to {filepath}")

class YamlFormatter(BaseFormatter):
    """Formats output into a YAML file."""

    def write(self, pages: List[Page], metadata: Dict[str, Any]):
        domain = self._get_domain(metadata.get("base_url", ""))
        filepath = os.path.join(self.output_dir, f"{domain}.yaml")

        output_data = {
            "metadata": metadata,
            "pages": [page.model_dump() for page in pages]
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Successfully wrote YAML output to {filepath}")
