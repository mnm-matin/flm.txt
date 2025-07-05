

def create_llms_txt(domain: str, summary: str, internal_links: dict[str, dict[str, str]], external_links: dict[str, str], certificates: dict[str, str]) -> str:
    """
    Create a llms.txt file for the domain

    Args:
        domain (str): The domain to create the llms.txt file for
        summary (str): The summary of the domain
        internal_links (dict[str, dict[str, str]]): A dictionary of internal links, where the key is the URL and the value is a dictionary with the title and summary
        external_links (dict[str, str]): A dictionary of external links, where the key is the internal link and the value is the external link
        certificates (dict[str, str]): A dictionary of certificates, where the key is the internal link and the value is the certificate

    Returns:
        str: The llms.txt file as a string
    """
    llmstxt = f"# {domain}"

    # summary
    llmstxt += f"\n{summary}\n"

    # pages overview
    llmstxt += "\n## Pages Overview\n"
    for url, summary in internal_links.items():
        # Use markdown header for the title
        llmstxt += f"### {summary['title']}\n"

        # Use proper markdown link format
        llmstxt += f"**URL:** [{url}]({url})\n"

        # Format summary with proper markdown
        llmstxt += f"**Summary:**\n{summary['summary']}\n"

        # Add external links if they exist
        if url in external_links:
            llmstxt += f"**External Links:**\n"
            for x in external_links[url]:
                llmstxt += f"- [{x.lstrip('https://').split('/')[0]}]({x}) - {certificates[url][0].split('\n')[1]}\n"

        # Add horizontal rule to separate entries
        llmstxt += "\n\n"

    return llmstxt
