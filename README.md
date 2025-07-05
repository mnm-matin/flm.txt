# Forward-Link Manifest (FLM)

A Forward-Link Manifest (FLM) extends traditional robots.txt functionality, enabling site owners to explicitly recommend trusted external URLs for LLM-powered crawlers. This structured manifest helps crawlers identify authoritative sources, improving citation accuracy, reducing hallucinations, and optimizing crawl efficiency.

## Key Benefits

- **Enhanced Trust & Provenance**: Clearly identifies authoritative external resources.
- **Improved Attribution**: Reduces hallucinations by providing explicitly endorsed references.
- **Fine-Grained Control**: Offers more detailed crawl instructions beyond traditional robots.txt.
- **Efficient Crawling**: Accelerates discovery of trusted resources without exhaustive HTML parsing.

## Demo

![Demo](docs/demo.png)

## Flow Diagram

![Flow](docs/flow.png)

## Documentation

For detailed documentation and examples, visit: [https://github.com/mnm-matin/flm.txt](https://github.com/mnm-matin/flm.txt)

## Example Usage

```txt
User-agent: llm-search-bot
Disallow: /drafts/
Allow: /

Forward: https://example.org/whitepaper.pdf
Forward: https://partner.example.com/api-spec
Digest-SHA256: https://example.org/whitepaper.pdf 517f2e...
```

## Relationship to Existing Standards

- Complements `robots.txt` (does not replace it).
- Different from `sitemap.xml` (lists external, trusted resources rather than internal pages).

## Installation and Setup

Follow these steps to set up the project environment:

### 1. Create a virtual environment using `uv`

```bash
uv venv
source .venv/bin/activate
```

### 2. Install dependencies from `requirements.txt`

```bash
uv pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
playwright install
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 5. Launch the application

Start the Flask application:

```bash
python app.py
```

The application will be available at `http://localhost:5055`

### API Endpoints

- **GET /**: Main interface for the FLM generator
- **GET /explainer**: Documentation and explanation page
- **GET /api/flm?domain=example.com**: Generate FLM for a specific domain

### Usage Example

Once the app is running, you can:

1. Visit `http://localhost:5055` to use the web interface
2. Or make API calls directly: `http://localhost:5055/api/flm?domain=example.com`

---

<div align="center" style="display: flex; justify-content: center; align-items: center; gap: 50px; flex-wrap: wrap;">
  <div>
    <h3>PEEC.AI</h3>
    <a href="https://peec.ai/">
      <img src="https://assets.reviews.omr.com/t7b8cun56abnl2mhz6s1wk64ibn8" alt="PEEC.AI" width="200" height="auto">
    </a>
  </div>
  
  <div>
    <h3>{Tech : Europe}</h3>
    <a href="https://techeurope.io/">
      <img src="https://techeurope.io/wp-content/uploads/2025/01/european-flag-1-150x150.png" alt="Tech Europe" width="150" height="150">
    </a>
  </div>
</div>
