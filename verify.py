from typing import List
from sentence_transformers import SentenceTransformer
import requests
import numpy as np
# --------------------
# Utility Functions
# --------------------
def normalize(text):
    # Clean and normalize text
    text = text.lower()
    # Remove HTML tags
    text = text.replace("<br>", " ").replace("<br/>", " ")
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def get_embedding(text, model):
    """Get sentence embedding for the text"""
    return model.encode(text)

def similarity(a, b):
    """Calculate cosine similarity between two texts using sentence embeddings"""
    # Initialize model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get embeddings
    embedding_a = get_embedding(a, model)
    embedding_b = get_embedding(b, model)
    
    # Calculate cosine similarity
    similarity_score = np.dot(embedding_a, embedding_b) / (np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b))
    return similarity_score

def parse_forward_links(file_path: str) -> List[str]:
    """
    Parses an llm.txt file and returns a list of forward links.

    Args:
        file_path (str): Path to the llm.txt file.

    Returns:
        List[str]: List of forward links extracted from the file.
    """
    forward_links = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Forward:"):
                link = line.split("Forward:", 1)[1].strip()
                forward_links.append(link)
    return forward_links

def verify_forward_link(source_url: str, forward_link: list[str]) -> bool:
    """
    Verifies if a forward link is correctly mentioned for the source URL

    Source URL: URL of the page containing the forward link. (e.g PEEC AI)
    Forward Link: The forward link to verify.

    e.g 
    Source URL: http://peec.ai
    Forward Link: https://www.reddit.com/r/SEO/comments/1j0gt6q/ai_engine_visibility/

    Args:
        source_url (str): The URL of the source page containing the forward link.
        forward_link (list[str]): The forward link to verify.

    Raises:
        NotImplementedError: This function is a stub and needs implementation.
    """
    # raise NotImplementedError("This function needs to be implemented.")

    llm_response = requests.get(source_url, timeout=10)
    llm_response.raise_for_status()
    llm_text = normalize(llm_response.text)

    for link in forward_link:
        forward_link_response = requests.get(link, timeout=10)
        forward_link_response.raise_for_status()
        forward_link_text = normalize(forward_link_response.text)

        score = similarity(llm_text, forward_link_text)
        print(f"Score: {score}, link: {link}")
        if score < 0.1:
            return False
    return True

result = verify_forward_link(source_url='https://www.purdueglobal.edu/blog/student-life/valuable-health-wellness-blogs/', forward_link=['https://www.acefitness.org/resources/pros/expert-articles/'])
print(result)

result2 = verify_forward_link(source_url='https://www.purdueglobal.edu/blog/student-life/valuable-health-wellness-blogs/', forward_link=['https://public.com/?wpsrc=Organic+Search&wpsn=www.google.com'])
print(result2)
