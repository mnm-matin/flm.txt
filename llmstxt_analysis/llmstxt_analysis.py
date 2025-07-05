#!/usr/bin/env python3
"""
LLMs.txt Link Analysis Script

This script scrapes https://llmstxt.site/ for all links to llms.txt files,
then analyzes the links in each file to determine:
- How many outgoing links (to other domains)
- How many internal links (to the same domain)
- Statistics grouped by domain
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from collections import defaultdict, Counter
import time
import json
from typing import Dict, List, Tuple, Set
import sys
import signal
import os
import hashlib


class LLMSTxtAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.llms_txt_urls = set()
        self.link_data = {}
        self.domain_stats = defaultdict(lambda: {'internal': 0, 'external': 0, 'total': 0})
        self.interrupted = False
        
        # Simple cache settings
        self.cache_dir = "./cache"
        self.cache_expire_hours = 24
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\nReceived interrupt signal (Ctrl+C)...")
        print("Stopping scraping and generating statistics with data collected so far...")
        self.interrupted = True
        
    def fetch_page(self, url: str) -> str:
        """Fetch a web page with simple caching"""
        # Create simple cache filename from URL hash
        cache_filename = hashlib.md5(url.encode()).hexdigest() + '.txt'
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        # Check if cache exists and is recent
        if os.path.exists(cache_path):
            cache_age = time.time() - os.path.getmtime(cache_path)
            if cache_age < (self.cache_expire_hours * 3600):  # Convert hours to seconds
                print(f"Cache hit: {url}")
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except:
                    # If cache read fails, continue to fetch
                    pass
        
        # Fetch from web
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            # Save to cache
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                # If cache write fails, continue anyway
                pass
            
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_llms_txt_links(self, html_content: str, base_url: str) -> Set[str]:
        """Extract all links to llms.txt files from the HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        llms_txt_links = set()
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if it's a link to llms.txt
            if href.endswith('llms.txt') or '/llms.txt' in href:
                full_url = urljoin(base_url, href)
                llms_txt_links.add(full_url)
        
        return llms_txt_links
    
    def extract_links_from_llms_txt(self, content: str) -> List[str]:
        """Extract all URLs from llms.txt content"""
        if not content:
            return []
        
        # Find URLs using regex
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+[^\s<>"{}|\\^`[\].,;:!?)]'
        urls = re.findall(url_pattern, content)
        
        # Also look for markdown-style links
        markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        markdown_matches = re.findall(markdown_pattern, content)
        for _, url in markdown_matches:
            if url.startswith('http'):
                urls.append(url)
        
        return urls
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "unknown"
    
    def normalize_domain(self, domain: str) -> str:
        """Normalize domain for more robust matching"""
        if not domain or domain == "unknown":
            return domain
        
        # Remove port numbers
        domain = domain.split(':')[0]
        
        # Remove www prefix for comparison
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower()
    
    def get_base_domain(self, url: str) -> str:
        """Extract and normalize the base domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return self.normalize_domain(domain)
        except:
            return "unknown"
    
    def are_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs belong to the same domain (considering subdomains)"""
        try:
            domain1 = self.get_base_domain(url1)
            domain2 = self.get_base_domain(url2)
            
            if domain1 == "unknown" or domain2 == "unknown":
                return False
            
            # Direct match
            if domain1 == domain2:
                return True
            
            # Check if one is a subdomain of the other
            # For example: blog.example.com should match example.com
            parts1 = domain1.split('.')
            parts2 = domain2.split('.')
            
            # Get the main domain (last 2 parts for most cases)
            if len(parts1) >= 2 and len(parts2) >= 2:
                main_domain1 = '.'.join(parts1[-2:])
                main_domain2 = '.'.join(parts2[-2:])
                
                # Handle special cases like .co.uk, .com.au, etc.
                # For now, we'll use a simple heuristic
                if main_domain1 == main_domain2:
                    return True
                
                # Check if one domain ends with the other (subdomain relationship)
                if domain1.endswith('.' + domain2) or domain2.endswith('.' + domain1):
                    return True
            
            return False
        except:
            return False
    
    def analyze_llms_txt_file(self, url: str) -> Dict:
        """Analyze a single llms.txt file"""
        print(f"Analyzing llms.txt: {url}")
        
        content = self.fetch_page(url)
        if not content:
            return None
        
        # Extract all links from the content
        links = self.extract_links_from_llms_txt(content)
        
        # Get the domain of the llms.txt file
        source_domain = self.get_domain(url)
        normalized_source_domain = self.get_base_domain(url)
        
        # Categorize links using robust domain matching
        internal_links = []
        external_links = []
        
        for link in links:
            if self.are_same_domain(url, link):
                internal_links.append(link)
            else:
                external_links.append(link)
        
        analysis = {
            'url': url,
            'source_domain': source_domain,
            'normalized_source_domain': normalized_source_domain,
            'total_links': len(links),
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'internal_link_list': internal_links,
            'external_link_list': external_links,
            'external_domains': Counter([self.get_base_domain(link) for link in external_links])
        }
        
        return analysis
    
    def scrape_llmstxt_site(self):
        """Scrape the main llmstxt.site page for llms.txt links"""
        print("Scraping https://llmstxt.site/ for llms.txt links...")
        
        content = self.fetch_page('https://llmstxt.site/')
        if not content:
            print("Failed to fetch the main page")
            return
        
        # Extract llms.txt links
        llms_txt_links = self.extract_llms_txt_links(content, 'https://llmstxt.site/')
        
        print(f"Found {len(llms_txt_links)} llms.txt links")
        for link in sorted(llms_txt_links):
            print(f"  - {link}")
        
        self.llms_txt_urls = llms_txt_links
    
    def analyze_all_llms_txt_files(self):
        """Analyze all found llms.txt files"""
        print("\nAnalyzing all llms.txt files...")
        print("Press Ctrl+C to stop scraping and generate statistics with current data")
        
        for i, url in enumerate(self.llms_txt_urls, 1):
            # Check for interruption
            if self.interrupted:
                print(f"\nInterrupted after processing {i-1} files.")
                break
                
            print(f"\n[{i}/{len(self.llms_txt_urls)}] Processing: {url}")
            
            analysis = self.analyze_llms_txt_file(url)
            if analysis:
                self.link_data[url] = analysis
                
                # Update domain statistics using normalized domain for better grouping
                domain = analysis['normalized_source_domain']
                self.domain_stats[domain]['internal'] += analysis['internal_links']
                self.domain_stats[domain]['external'] += analysis['external_links']
                self.domain_stats[domain]['total'] += analysis['total_links']
            
            # Be nice to servers
            time.sleep(0.5)
    
    def generate_statistics(self):
        """Generate and display comprehensive statistics"""
        print("\n" + "="*80)
        if self.interrupted:
            print("PARTIAL STATISTICS (Analysis was interrupted)")
        else:
            print("COMPREHENSIVE STATISTICS")
        print("="*80)
        
        # Overall statistics
        total_files = len(self.link_data)
        total_links = sum(data['total_links'] for data in self.link_data.values())
        total_internal = sum(data['internal_links'] for data in self.link_data.values())
        total_external = sum(data['external_links'] for data in self.link_data.values())
        
        print(f"\nOVERALL SUMMARY:")
        if self.interrupted:
            print(f"  ⚠️  Analysis was interrupted - showing partial results")
            print(f"  Total llms.txt files found: {len(self.llms_txt_urls)}")
        print(f"  Total llms.txt files analyzed: {total_files}")
        print(f"  Total links found: {total_links}")
        if total_links > 0:
            print(f"  Total internal links: {total_internal} ({total_internal/total_links*100:.1f}%)")
            print(f"  Total external links: {total_external} ({total_external/total_links*100:.1f}%)")
        else:
            print(f"  Total internal links: {total_internal}")
            print(f"  Total external links: {total_external}")
        
        # Domain-wise statistics
        print(f"\nDOMAIN-WISE STATISTICS:")
        print(f"{'Domain':<30} {'Internal':<10} {'External':<10} {'Total':<10} {'Internal %':<12}")
        print("-" * 75)
        
        for domain, stats in sorted(self.domain_stats.items()):
            internal_pct = (stats['internal'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{domain:<30} {stats['internal']:<10} {stats['external']:<10} {stats['total']:<10} {internal_pct:<12.1f}%")
        
        # Top external domains
        all_external_domains = Counter()
        for data in self.link_data.values():
            all_external_domains.update(data['external_domains'])
        
        print(f"\nTOP 15 EXTERNAL DOMAINS REFERENCED:")
        print(f"{'Domain':<40} {'Count':<8}")
        print("-" * 50)
        for domain, count in all_external_domains.most_common(15):
            print(f"{domain:<40} {count:<8}")
        
        # Files with highest external link ratios
        print(f"\nFILES WITH HIGHEST EXTERNAL LINK RATIOS:")
        print(f"{'Domain':<30} {'External %':<12} {'External/Total':<15}")
        print("-" * 60)
        
        external_ratios = []
        for data in self.link_data.values():
            if data['total_links'] > 0:
                ratio = data['external_links'] / data['total_links']
                external_ratios.append((data['normalized_source_domain'], ratio, f"{data['external_links']}/{data['total_links']}"))
        
        for domain, ratio, fraction in sorted(external_ratios, key=lambda x: x[1], reverse=True)[:10]:
            print(f"{domain:<30} {ratio*100:<12.1f}% {fraction:<15}")
        
        # Files with most internal links
        print(f"\nFILES WITH MOST INTERNAL LINKS:")
        print(f"{'Domain':<30} {'Internal Links':<15} {'Total Links':<12}")
        print("-" * 60)
        
        internal_counts = [(data['normalized_source_domain'], data['internal_links'], data['total_links']) 
                          for data in self.link_data.values()]
        
        for domain, internal, total in sorted(internal_counts, key=lambda x: x[1], reverse=True)[:10]:
            print(f"{domain:<30} {internal:<15} {total:<12}")
        
        # Show examples of domain classification for validation
        print(f"\nDOMAIN CLASSIFICATION EXAMPLES (for validation):")
        print(f"{'Source Domain':<25} {'Link Domain':<25} {'Classification':<12} {'Sample Link':<50}")
        print("-" * 115)
        
        shown_examples = 0
        for data in list(self.link_data.values())[:5]:  # Show examples from first 5 files
            source_domain = data['normalized_source_domain']
            
            # Show a few internal links
            for link in data['internal_link_list'][:2]:
                link_domain = self.get_base_domain(link)
                print(f"{source_domain:<25} {link_domain:<25} {'Internal':<12} {link[:50]:<50}")
                shown_examples += 1
                if shown_examples >= 10:
                    break
                    
            # Show a few external links
            for link in data['external_link_list'][:2]:
                link_domain = self.get_base_domain(link)
                print(f"{source_domain:<25} {link_domain:<25} {'External':<12} {link[:50]:<50}")
                shown_examples += 1
                if shown_examples >= 10:
                    break
                    
            if shown_examples >= 10:
                break
        
        # Save detailed results to JSON
        print(f"\nSaving detailed results to 'llmstxt_analysis_results.json'...")
        with open('llmstxt_analysis_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_files': total_files,
                    'total_links': total_links,
                    'total_internal': total_internal,
                    'total_external': total_external
                },
                'domain_stats': dict(self.domain_stats),
                'detailed_analysis': self.link_data,
                'top_external_domains': dict(all_external_domains.most_common(50))
            }, f, indent=2)
    
    def run(self):
        """Main execution method"""
        print("Starting LLMs.txt Link Analysis")
        print("="*50)
        print(f"Cache directory: {os.path.abspath(self.cache_dir)}")
        print()
        
        # Set up signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # Step 1: Scrape llmstxt.site for llms.txt links
            self.scrape_llmstxt_site()
            
            if not self.llms_txt_urls:
                print("No llms.txt links found. Exiting.")
                return
            
            # Step 2: Analyze each llms.txt file (caching happens transparently)
            self.analyze_all_llms_txt_files()
            
        except KeyboardInterrupt:
            # This shouldn't happen now since we handle it with signal handler
            print("\nKeyboard interrupt received...")
            self.interrupted = True
        
        # Step 3: Generate statistics (always run this, even if interrupted)
        if self.link_data:
            self.generate_statistics()
        else:
            print("\nNo data collected to generate statistics.")
        
        if self.interrupted:
            print("\nAnalysis interrupted by user.")
        else:
            print("\nAnalysis complete!")


def main():
    analyzer = LLMSTxtAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
