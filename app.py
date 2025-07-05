#!/usr/bin/env python3
"""
Minimal Flask app for LLMs.txt generation
"""

from flask import Flask, render_template, jsonify, request
from openai import OpenAI
import os
from pathlib import Path



env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

client = OpenAI()


app = Flask(__name__)

@app.route('/')
def index():
    """Serve the index.html file"""
    return render_template('index.html')

@app.route('/api/llmstxt')
def api_llmstxt():
    domain = request.args.get('domain')
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
                "content": domain,
        }],
    )

    return jsonify(completion.choices[0].message.content)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
