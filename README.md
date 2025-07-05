# Forward-Link Manifest (FLM)

A Forward-Link Manifest (FLM) extends traditional robots.txt functionality, enabling site owners to explicitly recommend trusted external URLs for LLM-powered crawlers. This structured manifest helps crawlers identify authoritative sources, improving citation accuracy, reducing hallucinations, and optimizing crawl efficiency.

## Key Benefits

- **Enhanced Trust & Provenance**: Clearly identifies authoritative external resources.
- **Improved Attribution**: Reduces hallucinations by providing explicitly endorsed references.
- **Fine-Grained Control**: Offers more detailed crawl instructions beyond traditional robots.txt.
- **Efficient Crawling**: Accelerates discovery of trusted resources without exhaustive HTML parsing.

## Example Usage

```txt
User-agent: llm-search-bot
Disallow: /drafts/
Allow: /

Forward: https://example.org/whitepaper.pdf
Forward: https://partner.example.com/api-spec
Digest-SHA256: https://example.org/whitepaper.pdf 517f2e...
```

## Relationship to Existing Standards

- Complements `robots.txt` (does not replace it).
- Different from `sitemap.xml` (lists external, trusted resources rather than internal pages).
