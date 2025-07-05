

def create_llms_txt(domain: str, internal_links: dict[str, dict[str, str]], external_links: dict[str, str], certificates: dict[str, str]) -> str:
    """
    Create a llms.txt file for the domain
    """
    llmstxt = ""
    # TODO: summary
    for url, summary in internal_links.items():
        llmstxt += f"title: {summary['title']}\n"
        llmstxt += f"url: {url}\n"
        # llmstxt += f"important: {summary['important']}\n"
        llmstxt += f"summary: {summary['summary']}\n"
        if url in external_links:
            external_link = external_links[url]
            llmstxt += f"external_link: {external_link}\n"
            if external_link in certificates:
                certificate = certificates[external_link]
                llmstxt += f"certificate: {certificate}\n"
        llmstxt += "\n\n"
    return llmstxt
