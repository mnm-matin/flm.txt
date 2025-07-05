from typing import List
from collections import defaultdict


def get_certificates(external_links: dict[str, str]) -> dict[str, str]:
    """
    Get the certificates for the external links

    Args:
        external_links (dict[str, str]): A dictionary of external links, where the key is the internal link and the value is the external link

    Returns:
        dict[str, str]: A dictionary of certificates, where the key is the internal link and the value is the certificate
    """
    certificates = defaultdict(list)
    for internal_link, external_link in external_links.items():
        certificate = verify_forward_link(internal_link, external_link)
        if certificate:
            certificates[internal_link].append(certificate)
    return certificates



def verify_forward_link(source_url: str, forward_link: str) -> bool:
    """
    Verifies if a forward link is correctly mentioned for the source URL

    Source URL: URL of the page containing the forward link. (e.g PEEC AI)
    Forward Link: The forward link to verify.

    e.g 
    Source URL: http://peec.ai
    Forward Link: https://www.reddit.com/r/SEO/comments/1j0gt6q/ai_engine_visibility/

    Args:
        source_url (str): The URL of the source page containing the forward link.
        forward_link (str): The forward link to verify.

    Raises:
        NotImplementedError: This function is a stub and needs implementation.
    """
    raise NotImplementedError("This function needs to be implemented.")


# for debugging
if __name__ == "__main__":
    print(verify_forward_link(source_url='http://peec.ai', forward_link='https://www.reddit.com/r/SEO/comments/1j0gt6q/ai_engine_visibility/'))
