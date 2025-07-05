def get_external_links(domain: str) -> dict[str, str]:
    """
    Get the external links from the domain

    Args:
        domain (str): The domain to get the external links from

    Returns:
        dict[str, str]: A dictionary of external links, where the key is the internal link and the value is the external link
    """
    external_links = {}
    # TODO: do some real search for external links
    # for now just return some dummy links
    external_links[f"https://{domain}"] = f"https://www.reddit.com/r/SEO/comments/1j0gt6q/ai_engine_visibility/"
    external_links[f"https://{domain}/about"] = f"https://www.reddit.com/r/SEO/comments/1j0gt6q/ai_engine_visibility/"
    external_links[f"https://{domain}/imprint"] = f"https://www.reddit.com/r/SEO/comments/1j0gt6q/ai_engine_visibility/"
    return external_links


if __name__ == "__main__":
    get_external_links("peec.ai")
