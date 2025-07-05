#!/usr/bin/env python3
"""
Minimal Flask app for LLMs.txt generation
"""

from flask import Flask, render_template, jsonify, request
from openai import OpenAI
import os
from pathlib import Path
import internal_scaping
import external_scaping
import llms_txt_generation
import verify

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()


app = Flask(__name__)

@app.route('/')
def index():
    """Serve the index.html file"""
    return render_template('index.html')

@app.route('/api/llmstxt')
def api_llmstxt():
    domain = request.args.get('domain')
    internal_links = internal_scaping.get_summaries(domain)
    external_links = external_scaping.get_external_links(domain)
    certificates = verify.get_certificates(external_links)
    llmstxt = llms_txt_generation.create_llms_txt(domain, internal_links, external_links, certificates)

    return jsonify(llmstxt)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5055)
