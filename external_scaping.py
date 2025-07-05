def get_external_links(domain: str) -> dict[str, str]:
    """
    Get the external links from the domain

    Args:
        domain (str): The domain to get the external links from

    Returns:
        dict[str, str]: A dictionary of external links, where the key is the internal link and the value is the external link
    """
    raise NotImplementedError("This function needs to be implemented.")


if __name__ == "__main__":
    get_external_links("peec.ai")