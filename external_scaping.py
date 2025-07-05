from link_harvesting.link_harvester import (
    seed_urls_via_openai,
    fetch, extract_text, verify, summarise, base_domain
)

# ─── hard limits you can tweak once and forget ─────────────
_OPENAI_LIMIT = 20      # how many URLs to ask the search model for
_MAX_ROWS     = 5      # stop after N verified pages

def get_external_links(domain: str, brand: str) -> dict[str, list[str]]:
    """
    Harvest ONLY 'openai-search' external links.
    
    Parameters
    ----------
    domain : str   e.g.  "peec.ai"
    brand  : str   e.g.  "Peec AI"
    
    Returns
    -------
    dict[str, str]
        { seed_url : external_url }
        (one entry per accepted page, up to _MAX_ROWS)
    """
    seed_url = f"https://{domain.strip('/')}"
    mapping  = {}
    count    = 0

    for ext in seed_urls_via_openai(brand, limit=_OPENAI_LIMIT):
        html = fetch(ext)
        txt  = extract_text(html)
        if txt and verify(txt, brand):
            mapping[seed_url] = [ext]
            count += 1
            if count >= _MAX_ROWS:
                break   # hard stop

    return mapping


# quick manual test
if __name__ == "__main__":
    from pprint import pprint
    pprint(get_external_links("peec.ai", "Peec AI"))
