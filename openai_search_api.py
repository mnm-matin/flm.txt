from openai import OpenAI
import os
from pathlib import Path

# Load .env file manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-search-preview",
    web_search_options={
        "search_context_size": "low",
    },
    messages=[{
            "role": "system",
            "content": "You search the given domain and return a summary of all websites on it and a list of the most relevant internal links. The goal is to create a llms.txt file that contains all information about the domain. Only use internal links, not external links."
        }, {
            "role": "user",
            "content": "peec.ai",
    }],
)

print(completion.choices[0].message.content)