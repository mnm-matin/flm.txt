Idea in one sentence  
“Think of an extended robots-style manifest that not only tells an LLM-powered crawler where it may (or may not) go, but also hands it a pre-approved set of outbound URLs—‘forward links’—that the site owner vouches for.”

Why do this?  

1. Authority & provenance  
   • Large-language-model search agents have difficulty deciding which external sources are trustworthy.  
   • If the site author enumerates “forward links,” the agent can treat them as higher-confidence citations, training material or augmentation nodes.  

2. Better attribution & fewer hallucinations  
   • The crawler can quote or paraphrase from whitelisted pages knowing the site owner explicitly endorsed them.  
   • Linking out through a curated list reduces the risk that the model invents references.

3. Fine-grained crawl control beyond robots.txt  
   • robots.txt only says “do/don’t crawl X.”  
   • A Forward-Link Manifest (FLM) also says “these Y URLs are recommended next hops; treat them as canonical or related.”  

4. Faster discovery than HTML link graph  
   • A single machine-readable file is lighter to fetch than crawling every page just to extract anchors.  

What the file might contain  

# “flm.txt” (or any name you choose; user-agent string makes it discoverable)
User-agent: llm-search-bot
# Normal robots semantics
Disallow: /drafts/
Allow: /
# Forward links block
Forward: https://example.org/whitepaper.pdf
Forward: https://partner.example.com/api-spec
Forward: https://doi.org/10.1234/some-journal-article
# Hashes (optional integrity check)
Digest-SHA256: https://example.org/whitepaper.pdf 517f2e…
Digest-SHA256: https://partner.example.com/api-spec 9bafcd…

Directive grammar (illustrative)  
• Forward: absolute-URL — a link owner certifies as relevant/authoritative.  
• Digest-SHA256: URL HASH — assures the model that the payload hasn’t been tampered with.  
• Include: sitemap.xml — avoid duplicate work if you already maintain a sitemap.  
• Expire: 2024-12-31 — date after which the crawler should re-verify or drop the link.

How an LLM agent would use it  

1. Fetch flm.txt (or robots.txt section) first.  
2. Parse normal robots rules to respect crawl constraints.  
3. Parse Forward lines; push those URLs to the front of the crawl queue with “high-trust” metadata.  
4. Optionally verify digests.  
5. When answering user queries, prefer citing these links if they match the topic.

Relationship to existing standards  

• NOT a replacement for robots.txt—the traditional directives still live there; this is an extension.  
• NOT the same as sitemap.xml—sitemaps list the owner’s own pages, whereas Forward lists third-party resources the owner trusts.  
• Can coexist: robots.txt could simply contain  
  ```
  User-agent: llm-search-bot
  Forward-manifest: /flm.txt
  ```  

Open questions / potential pitfalls  

• Abuse: spammers might “forward” to low-quality sites; search engines will still need reputation scoring.  
• Versioning: What happens when a linked page changes? Hash digests help, but require upkeep.  
• Size limits: A giant list defeats the “single fetch” efficiency goal; pagination or Link: headers might be needed.  
• Standardization: To gain traction, major LLM search vendors should agree on at least the directive names.

Naming  

It does not have to be called llm.txt; any filename works if the bot is instructed where to look (robots directive, well-known URI, or HTTP header). “flm.txt” or “llm-robots.txt” are common suggestions.

Short pitch to stakeholders  
“Adding a Forward-Link Manifest lets us curate the outbound universe our content points to, giving LLM crawlers trusted references, reducing hallucinations, and keeping the conventional robots.txt semantics intact—all in one tiny text file.”