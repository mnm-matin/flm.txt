import requests
import json
from bs4 import BeautifulSoup
import re
import os
from pathlib import Path
from openai import OpenAI


from dotenv import load_dotenv
load_dotenv()

client = OpenAI()



def summarize(text: str) -> dict:
    """
    Summarize the text
    """
    # Summarize the content using LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You shortly summarize the content of the page. Additionally, you check if the site is very important/essential to understand what the domain is about (specific subsites are usually not important). You output a json object with the following fields: title: string, summary: string, important: boolean."},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    ).choices[0].message.content

    # return json object
    return json.loads(response)



def get_summaries(domain: str, max_scapes: int = 20) -> dict[str, str]:
    """
    Scape the domain and return the llms.txt file
    """
    print(f"Scaping {domain}")
    domain = domain.strip().rstrip('/')

    # Ensure domain is a full URL
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"

    summaries = dict()
    internal_links = set([domain])

    # Try to load sitemap
    try:
        raise  # TODO: just for debugging
        sitemap_url = f"{domain}/sitemap.xml"
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            # Successfully found sitemap
            print(f"Sitemap found")
            sitemap_content = response.text
            # Parse sitemap
            soup = BeautifulSoup(sitemap_content, "xml")
            for url in soup.find_all("loc"):
                internal_links.add(url.text)
        else:
            print(f"Sitemap not available")
    except:
        # Sitemap not available or error occurred
        print(f"Sitemap not available")

    # Try to load llms.txt
    try:
        llms_txt_url = f"{domain}/llms.txt"
        response = requests.get(llms_txt_url)
        if response.status_code == 200:
            print(f"LLMs.txt found")
            llms_txt_content = response.text
            # Parse markdown links from llms.txt
            md_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', llms_txt_content)
            for _, url in md_links:
                if url.startswith(domain) or url.startswith(f"{domain}/"):
                    if url.startswith('/'):
                        url = f"{domain}{url}"
                    internal_links.add(url)
        else:
            print(f"LLMs.txt not available")
    except requests.exceptions.RequestException as e:
        print(f"LLMs.txt not available")

    while internal_links:
        if len(summaries) >= max_scapes:
            break
        url = internal_links.pop()
        print(f"[{len(summaries)+1}/{len(internal_links)+len(summaries)+1}] Scaping {url}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Parse HTML and extract meaningful content
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                site_content = soup.get_text()
                site_content = " ".join(site_content.split())

                summaries[url] = summarize(site_content)
                new_links_raw = soup.find_all("a")
                new_links = set()
                for link in new_links_raw:
                    href = link.get("href").strip()
                    href = href.split('#')[0]  # remove anchor
                    if not href:
                        continue
                    elif href.startswith(domain) or href.startswith(f"{domain}/"):
                        pass
                    elif href.startswith('/'):
                        href = f"{domain}{href}"
                    elif href.startswith('./'):
                        href = f"{domain}{href[1:]}"
                    else:
                        continue
                    new_links.add(href)
                internal_links.update(new_links - summaries.keys())

        except requests.exceptions.RequestException as e:
            print(f"Failed: {e}")
            continue

    return summaries


# just for testing
def create_summary(summaries: dict[str, dict[str, str]]) -> str:
    summaries_combined = ""
    for url, summary in summaries.items():
        summaries_combined += f"title: {summary['title']}\n"
        summaries_combined += f"url: {url}\n"
        summaries_combined += f"important: {summary['important']}\n"
        summaries_combined += f"summary: {summary['summary']}\n"
        summaries_combined += "\n---\n\n"

    print("#"*50)
    print(summaries_combined)
    print("#"*50)


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create a summary of the domain based on the summaries of the internal pages. You output the summary as a string."},
            {"role": "user", "content": summaries_combined}
        ]
    )

    return response.choices[0].message.content


# just for testing
if __name__ == "__main__":
    summaries = get_summaries("peec.ai")
    result = create_summary(summaries)
    print(result)
