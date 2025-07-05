# Crawl4ai - AI Friendly Documentation (aka LLM.TXT)

This document provides AI-friendly documentation for the Crawl4ai library. It contains three types of content:

**Memory (Facts)**: Similar to traditional LLM.txt files, this section contains factual information about the library - what it is, what it does, its components, APIs, and capabilities. This is the reference knowledge that an AI needs to understand the library.

**Reasoning (Instructions)**: This section instructs AI models on how to use the factual knowledge, think about problems in the way the library authors intended, and provide solutions that align with the library's design philosophy. It guides the AI's problem-solving approach when working with Crawl4ai.

**Examples**: Practical code examples demonstrating how to use the library's features in real-world scenarios. These examples help AI models understand the practical application of the concepts.

## Content (Memory)

```markdown
# Detailed Outline for crawl4ai - deployment Component

**Target Document Type:** memory
**Target Output Filename Suggestion:** `llm_memory_deployment.md`
**Library Version Context:** 0.6.0 (as per Dockerfile ARG `C4AI_VER` from provided `Dockerfile` content)
**Outline Generation Date:** 2025-05-24
---

## 1. Introduction to Deployment
    * 1.1. Purpose: This document provides a factual reference for installing the `crawl4ai` library and deploying its server component using Docker. It covers basic and advanced library installation, various Docker deployment methods, server configuration, and an overview of the API for interaction.
    * 1.2. Scope:
        * Installation of the `crawl4ai` Python library.
        * Setup and diagnostic commands for the library.
        * Deployment of the `crawl4ai` server using Docker, including pre-built images, Docker Compose, and manual builds.
        * Explanation of Dockerfile parameters and server configuration via `config.yml`.
        * Details of API interaction, including the Playground UI, Python SDK, and direct REST API calls.
        * Overview of additional server API endpoints and Model Context Protocol (MCP) support.
        * High-level understanding of the server's internal logic relevant to users.
        * The library's version numbering scheme.

## 2. Library Installation

    * 2.1. **Basic Library Installation**
        * 2.1.1. Standard Installation
            * Command: `pip install crawl4ai`
            * Purpose: Installs the core `crawl4ai` library and its essential dependencies for performing web crawling and scraping tasks. This provides the fundamental `AsyncWebCrawler` and related configuration objects.
        * 2.1.2. Post-Installation Setup
            * Command: `crawl4ai-setup`
            * Purpose:
                * Initializes the user's home directory structure for Crawl4ai (e.g., `~/.crawl4ai/cache`).
                * Installs or updates necessary Playwright browsers (Chromium is installed by default) required for browser-based crawling. The `crawl4ai-setup` script internally calls `playwright install --with-deps chromium`.
                * Performs OS-level checks for common missing libraries that Playwright might depend on, providing guidance if issues are found.
                * Creates a default `global.yml` configuration file if one doesn't exist.
        * 2.1.3. Diagnostic Check
            * Command: `crawl4ai-doctor`
            * Purpose:
                * Verifies Python version compatibility.
                * Confirms Playwright installation and browser integrity by attempting a simple crawl of `https://crawl4ai.com`.
                * Inspects essential environment variables and potential library conflicts that might affect Crawl4ai's operation.
                * Provides diagnostic messages indicating success or failure of these checks, with suggestions for resolving common issues.
        * 2.1.4. Verification Process
            * Purpose: To confirm that the basic installation and setup were successful and Crawl4ai can perform a simple crawl.
            * Script Example (as inferred from `crawl4ai-doctor` logic and typical usage):
                ```python
                import asyncio
                from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

                async def main():
                    browser_config = BrowserConfig(
                        headless=True,
                        browser_type="chromium",
                        ignore_https_errors=True,
                        light_mode=True,
                        viewport_width=1280,
                        viewport_height=720,
                    )
                    run_config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        screenshot=True,
                    )
                    async with AsyncWebCrawler(config=browser_config) as crawler:
                        print("Testing crawling capabilities...")
                        result = await crawler.arun(url="https://crawl4ai.com", config=run_config)
                        if result and result.markdown:
                            print("âœ… Crawling test passed!")
                            return True
                        else:
                            print("âŒ Test failed: Failed to get content")
                            return False

                if __name__ == "__main__":
                    asyncio.run(main())
                ```
            * Expected Outcome: The script should print "âœ… Crawling test passed!" and successfully output Markdown content from the crawled page.

    * 2.2. **Advanced Library Installation (Optional Features)**
        * 2.2.1. Installation of Optional Extras
            * Purpose: To install additional dependencies required for specific advanced features of Crawl4ai, such as those involving machine learning models.
            * Options (as defined in `pyproject.toml`):
                * `pip install crawl4ai[pdf]`:
                    * Purpose: Installs `PyPDF2` for PDF processing capabilities.
                * `pip install crawl4ai[torch]`:
                    * Purpose: Installs `torch`, `nltk`, and `scikit-learn`. Enables features relying on PyTorch models, such as some advanced text clustering or semantic analysis within extraction strategies.
                * `pip install crawl4ai[transformer]`:
                    * Purpose: Installs `transformers` and `tokenizers`. Enables the use of Hugging Face Transformers models for tasks like summarization, question answering, or other advanced NLP features within Crawl4ai.
                * `pip install crawl4ai[cosine]`:
                    * Purpose: Installs `torch`, `transformers`, and `nltk`. Specifically for features utilizing cosine similarity with embeddings (implies model usage).
                * `pip install crawl4ai[sync]`:
                    * Purpose: Installs `selenium` for synchronous crawling capabilities (less common, as Crawl4ai primarily focuses on async).
                * `pip install crawl4ai[all]`:
                    * Purpose: Installs all optional dependencies listed above (`PyPDF2`, `torch`, `nltk`, `scikit-learn`, `transformers`, `tokenizers`, `selenium`), providing the complete suite of Crawl4ai capabilities.
        * 2.2.2. Model Pre-fetching
            * Command: `crawl4ai-download-models` (maps to `crawl4ai.model_loader:main`)
            * Purpose: Downloads and caches machine learning models (e.g., specific sentence transformers or classification models from Hugging Face) that are used by certain optional features, particularly those installed via `crawl4ai[transformer]` or `crawl4ai[cosine]`. This avoids runtime downloads and ensures models are available offline.

## 3. Docker Deployment (Server Mode)

    * 3.1. **Prerequisites**
        * 3.1.1. Docker: A working Docker installation. (Link: `https://docs.docker.com/get-docker/`)
        * 3.1.2. Git: Required for cloning the `crawl4ai` repository if building locally or using Docker Compose from the repository. (Link: `https://git-scm.com/book/en/v2/Getting-Started-Installing-Git`)
        * 3.1.3. RAM Requirements:
            * Minimum: 2GB for the basic server without intensive LLM tasks. The `Dockerfile` HEALTCHECK indicates a warning if less than 2GB RAM is available.
            * Recommended for LLM support: 4GB+ (as specified in `docker-compose.yml` limits).
            * Shared Memory (`/dev/shm`): Recommended size is 1GB (`--shm-size=1g`) for optimal Chromium browser performance, as specified in `docker-compose.yml` and run commands.
    * 3.2. **Installation Options**
        * 3.2.1. **Using Pre-built Images from Docker Hub**
            * 3.2.1.1. Image Source: `unclecode/crawl4ai:<tag>`
                * Explanation of `<tag>`:
                    * `latest`: Points to the most recent stable release of Crawl4ai.
                    * Specific version tags (e.g., `0.6.0`, `0.5.1`): Correspond to specific library releases.
                    * Pre-release tags (e.g., `0.6.0-rc1`, `0.7.0-devN`): Development or release candidate versions for testing.
            * 3.2.1.2. Pulling the Image
                * Command: `docker pull unclecode/crawl4ai:<tag>` (e.g., `docker pull unclecode/crawl4ai:latest`)
            * 3.2.1.3. Environment Setup (`.llm.env`)
                * File Name: `.llm.env` (to be created by the user in the directory where `docker run` or `docker-compose` commands are executed).
                * Purpose: To securely provide API keys for various LLM providers used by Crawl4ai for features like LLM-based extraction or Q&A.
                * Example Content (based on `docker-compose.yml`):
                    ```env
                    OPENAI_API_KEY=your_openai_api_key
                    DEEPSEEK_API_KEY=your_deepseek_api_key
                    ANTHROPIC_API_KEY=your_anthropic_api_key
                    GROQ_API_KEY=your_groq_api_key
                    TOGETHER_API_KEY=your_together_api_key
                    MISTRAL_API_KEY=your_mistral_api_key
                    GEMINI_API_TOKEN=your_gemini_api_token
                    ```
                * Creation: Users should create this file and populate it with their API keys. An example (`.llm.env.example`) might be provided in the repository.
            * 3.2.1.4. Running the Container
                * Basic Run (without LLM support):
                    * Command: `docker run -d -p 11235:11235 --shm-size=1g --name crawl4ai-server unclecode/crawl4ai:<tag>`
                    * Port Mapping: `-p 11235:11235` maps port 11235 on the host to port 11235 in the container (default server port).
                    * Shared Memory: `--shm-size=1g` allocates 1GB of shared memory for the browser.
                * Run with LLM Support (mounting `.llm.env`):
                    * Command: `docker run -d -p 11235:11235 --env-file .llm.env --shm-size=1g --name crawl4ai-server unclecode/crawl4ai:<tag>`
            * 3.2.1.5. Stopping the Container
                * Command: `docker stop crawl4ai-server`
                * Command (to remove): `docker rm crawl4ai-server`
            * 3.2.1.6. Docker Hub Versioning:
                * Docker image tags on Docker Hub (e.g., `unclecode/crawl4ai:0.6.0`) directly correspond to `crawl4ai` library releases. The `latest` tag usually points to the most recent stable release. Pre-release tags include suffixes like `-devN`, `-aN`, `-bN`, or `-rcN`.

        * 3.2.2. **Using Docker Compose (`docker-compose.yml`)**
            * 3.2.2.1. Cloning the Repository
                * Command: `git clone https://github.com/unclecode/crawl4ai.git`
                * Command: `cd crawl4ai`
            * 3.2.2.2. Environment Setup (`.llm.env`)
                * File Name: `.llm.env` (should be created in the root of the cloned `crawl4ai` repository).
                * Purpose: Same as above, to provide LLM API keys.
            * 3.2.2.3. Running Pre-built Images
                * Command: `docker-compose up -d`
                * Behavior: Uses the image specified in `docker-compose.yml` (e.g., `${IMAGE:-unclecode/crawl4ai}:${TAG:-latest}`).
                * Overriding image tag: `TAG=0.6.0 docker-compose up -d` or `IMAGE=mycustom/crawl4ai TAG=mytag docker-compose up -d`.
            * 3.2.2.4. Building Locally with Docker Compose
                * Command: `docker-compose up -d --build`
                * Build Arguments (passed from environment variables to `docker-compose.yml` which then passes to `Dockerfile`):
                    * `INSTALL_TYPE`: (e.g., `default`, `torch`, `all`)
                        * Purpose: To include optional Python dependencies during the Docker image build process.
                        * Example: `INSTALL_TYPE=all docker-compose up -d --build`
                    * `ENABLE_GPU`: (e.g., `true`, `false`)
                        * Purpose: To include GPU support (e.g., CUDA toolkits) in the Docker image if the build hardware and target runtime support it.
                        * Example: `ENABLE_GPU=true docker-compose up -d --build`
            * 3.2.2.5. Stopping Docker Compose Services
                * Command: `docker-compose down`

        * 3.2.3. **Manual Local Build & Run**
            * 3.2.3.1. Cloning the Repository: (As above)
            * 3.2.3.2. Environment Setup (`.llm.env`): (As above)
            * 3.2.3.3. Building with `docker buildx`
                * Command Example:
                    ```bash
                    docker buildx build --platform linux/amd64,linux/arm64 \
                      --build-arg C4AI_VER=0.6.0 \
                      --build-arg INSTALL_TYPE=all \
                      --build-arg ENABLE_GPU=false \
                      --build-arg USE_LOCAL=true \
                      -t my-crawl4ai-image:custom .
                    ```
                * Purpose of `docker buildx`: A Docker CLI plugin that extends the `docker build` command with full support for BuildKit builder capabilities, including multi-architecture builds.
                * Explanation of `--platform`: Specifies the target platform(s) for the build (e.g., `linux/amd64`, `linux/arm64`).
                * Explanation of `--build-arg`: Passes build-time variables defined in the `Dockerfile` (see section 3.3).
            * 3.2.3.4. Running the Custom-Built Container
                * Basic Run: `docker run -d -p 11235:11235 --shm-size=1g --name my-crawl4ai-server my-crawl4ai-image:custom`
                * Run with LLM Support: `docker run -d -p 11235:11235 --env-file .llm.env --shm-size=1g --name my-crawl4ai-server my-crawl4ai-image:custom`
            * 3.2.3.5. Stopping the Container: (As above)

    * 3.3. **Dockerfile Parameters (`ARG` values)**
        * 3.3.1. `C4AI_VER`: (Default: `0.6.0`)
            * Role: Specifies the version of the `crawl4ai` library. Used for labeling the image and potentially for version-specific logic.
        * 3.3.2. `APP_HOME`: (Default: `/app`)
            * Role: Defines the working directory inside the Docker container where the application code and related files are stored and executed.
        * 3.3.3. `GITHUB_REPO`: (Default: `https://github.com/unclecode/crawl4ai.git`)
            * Role: The URL of the GitHub repository to clone if `USE_LOCAL` is set to `false`.
        * 3.3.4. `GITHUB_BRANCH`: (Default: `main`)
            * Role: The specific branch of the GitHub repository to clone if `USE_LOCAL` is `false`.
        * 3.3.5. `USE_LOCAL`: (Default: `true`)
            * Role: A boolean flag. If `true`, the `Dockerfile` installs `crawl4ai` from the local source code copied into `/tmp/project/` during the build context. If `false`, it clones the repository specified by `GITHUB_REPO` and `GITHUB_BRANCH`.
        * 3.3.6. `PYTHON_VERSION`: (Default: `3.12`)
            * Role: Specifies the Python version for the base image (e.g., `python:3.12-slim-bookworm`).
        * 3.3.7. `INSTALL_TYPE`: (Default: `default`)
            * Role: Controls which optional dependencies of `crawl4ai` are installed. Possible values: `default` (core), `pdf`, `torch`, `transformer`, `cosine`, `sync`, `all`.
        * 3.3.8. `ENABLE_GPU`: (Default: `false`)
            * Role: A boolean flag. If `true` and `TARGETARCH` is `amd64`, the `Dockerfile` attempts to install the NVIDIA CUDA toolkit for GPU acceleration.
        * 3.3.9. `TARGETARCH`:
            * Role: An automatic build argument provided by Docker, indicating the target architecture of the build (e.g., `amd64`, `arm64`). Used for conditional logic in the `Dockerfile`, such as installing platform-specific optimized libraries or CUDA for `amd64`.

    * 3.4. **Server Configuration (`config.yml`)**
        * 3.4.1. Location: The server loads its configuration from `/app/config.yml` inside the container by default. This path is relative to `APP_HOME`.
        * 3.4.2. Structure Overview (based on `deploy/docker/config.yml`):
            * `app`: General application settings.
                * `title (str)`: API title (e.g., "Crawl4AI API").
                * `version (str)`: API version (e.g., "1.0.0").
                * `host (str)`: Host address for the server to bind to (e.g., "0.0.0.0").
                * `port (int)`: Port for the server to listen on (e.g., 11234, though Docker usually maps to 11235).
                * `reload (bool)`: Enable/disable auto-reload for development (default: `false`).
                * `workers (int)`: Number of worker processes (default: 1).
                * `timeout_keep_alive (int)`: Keep-alive timeout in seconds (default: 300).
            * `llm`: Default LLM configuration.
                * `provider (str)`: Default LLM provider string (e.g., "openai/gpt-4o-mini").
                * `api_key_env (str)`: Environment variable name to read the API key from (e.g., "OPENAI_API_KEY").
                * `api_key (Optional[str])`: Directly pass API key (overrides `api_key_env`).
            * `redis`: Redis connection details.
                * `host (str)`: Redis host (e.g., "localhost").
                * `port (int)`: Redis port (e.g., 6379).
                * `db (int)`: Redis database number (e.g., 0).
                * `password (str)`: Redis password (default: "").
                * `ssl (bool)`: Enable SSL for Redis connection (default: `false`).
                * `ssl_cert_reqs (Optional[str])`: SSL certificate requirements (e.g., "none", "optional", "required").
                * `ssl_ca_certs (Optional[str])`: Path to CA certificate file.
                * `ssl_certfile (Optional[str])`: Path to SSL certificate file.
                * `ssl_keyfile (Optional[str])`: Path to SSL key file.
            * `rate_limiting`: Configuration for API rate limits.
                * `enabled (bool)`: Enable/disable rate limiting (default: `true`).
                * `default_limit (str)`: Default rate limit (e.g., "1000/minute").
                * `trusted_proxies (List[str])`: List of trusted proxy IP addresses.
                * `storage_uri (str)`: Storage URI for rate limit counters (e.g., "memory://", "redis://localhost:6379").
            * `security`: Security-related settings.
                * `enabled (bool)`: Master switch for security features (default: `false`).
                * `jwt_enabled (bool)`: Enable/disable JWT authentication (default: `false`).
                * `https_redirect (bool)`: Enable/disable HTTPS redirection (default: `false`).
                * `trusted_hosts (List[str])`: List of allowed host headers (e.g., `["*"]` or specific domains).
                * `headers (Dict[str, str])`: Default security headers to add to responses (e.g., `X-Content-Type-Options`, `Content-Security-Policy`).
            * `crawler`: Default crawler behavior.
                * `base_config (Dict[str, Any])`: Base parameters for `CrawlerRunConfig`.
                    * `simulate_user (bool)`: (default: `true`).
                * `memory_threshold_percent (float)`: Memory usage threshold for adaptive dispatcher (default: `95.0`).
                * `rate_limiter (Dict[str, Any])`: Configuration for the internal rate limiter for crawling.
                    * `enabled (bool)`: (default: `true`).
                    * `base_delay (List[float, float])`: Min/max delay range (e.g., `[1.0, 2.0]`).
                * `timeouts (Dict[str, float])`: Timeouts for different crawler operations.
                    * `stream_init (float)`: Timeout for stream initialization (default: `30.0`).
                    * `batch_process (float)`: Timeout for batch processing (default: `300.0`).
                * `pool (Dict[str, Any])`: Browser pool settings.
                    * `max_pages (int)`: Max concurrent browser pages (default: `40`).
                    * `idle_ttl_sec (int)`: Time-to-live for idle crawlers in seconds (default: `1800`).
                * `browser (Dict[str, Any])`: Default `BrowserConfig` parameters.
                    * `kwargs (Dict[str, Any])`: Keyword arguments for `BrowserConfig`.
                        * `headless (bool)`: (default: `true`).
                        * `text_mode (bool)`: (default: `true`).
                    * `extra_args (List[str])`: List of additional browser launch arguments (e.g., `"--no-sandbox"`).
            * `logging`: Logging configuration.
                * `level (str)`: Logging level (e.g., "INFO", "DEBUG").
                * `format (str)`: Log message format string.
            * `observability`: Observability settings.
                * `prometheus (Dict[str, Any])`: Prometheus metrics configuration.
                    * `enabled (bool)`: (default: `true`).
                    * `endpoint (str)`: Metrics endpoint path (e.g., "/metrics").
                * `health_check (Dict[str, str])`: Health check endpoint configuration.
                    * `endpoint (str)`: Health check endpoint path (e.g., "/health").
        * 3.4.3. JWT Authentication
            * Enabling: Set `security.enabled: true` and `security.jwt_enabled: true` in `config.yml`.
            * Secret Key: Configured via `security.jwt_secret_key`. This value can be overridden by the environment variable `JWT_SECRET_KEY`.
            * Algorithm: Configured via `security.jwt_algorithm` (default: `HS256`).
            * Token Expiry: Configured via `security.jwt_expire_minutes` (default: `30`).
            * Usage:
                * 1. Client obtains a token by sending a POST request to the `/token` endpoint with an email in the request body (e.g., `{"email": "user@example.com"}`). The email domain might be validated if configured.
                * 2. Client includes the received token in the `Authorization` header of subsequent requests to protected API endpoints: `Authorization: Bearer <your_jwt_token>`.
        * 3.4.4. Customizing `config.yml`
            * 3.4.4.1. Modifying Before Build:
                * Method: Edit the `deploy/docker/config.yml` file within the cloned `crawl4ai` repository before building the Docker image. This new configuration will be baked into the image.
            * 3.4.4.2. Runtime Mount:
                * Method: Mount a custom `config.yml` file from the host machine to `/app/config.yml` (or the path specified by `APP_HOME`) inside the running Docker container.
                * Example Command: `docker run -d -p 11235:11235 -v /path/on/host/my-config.yml:/app/config.yml --name crawl4ai-server unclecode/crawl4ai:latest`
        * 3.4.5. Key Configuration Recommendations
            * Security:
                * Enable JWT (`security.jwt_enabled: true`) if the server is exposed to untrusted networks.
                * Use a strong, unique `jwt_secret_key`.
                * Configure `security.trusted_hosts` to a specific list of allowed hostnames instead of `["*"]` for production.
                * If using a reverse proxy for SSL termination, ensure `https_redirect` is appropriately configured or disabled if the proxy handles it.
            * Resource Management:
                * Adjust `crawler.pool.max_pages` based on server resources to prevent overwhelming the system.
                * Tune `crawler.pool.idle_ttl_sec` to balance resource usage and responsiveness for pooled browser instances.
            * Monitoring:
                * Keep `observability.prometheus.enabled: true` for production monitoring via the `/metrics` endpoint.
                * Ensure the `/health` endpoint is accessible to health checking systems.
            * Performance:
                * Review and customize `crawler.browser.extra_args` for headless browser optimization (e.g., disabling GPU, sandbox if appropriate for your environment).
                * Set reasonable `crawler.timeouts` to prevent long-stalled crawls.

    * 3.5. **API Usage (Interacting with the Dockerized Server)**
        * 3.5.1. **Playground Interface**
            * Access URL: `http://localhost:11235/playground` (assuming default port mapping).
            * Purpose: An interactive web UI (Swagger UI/OpenAPI) allowing users to explore API endpoints, view schemas, construct requests, and test API calls directly from their browser.
        * 3.5.2. **Python SDK (`Crawl4aiDockerClient`)**
            * Class Name: `Crawl4aiDockerClient`
            * Location: (Typically imported as `from crawl4ai.docker_client import Crawl4aiDockerClient`) - Actual import might vary based on final library structure; refer to `docs/examples/docker_example.py` or `docs/examples/docker_python_sdk.py`.
            * Initialization:
                * Signature: `Crawl4aiDockerClient(base_url: str = "http://localhost:11235", api_token: Optional[str] = None, timeout: int = 300)`
                * Parameters:
                    * `base_url (str)`: The base URL of the Crawl4ai server. Default: `"http://localhost:11235"`.
                    * `api_token (Optional[str])`: JWT token for authentication if enabled on the server. Default: `None`.
                    * `timeout (int)`: Default timeout in seconds for HTTP requests to the server. Default: `300`.
            * Authentication (JWT):
                * Method: Pass the `api_token` during client initialization. The token can be obtained from the server's `/token` endpoint or other authentication mechanisms.
            * `crawl()` Method:
                * Signature (Conceptual, based on typical SDK patterns and server capabilities): `async def crawl(self, urls: Union[str, List[str]], browser_config: Optional[Dict] = None, crawler_config: Optional[Dict] = None, stream: bool = False) -> Union[List[Dict], AsyncGenerator[Dict, None]]`
                    *Note: SDK might take `BrowserConfig` and `CrawlerRunConfig` objects directly, which it then serializes.*
                * Key Parameters:
                    * `urls (Union[str, List[str]])`: A single URL string or a list of URL strings to crawl.
                    * `browser_config (Optional[Dict])`: A dictionary representing the `BrowserConfig` object, or a `BrowserConfig` instance itself.
                    * `crawler_config (Optional[Dict])`: A dictionary representing the `CrawlerRunConfig` object, or a `CrawlerRunConfig` instance itself.
                    * `stream (bool)`: If `True`, the method returns an async generator yielding individual `CrawlResult` dictionaries as they are processed by the server. If `False` (default), it returns a list containing all `CrawlResult` dictionaries after all URLs are processed.
                * Return Type: `List[Dict]` (for `stream=False`) or `AsyncGenerator[Dict, None]` (for `stream=True`), where each `Dict` represents a `CrawlResult`.
                * Streaming Behavior:
                    * `stream=True`: Allows processing of results incrementally, suitable for long crawl jobs or real-time data feeds.
                    * `stream=False`: Collects all results before returning, simpler for smaller batches.
            * `get_schema()` Method:
                * Signature: `async def get_schema(self) -> dict`
                * Return Type: `dict`.
                * Purpose: Fetches the JSON schemas for `BrowserConfig` and `CrawlerRunConfig` from the server's `/schema` endpoint. This helps in constructing valid configuration payloads.
        * 3.5.3. **JSON Request Schema for Configurations**
            * Structure: `{"type": "ClassName", "params": {...}}`
            * Purpose: This structure is used by the server (and expected by the Python SDK internally) to deserialize JSON payloads back into Pydantic configuration objects like `BrowserConfig`, `CrawlerRunConfig`, and their nested strategy objects (e.g., `LLMExtractionStrategy`, `PruningContentFilter`). The `type` field specifies the Python class name, and `params` holds the keyword arguments for its constructor.
            * Example (`BrowserConfig`):
                ```json
                {
                    "type": "BrowserConfig",
                    "params": {
                        "headless": true,
                        "browser_type": "chromium",
                        "viewport_width": 1920,
                        "viewport_height": 1080
                    }
                }
                ```
            * Example (`CrawlerRunConfig` with a nested `LLMExtractionStrategy`):
                ```json
                {
                    "type": "CrawlerRunConfig",
                    "params": {
                        "cache_mode": {"type": "CacheMode", "params": "BYPASS"},
                        "screenshot": false,
                        "extraction_strategy": {
                            "type": "LLMExtractionStrategy",
                            "params": {
                                "llm_config": {
                                    "type": "LLMConfig",
                                    "params": {"provider": "openai/gpt-4o-mini"}
                                },
                                "instruction": "Extract the main title and summary."
                            }
                        }
                    }
                }
                ```
        * 3.5.4. **REST API Examples**
            * `/crawl` Endpoint:
                * URL: `http://localhost:11235/crawl`
                * HTTP Method: `POST`
                * Payload Structure (`CrawlRequest` model from `deploy/docker/schemas.py`):
                    ```json
                    {
                        "urls": ["https://example.com"],
                        "browser_config": { // JSON representation of BrowserConfig
                            "type": "BrowserConfig",
                            "params": {"headless": true}
                        },
                        "crawler_config": { // JSON representation of CrawlerRunConfig
                            "type": "CrawlerRunConfig",
                            "params": {"screenshot": true}
                        }
                    }
                    ```
                * Response Structure: A JSON object, typically `{"success": true, "results": [CrawlResult, ...], "server_processing_time_s": float, ...}`.
            * `/crawl/stream` Endpoint:
                * URL: `http://localhost:11235/crawl/stream`
                * HTTP Method: `POST`
                * Payload Structure: Same as `/crawl` (`CrawlRequest` model).
                * Response Structure: Newline Delimited JSON (NDJSON, `application/x-ndjson`). Each line is a JSON string representing a `CrawlResult` object.
                    * Headers: Includes `Content-Type: application/x-ndjson` and `X-Stream-Status: active` while streaming, and a final JSON object `{"status": "completed"}`.

    * 3.6. **Additional API Endpoints (from `server.py`)**
        * 3.6.1. `/html`
            * Endpoint URL: `/html`
            * HTTP Method: `POST`
            * Purpose: Crawls the given URL, preprocesses its raw HTML content specifically for schema extraction purposes (e.g., by sanitizing and simplifying the structure), and returns the processed HTML.
            * Request Body (`HTMLRequest` from `deploy/docker/schemas.py`):
                * `url (str)`: The URL to fetch and process.
            * Response Structure (JSON):
                * `html (str)`: The preprocessed HTML string.
                * `url (str)`: The original URL requested.
                * `success (bool)`: Indicates if the operation was successful.
        * 3.6.2. `/screenshot`
            * Endpoint URL: `/screenshot`
            * HTTP Method: `POST`
            * Purpose: Captures a full-page PNG screenshot of the specified URL. Allows an optional delay before capture and an option to save the file server-side.
            * Request Body (`ScreenshotRequest` from `deploy/docker/schemas.py`):
                * `url (str)`: The URL to take a screenshot of.
                * `screenshot_wait_for (Optional[float])`: Seconds to wait before taking the screenshot. Default: `2.0`.
                * `output_path (Optional[str])`: If provided, the screenshot is saved to this path on the server, and the path is returned. Otherwise, the base64 encoded image is returned. Default: `None`.
            * Response Structure (JSON):
                * `success (bool)`: Indicates if the screenshot was successfully taken.
                * `screenshot (Optional[str])`: Base64 encoded PNG image data, if `output_path` was not provided.
                * `path (Optional[str])`: The absolute server-side path to the saved screenshot, if `output_path` was provided.
        * 3.6.3. `/pdf`
            * Endpoint URL: `/pdf`
            * HTTP Method: `POST`
            * Purpose: Generates a PDF document of the rendered content of the specified URL.
            * Request Body (`PDFRequest` from `deploy/docker/schemas.py`):
                * `url (str)`: The URL to convert to PDF.
                * `output_path (Optional[str])`: If provided, the PDF is saved to this path on the server, and the path is returned. Otherwise, the base64 encoded PDF data is returned. Default: `None`.
            * Response Structure (JSON):
                * `success (bool)`: Indicates if the PDF generation was successful.
                * `pdf (Optional[str])`: Base64 encoded PDF data, if `output_path` was not provided.
                * `path (Optional[str])`: The absolute server-side path to the saved PDF, if `output_path` was provided.
        * 3.6.4. `/execute_js`
            * Endpoint URL: `/execute_js`
            * HTTP Method: `POST`
            * Purpose: Executes a list of JavaScript snippets on the specified URL in the browser context and returns the full `CrawlResult` object, including any modifications or data retrieved by the scripts.
            * Request Body (`JSEndpointRequest` from `deploy/docker/schemas.py`):
                * `url (str)`: The URL on which to execute the JavaScript.
                * `scripts (List[str])`: A list of JavaScript code snippets to execute sequentially. Each script should be an expression that returns a value.
            * Response Structure (JSON): A `CrawlResult` object (serialized to a dictionary) containing the state of the page after JS execution, including `js_execution_result`.
        * 3.6.5. `/ask` (Endpoint defined as `/ask` in `server.py`)
            * Endpoint URL: `/ask`
            * HTTP Method: `GET`
            * Purpose: Retrieves context about the Crawl4ai library itself, either code snippets or documentation sections, filtered by a query. This is designed for AI assistants or RAG systems needing information about Crawl4ai.
            * Parameters (Query):
                * `context_type (str, default="all", enum=["code", "doc", "all"])`: Specifies whether to return "code", "doc", or "all" (both).
                * `query (Optional[str])`: A search query string used to filter relevant chunks using BM25 ranking. If `None`, returns all context of the specified type(s).
                * `score_ratio (float, default=0.5, ge=0.0, le=1.0)`: The minimum score (as a fraction of the maximum possible score for the query) for a chunk to be included in the results.
                * `max_results (int, default=20, ge=1)`: The maximum number of result chunks to return.
            * Response Structure (JSON):
                * If `query` is provided:
                    * `code_results (Optional[List[Dict[str, Union[str, float]]]])`: A list of dictionaries, where each dictionary contains `{"text": "code_chunk...", "score": bm25_score}`. Present if `context_type` is "code" or "all".
                    * `doc_results (Optional[List[Dict[str, Union[str, float]]]])`: A list of dictionaries, where each dictionary contains `{"text": "doc_chunk...", "score": bm25_score}`. Present if `context_type` is "doc" or "all".
                * If `query` is not provided:
                    * `code_context (Optional[str])`: The full concatenated code context as a single string. Present if `context_type` is "code" or "all".
                    * `doc_context (Optional[str])`: The full concatenated documentation context as a single string. Present if `context_type` is "doc" or "all".

    * 3.7. **MCP (Model Context Protocol) Support**
        * 3.7.1. Explanation of MCP:
            * Purpose: The Model Context Protocol (MCP) is a standardized way for AI models (like Anthropic's Claude with Code Interpreter capabilities) to discover and interact with external tools and data sources. Crawl4ai's MCP server exposes its functionalities as tools that an MCP-compatible AI can use.
        * 3.7.2. Connection Endpoints (defined in `mcp_bridge.py` and attached to FastAPI app):
            * `/mcp/sse`: Server-Sent Events (SSE) endpoint for MCP communication.
            * `/mcp/ws`: WebSocket endpoint for MCP communication.
            * `/mcp/messages`: Endpoint for clients to POST messages in the SSE transport.
        * 3.7.3. Usage with Claude Code Example:
            * Command: `claude mcp add -t sse c4ai-sse http://localhost:11235/mcp/sse`
            * Purpose: This command (specific to the Claude Code CLI) registers the Crawl4ai MCP server as a tool provider named `c4ai-sse` using the SSE transport. The AI can then discover and invoke tools from this source.
        * 3.7.4. List of Available MCP Tools (defined by `@mcp_tool` decorators in `server.py`):
            * `md`: Fetches Markdown for a URL.
                * Parameters (derived from `get_markdown` function signature): `url (str)`, `filter_type (FilterType)`, `query (Optional[str])`, `cache (Optional[str])`.
            * `html`: Generates preprocessed HTML for a URL.
                * Parameters (derived from `generate_html` function signature): `url (str)`.
            * `screenshot`: Generates a screenshot of a URL.
                * Parameters (derived from `generate_screenshot` function signature): `url (str)`, `screenshot_wait_for (Optional[float])`, `output_path (Optional[str])`.
            * `pdf`: Generates a PDF of a URL.
                * Parameters (derived from `generate_pdf` function signature): `url (str)`, `output_path (Optional[str])`.
            * `execute_js`: Executes JavaScript on a URL.
                * Parameters (derived from `execute_js` function signature): `url (str)`, `scripts (List[str])`.
            * `crawl`: Performs a full crawl operation.
                * Parameters (derived from `crawl` function signature): `urls (List[str])`, `browser_config (Optional[Dict])`, `crawler_config (Optional[Dict])`.
            * `ask`: Retrieves library context.
                * Parameters (derived from `get_context` function signature): `context_type (str)`, `query (Optional[str])`, `score_ratio (float)`, `max_results (int)`.
        * 3.7.5. Testing MCP Connections:
            * Method: Use an MCP client tool (e.g., `claude mcp call c4ai-sse.md url=https://example.com`) to invoke a tool and verify the response.
        * 3.7.6. Accessing MCP Schemas:
            * Endpoint URL: `/mcp/schema`
            * Purpose: Returns a JSON response detailing all registered MCP tools, including their names, descriptions, and input schemas, enabling clients to understand how to use them.

    * 3.8. **Metrics & Monitoring Endpoints**
        * 3.8.1. `/health`
            * Purpose: Provides a basic health check for the server, indicating if it's running and responsive.
            * Response Structure (JSON from `server.py`): `{"status": "ok", "timestamp": float, "version": str}` (where version is `__version__` from `server.py`).
            * Configuration: Path configurable via `observability.health_check.endpoint` in `config.yml`.
        * 3.8.2. `/metrics`
            * Purpose: Exposes application metrics in a format compatible with Prometheus for monitoring and alerting.
            * Response Format: Prometheus text format.
            * Configuration: Enabled via `observability.prometheus.enabled: true` and endpoint path via `observability.prometheus.endpoint` in `config.yml`.

    * 3.9. **Underlying Server Logic (`server.py` - High-Level Understanding)**
        * 3.9.1. FastAPI Application:
            * Framework: The server is built using the FastAPI Python web framework for creating APIs.
        * 3.9.2. `crawler_pool` (`CrawlerPool` from `deploy.docker.crawler_pool`):
            * Role: Manages a pool of `AsyncWebCrawler` instances to reuse browser resources efficiently.
            * `get_crawler(BrowserConfig)`: Fetches an existing idle crawler compatible with the `BrowserConfig` or creates a new one if none are available or compatible.
            * `close_all()`: Iterates through all pooled crawlers and closes them.
            * `janitor()`: An `asyncio.Task` that runs periodically to close and remove crawler instances that have been idle for longer than `crawler.pool.idle_ttl_sec` (configured in `config.yml`).
        * 3.9.3. Global Page Semaphore (`GLOBAL_SEM`):
            * Type: `asyncio.Semaphore`.
            * Purpose: A global semaphore that limits the total number of concurrently open browser pages across all `AsyncWebCrawler` instances managed by the server. This acts as a hard cap to prevent excessive resource consumption.
            * Configuration: The maximum number of concurrent pages is set by `crawler.pool.max_pages` in `config.yml` (default: `30` in `server.py`, but `40` in `config.yml`). The `AsyncWebCrawler.arun` method acquires this semaphore.
        * 3.9.4. Job Router (`init_job_router` from `deploy.docker.job`):
            * Role: Manages asynchronous, long-running tasks, particularly for the `/crawl` (non-streaming batch) endpoint.
            * Mechanism: Uses Redis (configured in `config.yml`) as a backend for task queuing (storing task metadata like status, creation time, URL, result, error) and status tracking.
            * User Interaction: When a job is submitted to an endpoint using this router (e.g., `/crawl/job`), a `task_id` is returned. The client then polls an endpoint like `/task/{task_id}` to get the status and eventual result or error.
        * 3.9.5. Rate Limiting Middleware:
            * Implementation: Uses the `slowapi` library, integrated with FastAPI.
            * Purpose: To protect the server from abuse by limiting the number of requests an IP address can make within a specified time window.
            * Configuration: Settings like `enabled`, `default_limit`, `storage_uri` (e.g., `memory://` or `redis://...`) are managed in the `rate_limiting` section of `config.yml`.
        * 3.9.6. Security Middleware:
            * Implementations: `HTTPSRedirectMiddleware` and `TrustedHostMiddleware` from FastAPI, plus custom logic for adding security headers.
            * Purpose:
                * `HTTPSRedirectMiddleware`: Redirects HTTP requests to HTTPS if `security.https_redirect` is true.
                * `TrustedHostMiddleware`: Ensures requests are only served if their `Host` header matches an entry in `security.trusted_hosts`.
                * Custom header logic: Adds HTTP security headers like `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Strict-Transport-Security` to all responses if `security.enabled` is true. These are defined in `security.headers` in `config.yml`.
        * 3.9.7. API Request Mapping:
            * Request Models: Pydantic models defined in `deploy/docker/schemas.py` (e.g., `CrawlRequest`, `MarkdownRequest`, `HTMLRequest`, `ScreenshotRequest`, `PDFRequest`, `JSEndpointRequest`, `TokenRequest`, `RawCode`) define the expected JSON structure for incoming API request bodies.
            * Endpoint Logic: Functions decorated with `@app.post(...)`, `@app.get(...)`, etc., in `server.py` handle incoming HTTP requests. These functions use FastAPI's dependency injection to parse and validate request bodies against the Pydantic models.
            * `AsyncWebCrawler` Interaction:
                * The parameters from the parsed request models (e.g., `CrawlRequest.urls`, `CrawlRequest.browser_config`, `CrawlRequest.crawler_config`) are used.
                * `BrowserConfig` and `CrawlerRunConfig` objects are created by calling their respective `.load()` class methods with the dictionary payloads received in the request (e.g., `BrowserConfig.load(crawl_request.browser_config)`).
                * These configuration objects are then passed to an `AsyncWebCrawler` instance obtained from the `crawler_pool`, typically to its `arun()` (for single URL or when JS execution context is critical) or `arun_many()` (for batch processing of multiple URLs) methods.
            * Result Serialization: The `CrawlResult` objects (or lists/generators of them) returned by the `AsyncWebCrawler` are usually serialized to JSON using their `.model_dump()` method before being included in the HTTP response. For streaming endpoints, each `CrawlResult` is serialized and sent as a separate NDJSON line.

## 4. Version Numbering Scheme

    * 4.1. **Standard Versioning (`MAJOR.MINOR.PATCH`)**
        * `MAJOR`: Incremented when incompatible API changes are made.
        * `MINOR`: Incremented when functionality is added in a backward-compatible manner.
        * `PATCH`: Incremented for backward-compatible bug fixes.
    * 4.2. **Pre-release Suffixes**
        * `devN`: (e.g., `0.6.0.dev1`) Development release. These are typically unstable and used for internal testing or early feedback on new, unrefined features.
        * `aN`: (e.g., `0.6.0a1`) Alpha release. Indicates an early preview of a new version, potentially unstable, and APIs might still change.
        * `bN`: (e.g., `0.6.0b1`) Beta release. Generally feature-complete for the targeted minor or major version but may still contain bugs. APIs are mostly stable at this point.
        * `rcN`: (e.g., `0.6.0rc1`) Release Candidate. A version that is potentially the final release, undergoing final testing to catch critical bugs before official release.
```

## Content (Reasoning)

Okay, I'm ready to generate the "Reasoning & Problem-Solving Framework" document for the `deployment` component of `crawl4ai`, based on the outline you provided and the code/documentation context from our previous interaction.

```markdown
# Detailed Outline for crawl4ai - deployment Component

**Target Document Type:** reasoning
**Target Output Filename Suggestion:** `llm_reasoning_deployment.md`
**Library Version Context:** 0.6.0
**Outline Generation Date:** 2025-05-24
---

## 1. Introduction to Crawl4ai Deployment

This guide focuses on deploying and configuring `crawl4ai`, whether you're using it as a simple Python library or as a robust Dockerized server. Understanding the different deployment strategies will help you choose the best approach for your specific needs, from quick local scripts to scalable, API-driven crawling services.

*   1.1. Why Different Deployment Strategies Matter
    *   1.1.1. Explaining the trade-offs: Library vs. Server (Docker) mode.
        *   **Library Mode:**
            *   **Pros:** Simplest to get started with for Python developers, direct integration into existing Python projects, easier debugging of Python-specific logic.
            *   **Cons:** Requires Python environment setup on every machine, can be harder to manage dependencies for larger teams or across different OS, resource management (browsers, memory) is directly tied to the script's host.
            *   **Why choose it?** Ideal for individual developers, small scripts, quick prototyping, or when `crawl4ai` is a component within a larger Python application.
        *   **Server (Docker) Mode:**
            *   **Pros:** Consistent environment (Docker handles dependencies), easy to scale, API-first (accessible from any language), better resource isolation and management, simplified deployment to cloud or on-premise servers.
            *   **Cons:** Requires Docker knowledge, slightly more setup initially, debugging might involve looking at container logs in addition to application logs.
            *   **Why choose it?** Best for team collaboration, production deployments, providing crawling as a service, language-agnostic access, or when you need robust, isolated browser instances.
    *   1.1.2. When to choose simple library installation.
        *   Choose simple library installation when:
            *   You are primarily working in a Python environment.
            *   You need to quickly integrate crawling into an existing Python script or application.
            *   Your deployment target is a machine where you can easily manage Python environments and Playwright browser installations.
            *   You are prototyping or working on a small-scale project.
    *   1.1.3. When a Dockerized server deployment is beneficial (scalability, isolation, API access).
        *   Opt for a Dockerized server when:
            *   You need a consistent, reproducible crawling environment across different machines or team members.
            *   You plan to offer crawling capabilities as an API to other services or applications (potentially written in different languages).
            *   You require better resource isolation for browser instances to prevent them from impacting other processes on the host machine.
            *   You anticipate needing to scale your crawling operations up or down based on demand.
            *   You are deploying to a cloud environment or a server where Docker is the preferred deployment method.

*   1.2. Overview of Installation Paths
    *   1.2.1. Quick guide to choosing your installation path based on needs.
        *   **For local Python development/scripting:** Start with "Core Library Installation." Add "Advanced Library Installation" if you need features like local ML model inference.
        *   **For a standalone, API-accessible server:** Jump to "Docker Deployment." You can choose between pre-built images (easiest), Docker Compose (good for managing related services like Redis), or manual builds (for full control).
    *   1.2.2. What this guide will cover for each path.
        *   This guide will provide step-by-step instructions, explanations of "why" certain steps are necessary, best practices, and troubleshooting tips for both library installation and the various Docker deployment options.

## 2. Core Library Installation & Usage

This section details how to get the `crawl4ai` library up and running directly in your Python environment.

*   2.1. Understanding the Basic Installation
    *   2.1.1. **How-to:** Installing the core `crawl4ai` library.
        *   **Command:**
            ```bash
            pip install crawl4ai
            ```
        *   **What core functionalities this provides:**
            *   The `AsyncWebCrawler` class and its associated configuration objects (`BrowserConfig`, `CrawlerRunConfig`).
            *   Core scraping capabilities (HTML, Markdown, links, media).
            *   Basic content processing and filtering.
            *   Support for Playwright-driven browser automation.
            *   The `crawl4ai-setup` and `crawl4ai-doctor` CLI tools.
    *   2.1.2. The Importance of Post-Installation Setup (`crawl4ai-setup`)
        *   **Why `crawl4ai-setup` is crucial:** `crawl4ai` relies on Playwright for browser automation. Playwright, in turn, needs browser executables (like Chromium, Firefox, WebKit) to be downloaded and installed in a location it can find. `crawl4ai-setup` automates this process.
        *   **What it does:**
            *   Invokes Playwright's browser installation mechanism (e.g., `playwright install --with-deps chromium`).
            *   Performs OS-specific checks to ensure necessary libraries or dependencies for running headless browsers are present (especially important on Linux).
            *   Sets up the local Crawl4ai home directory structure (e.g., `~/.crawl4ai/cache`).
        *   **Troubleshooting common `crawl4ai-setup` issues:**
            *   **Permission errors:** Ensure you have write permissions to the Playwright browser installation directory (often in your user's home directory or a system-wide location if installing as root).
            *   **Network issues:** Browser downloads can be large; ensure a stable internet connection. Proxies might interfere if not configured correctly for Playwright.
            *   **Missing OS dependencies (Linux):** The script attempts to guide you, but you might need to manually install packages like `libnss3`, `libatk1.0-0`, etc.
        *   *Code Example: Running `crawl4ai-setup` and interpreting its output.*
            ```bash
            crawl4ai-setup
            ```
            **Expected Output (Success):**
            ```
            [INIT] Running post-installation setup...
            [SETUP] Playwright browser installation complete.
            [COMPLETE] Post-installation setup completed!
            ```
            **Potential Issue Output:**
            ```
            [ERROR] Failed to install Playwright browsers. Please run 'playwright install --with-deps' manually.
            ```
    *   2.1.3. Diagnosing Your Environment with `crawl4ai-doctor`
        *   **When and why to use `crawl4ai-doctor`:** Run this command if you encounter issues after installation, or if crawls are failing unexpectedly. It performs a series of checks to verify that your Python environment, Playwright installation, and browser executables are correctly set up and accessible.
        *   **Interpreting `crawl4ai-doctor` output for common problems:**
            *   It will check Python version compatibility.
            *   It verifies if Playwright is installed and if browsers can be launched.
            *   It might suggest solutions for common issues it detects.
        *   *Code Example: Running `crawl4ai-doctor` and typical successful/problematic outputs.*
            ```bash
            crawl4ai-doctor
            ```
            **Expected Output (Success):**
            ```
            [INIT] Running Crawl4ai health check...
            [INFO] Python version: 3.X.X
            [INFO] Playwright version: X.Y.Z
            [TEST] Testing crawling capabilities...
            [COMPLETE] âœ… Crawling test passed!
            Crawl4ai doctor check completed. All systems operational.
            ```
            **Potential Issue Output:**
            ```
            [ERROR] âŒ Test failed: Could not launch browser. Ensure Playwright browsers are installed (run 'crawl4ai-setup' or 'playwright install --with-deps chromium').
            ```
    *   2.1.4. Verifying Your Basic Installation: Your First Simple Crawl
        *   **Step-by-step guide:**
            1.  Create a new Python file (e.g., `test_crawl.py`).
            2.  Import necessary classes: `AsyncWebCrawler`, `BrowserConfig`, `CrawlerRunConfig`.
            3.  Write an `async` function.
            4.  Inside the function, create a `BrowserConfig` instance (defaults are usually fine for a first test).
            5.  Create an `AsyncWebCrawler` instance, passing the `BrowserConfig`. Use an `async with` statement for proper resource management.
            6.  Create a `CrawlerRunConfig` instance (again, defaults are fine).
            7.  Call `crawler.arun(url="https://example.com", config=run_config)`.
            8.  Print a part of the result, e.g., `result.markdown[:300]`.
            9.  Use `asyncio.run()` to execute your `async` function.
        *   **Expected output:** You should see the first 300 characters of the Markdown content extracted from `example.com`.
        *   **How to confirm success:** If the script runs without errors and prints Markdown content, your basic installation is working.
        *   *Code Example: A minimal Python script to crawl `example.com`.*
            ```python
            import asyncio
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

            async def main():
                browser_cfg = BrowserConfig(headless=True) # Keep headless for non-UI environments
                run_cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS) # Bypass cache for a fresh fetch

                async with AsyncWebCrawler(config=browser_cfg) as crawler:
                    print("Attempting to crawl https://example.com...")
                    result = await crawler.arun(url="https://example.com", config=run_cfg)
                    if result.success:
                        print("Crawl successful!")
                        print("Markdown (first 300 chars):")
                        if result.markdown:
                            print(result.markdown.raw_markdown[:300])
                        else:
                            print("No markdown content generated.")
                    else:
                        print(f"Crawl failed: {result.error_message}")

            if __name__ == "__main__":
                asyncio.run(main())
            ```

*   2.2. Advanced Library Installation: Extending Functionality
    *   2.2.1. When to Consider Optional Features
        *   **Identifying use cases:**
            *   **Local Machine Learning/NLP tasks:** If you plan to use features like `CosineSimilarityFilter`, advanced `LLMContentFilter` modes that might leverage local sentence transformers, or other AI-driven text processing directly within your Python script without relying on an external LLM API for everything.
            *   **PyTorch-dependent features:** Some advanced filters or future AI integrations might specifically require PyTorch.
            *   **Hugging Face Transformers:** If you intend to use models directly from the Hugging Face Hub for tasks like summarization, classification, or custom embedding generation within your Crawl4ai workflow.
        *   **Understanding the additional capabilities:** These extras typically bring in libraries like `torch`, `transformers`, `scikit-learn`, and `nltk`, enabling more sophisticated local data processing and AI model inference.
    *   2.2.2. **How-to:** Installing Optional Extras
        *   **Explaining `crawl4ai[torch]`:**
            *   Installs `torch` and related dependencies.
            *   **Why:** Necessary for features that perform local neural network inference, such as certain embedding models or advanced NLP tasks that are PyTorch-based.
        *   **Explaining `crawl4ai[transformer]`:**
            *   Installs `transformers` (from Hugging Face) and `tokenizers`.
            *   **Why:** Enables the use of a wide range of pre-trained transformer models for tasks like text generation, summarization, and classification directly within Crawl4ai, often in conjunction with `torch`.
        *   **Explaining `crawl4ai[all]`:**
            *   Installs all optional dependencies, including `torch`, `transformers`, `nltk`, `scikit-learn`, `PyPDF2`, etc.
            *   **When to use:** If you anticipate needing a broad range of features and don't mind a larger installation footprint. Convenient for development environments.
            *   **Potential downsides:** Significantly larger installation size and more dependencies to manage, which might increase the chance of conflicts in complex environments.
        *   *Code Example: `pip install crawl4ai[torch]` and `pip install crawl4ai[all]`.*
            ```bash
            # For PyTorch related features
            pip install crawl4ai[torch]

            # For Hugging Face Transformers related features
            pip install crawl4ai[transformer]

            # To install all optional features
            pip install crawl4ai[all]
            ```
    *   2.2.3. Pre-fetching Models with `crawl4ai-download-models`
        *   **Why pre-fetch models:**
            *   **Offline use:** Allows features dependent on these models (e.g., certain embedding generators, classifiers) to run without an internet connection after initial download.
            *   **Faster startup:** Avoids download time on the first run of a script that uses these models.
            *   **Controlled environment:** Ensures you have the specific model versions Crawl4ai expects.
        *   **How to use the command:**
            ```bash
            crawl4ai-download-models
            ```
        *   **Where models are stored:** Typically in a cache directory managed by the underlying libraries (e.g., Hugging Face's cache, usually in `~/.cache/huggingface`). `crawl4ai-download-models` simply triggers the download process via these libraries.

## 3. Docker Deployment: Running Crawl4ai as a Server

Deploying Crawl4ai with Docker provides a consistent, isolated, and scalable environment, making it ideal for production or when offering crawling as an API service.

*   3.1. Why Deploy Crawl4ai with Docker?
    *   3.1.1. **Benefits:**
        *   **Isolation:** Browser instances and dependencies are contained within the Docker image, preventing conflicts with your host system or other applications.
        *   **Reproducibility:** Ensures that Crawl4ai runs the same way across different environments (development, staging, production).
        *   **Scalability:** Docker containers can be easily scaled up or down using orchestration tools like Kubernetes or Docker Swarm.
        *   **API-first Access:** Exposes Crawl4ai's functionality via a REST API, allowing applications written in any language to utilize its crawling capabilities.
    *   3.1.2. Common use cases for a Dockerized Crawl4ai server.
        *   Providing a centralized crawling service for multiple applications or teams.
        *   Integrating Crawl4ai into non-Python microservices architectures.
        *   Deploying to cloud platforms that favor containerized applications.
        *   Ensuring consistent browser behavior and dependency management for critical crawling tasks.

*   3.2. Prerequisites for Docker Deployment
    *   3.2.1. **Docker:** Ensure Docker Desktop (for Windows/Mac) or Docker Engine (for Linux) is installed and the Docker daemon is running.
        *   *Decision:* If you're new to Docker, visit the official Docker website for installation instructions specific to your OS.
    *   3.2.2. **Git:** Required if you plan to build the Docker image locally from the source code or use Docker Compose with a local repository clone.
        *   *Decision:* If you only intend to use pre-built images from Docker Hub, Git might not be strictly necessary on the deployment machine, but it's good practice for managing configurations.
    *   3.2.3. **RAM Requirements:** Web browsers, especially multiple concurrent instances, can be memory-intensive.
        *   **Guidance:**
            *   Minimum: At least 2GB RAM for the Docker container itself, plus additional RAM per concurrent browser page (e.g., 250-500MB per page, can vary).
            *   A common starting point for a server expected to handle a few concurrent crawls might be 4GB-8GB total allocated to Docker.
            *   Monitor your container's memory usage (`docker stats <container_id>`) and adjust resources as needed. Insufficient RAM can lead to browser crashes or slow performance.
            *   Remember to configure `--shm-size` (shared memory size) for your Docker run command (e.g., `--shm-size=1g`), as Chromium-based browsers heavily use it. The `docker-compose.yml` already includes a `/dev/shm` mount.

*   3.3. Docker Installation Options: A Decision Guide
    *   3.3.1. Option 1: Using Pre-built Images from Docker Hub
        *   **When to use:** This is the **easiest and quickest** way to get started if you don't need custom modifications to the Crawl4ai server image. It's ideal for standard use cases and trying out the server.
        *   **How-to:**
            *   **Pulling the image:**
                ```bash
                docker pull unclecode/crawl4ai:latest # For the latest stable release
                # Or, for a specific version (recommended for production):
                docker pull unclecode/crawl4ai:0.6.0
                ```
            *   **Understanding Docker Hub Tags:**
                *   `latest`: Points to the most recent stable release. Use with caution in production as it can change unexpectedly.
                *   Specific versions (e.g., `0.6.0`): Recommended for production to ensure reproducibility and avoid breaking changes.
                *   `0.6.0-rc1`: Release candidates, nearly stable.
                *   `dev`: Development builds from the `main` branch, potentially unstable.
                *   **Decision:** For production, always pin to a specific version tag. Use `latest` for quick tests or when you always want the newest features and are prepared for potential changes.
            *   **Setting up the environment:** Create a `.llm.env` file in your current directory to store API keys for LLM providers if you plan to use LLM-based extraction or filtering features.
                *   *Example `.llm.env` content:*
                    ```env
                    OPENAI_API_KEY=sk-yourOpenAiApiKeyxxxxxxxxxxxx
                    ANTHROPIC_API_KEY=sk-ant-yourAnthropicApiKeyxxxxxxxx
                    GEMINI_API_TOKEN=yourGoogleAIGeminiApiKeyxxxxxxxx
                    # Add other LLM provider keys as needed
                    ```
            *   **Running the container (Basic, no LLM support initially):**
                ```bash
                docker run -d -p 11235:11235 --name crawl4ai-server --shm-size=1g unclecode/crawl4ai:0.6.0
                ```
                *   `-d`: Run in detached mode (background).
                *   `-p 11235:11235`: Map port 11235 on your host to port 11235 in the container.
                *   `--name crawl4ai-server`: Assign a name to the container for easier management.
                *   `--shm-size=1g`: Allocate 1GB of shared memory, crucial for browser stability.
            *   **Running with LLM Support (mounting `.llm.env`):**
                ```bash
                docker run -d -p 11235:11235 --name crawl4ai-server --shm-size=1g --env-file .llm.env unclecode/crawl4ai:0.6.0
                ```
            *   **Stopping and removing the container:**
                ```bash
                docker stop crawl4ai-server
                docker rm crawl4ai-server
                ```
        *   **Best practices:**
            *   Always use specific version tags in production.
            *   Manage API keys securely using `.env` files or Docker secrets, not by hardcoding them into run commands or Dockerfiles.
    *   3.3.2. Option 2: Using Docker Compose
        *   **When to use:**
            *   When you want an easier way to manage the container's configuration and lifecycle.
            *   If you plan to run related services (e.g., a dedicated Redis instance for rate limiting or job queues) alongside Crawl4ai.
            *   If you need to make minor local customizations to the build process (like choosing `INSTALL_TYPE`) without managing complex `docker build` commands.
        *   **How-to:**
            1.  **Cloning the `crawl4ai` repository:**
                ```bash
                git clone https://github.com/unclecode/crawl4ai.git
                cd crawl4ai
                ```
            2.  **Setting up `.llm.env`:** Create this file in the root of the cloned repository if you need LLM support (see example above).
            3.  **Running with Pre-built Images (default in `docker-compose.yml`):**
                ```bash
                # This will use the image specified in docker-compose.yml (e.g., unclecode/crawl4ai:latest or a specific version)
                docker-compose up -d
                ```
                *   The `docker-compose.yml` file is pre-configured to pull official images and set up necessary volumes (like `/dev/shm`).
            4.  **Building Images Locally with Docker Compose:**
                *   **When this is preferred:** If you need to build the image with specific optional features (`INSTALL_TYPE`) or enable GPU support, and you prefer the `docker-compose` workflow.
                *   **How:** You'll modify the `docker-compose.yml` to use the `build` context or pass build arguments via the command line.
                    ```bash
                    # Example: Build with all features
                    docker-compose build --build-arg INSTALL_TYPE=all
                    docker-compose up -d

                    # Example: Build with GPU support (ensure Dockerfile supports this and host has NVIDIA drivers/toolkit)
                    # Potentially requires modifying docker-compose.yml to pass GPU runtime flags
                    docker-compose build --build-arg ENABLE_GPU=true
                    docker-compose up -d
                    ```
                    *Note: The provided `docker-compose.yml` already has a `build` section, so `docker-compose build` will use it. You can uncomment/modify `args` in the `build` section of `docker-compose.yml` as well.*
            5.  **Stopping services:**
                ```bash
                docker-compose down
                ```
        *   **Advantages:** Simplifies managing container configurations, volumes, and networks, especially if you add more services later.
    *   3.3.3. Option 3: Manual Local Build & Run
        *   **When to use:**
            *   When you need to make significant customizations to the `Dockerfile` itself.
            *   For development and testing of changes to the Crawl4ai server codebase.
            *   If you need to build for a specific architecture not readily available as a pre-built image variant (though `buildx` helps with this).
        *   **How-to:**
            1.  **Cloning the repository:**
                ```bash
                git clone https://github.com/unclecode/crawl4ai.git
                cd crawl4ai
                ```
            2.  **Setting up `.llm.env`:** Create this file in the root directory.
            3.  **Building with `docker buildx` (recommended for multi-arch):**
                *   **Understanding multi-arch builds:** `docker buildx` allows you to build images for multiple architectures (e.g., `linux/amd64` for typical Intel/AMD servers, `linux/arm64` for ARM-based servers like AWS Graviton or Raspberry Pi).
                *   **Passing build arguments:**
                    ```bash
                    # Example: Build for amd64 and arm64, with all features, and tag it
                    docker buildx build \
                      --platform linux/amd64,linux/arm64 \
                      --build-arg INSTALL_TYPE=all \
                      --build-arg ENABLE_GPU=false \
                      -t my-custom-crawl4ai:latest \
                      --push .  # Use --load to load into local Docker images instead of pushing
                    ```
                    *   Replace `--push` with `--load` if you want to use the image locally immediately.
            4.  **Running the locally built container:**
                ```bash
                docker run -d -p 11235:11235 --name my-crawl4ai-server --shm-size=1g --env-file .llm.env my-custom-crawl4ai:latest
                ```
            5.  **Stopping and removing the container:**
                ```bash
                docker stop my-crawl4ai-server
                docker rm my-crawl4ai-server
                ```
        *   **Considerations:** This method gives you the most control but requires a deeper understanding of Docker image building. Build times can be longer, especially with `INSTALL_TYPE=all`.

*   3.4. Understanding Dockerfile Build Parameters (`ARG` values)
    *   These arguments allow you to customize the Docker image during the build process (`docker build` or `docker-compose build`).
    *   `C4AI_VER`:
        *   **Role:** Specifies the version of Crawl4ai to install if not using local source. It's used in the Dockerfile if `USE_LOCAL=false`.
        *   **Why change:** You might want to build an image based on a specific older version or a development tag.
    *   `APP_HOME`:
        *   **Role:** Defines the working directory inside the container (e.g., `/app`).
        *   **Why change:** Rarely needed unless you have specific path requirements for integrations.
    *   `GITHUB_REPO`, `GITHUB_BRANCH`:
        *   **Role:** Used when `USE_LOCAL=false` to clone Crawl4ai from a specific GitHub repository and branch.
        *   **Why change:** To build from your own fork, a feature branch, or a specific commit for testing.
    *   `USE_LOCAL`:
        *   **Role:** A boolean (`true` or `false`). If `true`, the Docker build uses the local source code from the directory where the `Dockerfile` resides (copied via `COPY . /tmp/project/`). If `false`, it clones from `GITHUB_REPO` and `GITHUB_BRANCH`.
        *   **Why change:** Set to `true` when developing and wanting to build an image with your local changes. Set to `false` for CI/CD or building from a canonical Git source.
    *   `PYTHON_VERSION`:
        *   **Role:** Specifies the base Python slim image version (e.g., `3.12`).
        *   **Why change:** If you need to ensure compatibility with a specific Python version for your dependencies or environment.
    *   `INSTALL_TYPE`:
        *   **Role:** Controls which optional dependencies of `crawl4ai` are installed. Options include `default` (core), `all` (all extras), `torch`, `transformer`.
        *   **Impact:**
            *   `default`: Smallest image, fewest features.
            *   `all`: Largest image, all features (including ML/NLP capabilities).
            *   `torch`/`transformer`: Intermediate size, specific ML/NLP capabilities.
        *   **Why change:** To tailor the image size and included features to your specific needs, avoiding unnecessary bloat.
    *   `ENABLE_GPU`:
        *   **Role:** A boolean (`true` or `false`). If `true`, the Dockerfile attempts to install GPU-related dependencies (e.g., CUDA toolkit if `TARGETARCH` is compatible).
        *   **Why change:** Set to `true` if you have a compatible GPU on your Docker host and want to accelerate ML tasks (like local LLM inference or embeddings) inside the container. Requires appropriate Docker runtime configuration (e.g., `--gpus all`).
    *   `TARGETARCH`:
        *   **Role:** Automatically set by Docker Buildx based on the `--platform` flag. It informs the Dockerfile about the target architecture (e.g., `amd64`, `arm64`) so it can install architecture-specific dependencies (like OpenMP for AMD64 or OpenBLAS for ARM64, or CUDA for NVIDIA GPUs on compatible architectures).
        *   **Why be aware:** Essential for understanding multi-arch builds and ensuring correct dependencies are installed for the target platform.
    *   *Guidance: Best practices for setting these arguments:*
        *   For development with local changes: `USE_LOCAL=true`.
        *   For minimal production image: `INSTALL_TYPE=default` (if no advanced features needed).
        *   For ML-heavy tasks on GPU hardware: `ENABLE_GPU=true`, `INSTALL_TYPE=all` (or `torch`/`transformer`).
        *   Always specify `C4AI_VER` or `GITHUB_BRANCH` explicitly for reproducible builds if not using `USE_LOCAL=true`.

*   3.5. Server Configuration (`config.yml`)
    The `config.yml` file (located at `/app/config.yml` inside the container, and `deploy/docker/config.yml` in the source) controls various aspects of the Crawl4ai server's behavior.
    *   3.5.1. Overview of `config.yml` Structure
        *   **`app` section:**
            *   **Purpose:** Configures the FastAPI/Uvicorn server.
            *   `host`, `port`: Network interface and port the server listens on.
            *   `workers`: Number of Uvicorn worker processes (for handling concurrent requests).
            *   **Reasoning:** Adjust `workers` based on your server's CPU cores and expected load. `0.0.0.0` for `host` makes it accessible externally.
        *   **`llm` section:**
            *   **Purpose:** Default settings for LLM integrations.
            *   `provider`: Default LLM provider/model (e.g., `openai/gpt-4o-mini`).
            *   `api_key_env`: The environment variable name from which to read the API key for the default provider (e.g., `OPENAI_API_KEY`).
            *   `api_key`: (Optional, discouraged) Directly embed an API key. It's better to use `api_key_env`.
            *   **Reasoning:** Centralizes default LLM settings. API keys should almost always be managed via environment variables for security.
        *   **`redis` section:**
            *   **Purpose:** Configuration for connecting to a Redis instance.
            *   Used for distributed rate limiting (if `rate_limiting.storage_uri` points to Redis) and potentially for the job queue in future versions.
            *   **Reasoning:** Essential for robust rate limiting in a scaled environment. If not using distributed features, default `memory://` for rate limiting is simpler.
        *   **`rate_limiting` section:**
            *   **Purpose:** Controls API rate limiting to prevent abuse.
            *   `enabled`: `true` or `false`.
            *   `default_limit`: E.g., "1000/minute".
            *   `storage_uri`: `memory://` (default, per-instance) or `redis://...` (for distributed).
            *   **Reasoning:** Always enable in production. Adjust limits based on expected traffic and capacity.
        *   **`security` section:**
            *   **Purpose:** Security-related settings.
            *   `enabled`: Master switch for security features below.
            *   `jwt_enabled`: Enable/disable JWT token authentication for API endpoints.
            *   `https_redirect`: If `true`, redirects HTTP to HTTPS (requires a reverse proxy like Nginx to handle SSL termination).
            *   `trusted_hosts`: List of allowed host headers. `["*"]` allows all, but be more specific in production.
            *   `headers`: Default security headers (X-Content-Type-Options, X-Frame-Options, CSP, HSTS).
            *   **Reasoning:** Crucial for production. `jwt_enabled` protects your API. `trusted_hosts` prevents host header attacks. Default headers provide good baseline security.
        *   **`crawler` section:**
            *   **Purpose:** Default behaviors for the crawler instances managed by the server.
            *   `base_config`: Default `CrawlerRunConfig` parameters if not specified in the API request.
            *   `memory_threshold_percent`: For `MemoryAdaptiveDispatcher`, at what system memory percentage to start throttling.
            *   `rate_limiter`: Default settings for the `RateLimiter` used by dispatchers.
            *   `pool`:
                *   `max_pages`: Corresponds to `GLOBAL_SEM` in `server.py`. Max concurrent browser pages server-wide.
                *   `idle_ttl_sec`: How long an idle browser instance remains in the pool before being cleaned up by the `janitor`.
            *   `browser`: Default `BrowserConfig` parameters.
                *   `kwargs`: Passed to Playwright's browser launch.
                *   `extra_args`: Additional browser command-line flags.
            *   **Reasoning:** Fine-tune these based on server resources and crawling needs. `max_pages` is critical for stability. `idle_ttl_sec` balances responsiveness with resource conservation.
        *   **`logging` section:**
            *   **Purpose:** Controls server-side logging.
            *   `level`: `INFO`, `DEBUG`, `WARNING`, `ERROR`.
            *   `format`: Log message format.
            *   **Reasoning:** Set to `DEBUG` for detailed troubleshooting, `INFO` for general production logs.
        *   **`observability` section:**
            *   **Purpose:** Endpoints for monitoring.
            *   `prometheus.endpoint`: Path for Prometheus metrics (e.g., `/metrics`).
            *   `health_check.endpoint`: Path for health checks (e.g., `/health`).
            *   **Reasoning:** Essential for production monitoring and integration with alerting systems.
    *   3.5.2. Securing Your Server: JWT Authentication
        *   **Why enable JWT authentication:** To protect your Crawl4ai server API from unauthorized access, especially if it's exposed to the internet or a shared network.
        *   **How to enable:** In `config.yml`, under the `security` section, set `jwt_enabled: true`.
        *   **Impact on API requests:** Most API endpoints (those decorated with `Depends(token_dep)`) will require an `Authorization: Bearer <your_jwt_token>` header.
        *   **Generating tokens via the `/token` endpoint:**
            *   The `/token` endpoint itself is *not* protected by JWT.
            *   You send a POST request with an email (currently, any email in a valid format works, but domain verification can be configured for more robust auth if needed for other systems; for Crawl4ai's purpose, the token is the primary gate).
            *   The server responds with an access token.
            *   *Example: Requesting a token with `curl`.*
                ```bash
                curl -X POST "http://localhost:11235/token" \
                     -H "Content-Type: application/json" \
                     -d '{"email": "user@example.com"}'
                ```
                **Expected Response:**
                ```json
                {
                  "email": "user@example.com",
                  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                  "token_type": "bearer"
                }
                ```
            *   *Example: Requesting a token with Python `requests`.*
                ```python
                import requests
                import json

                response = requests.post(
                    "http://localhost:11235/token",
                    json={"email": "user@example.com"}
                )
                if response.status_code == 200:
                    token_data = response.json()
                    print(f"Access Token: {token_data['access_token']}")
                else:
                    print(f"Error getting token: {response.text}")
                ```
    *   3.5.3. Customizing `config.yml`
        *   **Method 1: Modifying `config.yml` before building a local Docker image.**
            *   **How:** If you're building your own Docker image (Option 3.3.3 or Docker Compose with a local build context), you can directly edit the `deploy/docker/config.yml` file in your cloned repository before running `docker build` or `docker-compose build`.
            *   **Why:** Best if you want the custom configuration to be part of the image itself, ensuring consistency if you distribute or version the image.
        *   **Method 2: Mounting a custom `config.yml` at runtime.**
            *   **How:** Create your custom `config.yml` file on your Docker host machine. Then, when running the container, use a volume mount to replace the default `config.yml` inside the container.
            *   *Code Example:*
                ```bash
                # Assuming your custom config is at ./my-custom-config.yml on the host
                docker run -d -p 11235:11235 \
                  --name crawl4ai-server \
                  --shm-size=1g \
                  --env-file .llm.env \
                  -v "$(pwd)/my-custom-config.yml:/app/config.yml" \
                  unclecode/crawl4ai:0.6.0
                ```
            *   **Why:** Useful for quick configuration changes without rebuilding the image, or for managing configurations separately from the image, especially if you use pre-built images.
    *   3.5.4. Key Configuration Recommendations
        *   **Security:**
            *   **Always** enable `security.jwt_enabled: true` in production or shared environments.
            *   If using a reverse proxy for SSL, set `security.https_redirect: true`.
            *   Configure `security.trusted_hosts` to your server's domain(s) instead of `["*"]` in production.
            *   Review default security headers in `security.headers` and customize if needed for your security policies (e.g., a stricter Content Security Policy).
        *   **Resource Management:**
            *   Adjust `crawler.pool.max_pages` based on your server's RAM and CPU. Too high can lead to instability; too low can underutilize resources.
            *   Set `app.workers` (Uvicorn workers) typically to `(2 * CPU_CORES) + 1` as a starting point, but benchmark for your specific workload.
            *   Tune `crawler.pool.idle_ttl_sec` to balance between keeping browser instances warm (lower TTL) and conserving resources (higher TTL).
        *   **Monitoring:**
            *   Ensure `observability.prometheus.enabled: true` if you use Prometheus.
            *   Integrate the `observability.health_check.endpoint` into your load balancer or container orchestrator health checks.
        *   **Performance:**
            *   For `rate_limiting`, use a Redis backend (`storage_uri: redis://...`) if you have multiple server instances behind a load balancer to share rate limit state. For a single instance, `memory://` is fine.
            *   Adjust `rate_limiting.default_limit` to a reasonable value that protects your server and downstream services without unduly restricting legitimate users.

*   3.6. Interacting with the Dockerized Crawl4ai Server
    *   3.6.1. The Playground Interface (`/playground`)
        *   **How-to:** Open your web browser and navigate to `http://localhost:11235/playground` (or your server's address and port).
        *   **Purpose:**
            *   Provides an interactive UI (Swagger/OpenAPI) to explore all available API endpoints.
            *   Allows you to test API calls directly from your browser.
            *   Shows request and response schemas, making it easy to understand payload structures.
            *   Helps in generating example request payloads for your own client applications.
        *   **Key features to explore:**
            *   Expand each endpoint to see its parameters, request body schema, and possible responses.
            *   Use the "Try it out" button to send test requests.
            *   Examine the "Schemas" section at the bottom to understand the structure of objects like `CrawlRequest`, `BrowserConfig`, `CrawlerRunConfig`, and `CrawlResult`.
    *   3.6.2. Using the Python SDK (`Crawl4aiDockerClient`)
        *   **How-to:**
            ```python
            from crawl4ai.docker_client import Crawl4aiDockerClient
            import asyncio

            client = Crawl4aiDockerClient(base_url="http://localhost:11235")

            async def run_crawl():
                # ... (define browser_config_dict and crawler_config_dict)
                # See "Constructing JSON Configuration Payloads" below for examples
                browser_config_dict = {"type": "BrowserConfig", "params": {"headless": True}}
                crawler_config_dict = {"type": "CrawlerRunConfig", "params": {"screenshot": True}}

                results = await client.crawl(
                    urls=["https://example.com"],
                    browser_config=browser_config_dict,
                    crawler_config=crawler_config_dict
                )
                for result in results:
                    if result.success:
                        print(f"Crawled {result.url}, screenshot available: {bool(result.screenshot)}")
                    else:
                        print(f"Failed {result.url}: {result.error_message}")

            # asyncio.run(run_crawl())
            ```
        *   **Authentication with the SDK when JWT is enabled:**
            *   If your server has `security.jwt_enabled: true`, you'll need to authenticate the client.
            *   *Code Example:*
                ```python
                # client = Crawl4aiDockerClient(base_url="http://localhost:11235")
                # await client.authenticate_with_email(email="user@example.com")
                # Now client will automatically include the token in subsequent requests.
                # Or, if you already have a token:
                # client.set_token("your_jwt_token_here")
                ```
                *Note: The `authenticate_with_email` method is a conceptual example. The actual SDK might require you to fetch the token separately and then use `client.set_token()`.*
        *   **Making `crawl()` requests:**
            *   **Non-streaming (default):**
                *   **When to use:** For a small number of URLs or when you need all results before proceeding.
                *   **How results are returned:** The `client.crawl()` call will block until all URLs are processed, then return a list of `CrawlResult` objects.
            *   **Streaming (`stream=True`):**
                *   **Benefits:** For long-running crawls involving many URLs or when processing time per URL is high. It allows you to process results incrementally as they become available, improving responsiveness and potentially reducing memory footprint if you process and discard results immediately.
                *   **How to process:** The `client.crawl(..., stream=True)` will return an async generator. You iterate over it using `async for`.
            *   *Code Example: Python snippet demonstrating both.*
                ```python
                from crawl4ai.docker_client import Crawl4aiDockerClient
                from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode
                import asyncio

                client = Crawl4aiDockerClient(base_url="http://localhost:11235")
                # Assume client is authenticated if JWT is enabled server-side

                browser_cfg_dict = BrowserConfig(headless=True).dump() # Use .dump() to get the serializable dict
                crawler_cfg_dict_base = CrawlerRunConfig(cache_mode=CacheMode.BYPASS).dump()

                urls_to_crawl = ["https://example.com", "https://crawl4ai.com"]

                async def non_streaming_example():
                    print("\n--- Non-Streaming Example ---")
                    results_list = await client.crawl(
                        urls=urls_to_crawl,
                        browser_config=browser_cfg_dict,
                        crawler_config=crawler_cfg_dict_base
                    )
                    for result_data in results_list: # result_data is a dict here
                        print(f"Non-Streamed: {result_data.get('url')} - Success: {result_data.get('success')}")

                async def streaming_example():
                    print("\n--- Streaming Example ---")
                    crawler_cfg_dict_stream = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=True).dump()
                    async for result_data in client.crawl( # result_data is a dict here
                        urls=urls_to_crawl,
                        browser_config=browser_cfg_dict,
                        crawler_config=crawler_cfg_dict_stream
                    ):
                        print(f"Streamed: {result_data.get('url')} - Success: {result_data.get('success')}")
                        # Process each result as it arrives
                        if result_data.get('status') == 'completed': # Check for final stream completion marker
                            print("Stream ended.")
                            break


                async def main_sdk():
                    # If JWT is enabled:
                    # success = await client.authenticate_with_email(email="user@example.com")
                    # if not success:
                    #     print("SDK Authentication failed.")
                    #     return

                    await non_streaming_example()
                    await streaming_example()

                # asyncio.run(main_sdk())
                ```
        *   **Fetching API Schema with `get_schema()`:**
            *   **How this helps:** The schema describes the structure of `BrowserConfig` and `CrawlerRunConfig`, including all available parameters, their types, and default values. This is useful for programmatically understanding configuration options or validating your payloads.
            *   *Code Example:*
                ```python
                # async def show_schema():
                #     schema = await client.get_schema()
                #     print("BrowserConfig Schema:", json.dumps(schema['browser'], indent=2))
                #     print("CrawlerRunConfig Schema:", json.dumps(schema['crawler'], indent=2))
                # asyncio.run(show_schema())
                ```
    *   3.6.3. Constructing JSON Configuration Payloads
        *   **Understanding the `{"type": "ClassName", "params": {...}}` pattern:**
            *   Crawl4ai uses this pattern for serializing and deserializing configuration objects that can have different underlying implementations (strategies).
            *   `"type"`: The Python class name (e.g., "BrowserConfig", "CrawlerRunConfig", "LLMExtractionStrategy").
            *   `"params"`: A dictionary of the parameters that would be passed to the class's `__init__` method.
            *   **Why this pattern?** It allows the server to dynamically instantiate the correct Python configuration objects from the JSON payload sent by the client.
        *   **How-to:** Translate Python class initializations to JSON:
            *   If you have `BrowserConfig(headless=False, browser_type="firefox")` in Python.
            *   The JSON equivalent is:
                ```json
                {
                    "type": "BrowserConfig",
                    "params": {
                        "headless": false,
                        "browser_type": "firefox"
                    }
                }
                ```
            *   Python `BrowserConfig().dump()` or `CrawlerRunConfig().dump()` methods automatically generate this correct JSON-serializable dictionary structure.
        *   **Common pitfalls:**
            *   Forgetting the `"type"` field.
            *   Incorrectly nesting `"params"`.
            *   Using Python booleans (`True`) instead of JSON booleans (`true`). The `dump()` method handles this.
        *   *Example: JSON payload for a complex `CrawlRequest` for the `/crawl` endpoint.*
            ```json
            {
                "urls": ["https://example.com/news", "https://blog.example.com"],
                "browser_config": {
                    "type": "BrowserConfig",
                    "params": {
                        "headless": true,
                        "user_agent": "MyCustomCrawler/1.0"
                    }
                },
                "crawler_config": {
                    "type": "CrawlerRunConfig",
                    "params": {
                        "screenshot": true,
                        "pdf": false,
                        "word_count_threshold": 50,
                        "cache_mode": "bypass"
                    }
                }
            }
            ```
    *   3.6.4. Direct REST API Usage
        *   **When to prefer direct HTTP requests:**
            *   When integrating Crawl4ai into applications written in languages other than Python.
            *   For simple, one-off requests where setting up the SDK might be overkill.
            *   When you need fine-grained control over HTTP headers or request timing not exposed by the SDK.
        *   **How-to:** Making POST requests to `/crawl` (non-streaming).
            *   *Example: `curl` snippet for `/crawl`.*
                ```bash
                # Ensure you have your JWT token if security is enabled
                # export C4AI_TOKEN="your_jwt_token_here"
                curl -X POST "http://localhost:11235/crawl" \
                     -H "Content-Type: application/json" \
                     -H "Authorization: Bearer $C4AI_TOKEN" \
                     -d '{
                           "urls": ["https://example.com"],
                           "browser_config": {"type": "BrowserConfig", "params": {"headless": true}},
                           "crawler_config": {"type": "CrawlerRunConfig", "params": {"screenshot": false}}
                         }'
                ```
            *   *Python `requests` snippet for `/crawl`.*
                ```python
                # import requests
                # import json
                #
                # headers = {"Content-Type": "application/json"}
                # # if jwt_token: headers["Authorization"] = f"Bearer {jwt_token}"
                #
                # payload = {
                #     "urls": ["https://example.com"],
                #     "browser_config": {"type": "BrowserConfig", "params": {"headless": True}},
                #     "crawler_config": {"type": "CrawlerRunConfig", "params": {"screenshot": False}}
                # }
                # response = requests.post("http://localhost:11235/crawl", headers=headers, json=payload)
                # if response.status_code == 200:
                #     print(json.dumps(response.json(), indent=2))
                # else:
                #     print(f"Error: {response.status_code} - {response.text}")
                ```
        *   **How-to:** Making POST requests to `/crawl/stream` (streaming).
            *   **Understanding NDJSON:** The server will stream back results as Newline Delimited JSON. Each line is a complete JSON object representing a `CrawlResult` for one URL, or a status update.
            *   *Example: `curl` for `/crawl/stream` (NDJSON output will print to terminal).*
                ```bash
                # curl -N -X POST "http://localhost:11235/crawl/stream" \
                #      -H "Content-Type: application/json" \
                #      -H "Authorization: Bearer $C4AI_TOKEN" \
                #      -d '{
                #            "urls": ["https://example.com", "https://crawl4ai.com"],
                #            "browser_config": {"type": "BrowserConfig", "params": {"headless": true}},
                #            "crawler_config": {"type": "CrawlerRunConfig", "params": {"stream": true}}
                #          }'
                ```
            *   *Python `requests` snippet for `/crawl/stream` and processing NDJSON.*
                ```python
                # import requests
                # import json
                #
                # headers = {"Content-Type": "application/json"}
                # # if jwt_token: headers["Authorization"] = f"Bearer {jwt_token}"
                #
                # payload = {
                #     "urls": ["https://example.com", "https://crawl4ai.com"],
                #     "browser_config": {"type": "BrowserConfig", "params": {"headless": True}},
                #     "crawler_config": {"type": "CrawlerRunConfig", "params": {"stream": True}} # stream implicitly handled by endpoint
                # }
                # with requests.post("http://localhost:11235/crawl/stream", headers=headers, json=payload, stream=True) as r:
                #     if r.status_code == 200:
                #         for line in r.iter_lines():
                #             if line:
                #                 result_data = json.loads(line.decode('utf-8'))
                #                 print(f"Streamed API: {result_data.get('url')} - Success: {result_data.get('success')}")
                #                 if result_data.get('status') == 'completed':
                #                     print("Stream ended via API.")
                #                     break
                #     else:
                #         print(f"Error: {r.status_code} - {r.text}")
                ```

*   3.7. Exploring Additional API Endpoints
    These endpoints provide targeted functionalities beyond general crawling.
    *   3.7.1. `/html`: Generating Preprocessed HTML
        *   **Purpose:** Use this when you need the HTML of a page after JavaScript execution and basic sanitization (e.g., removing scripts, styles), but *before* Crawl4ai's full Markdown conversion or complex filtering. It's ideal for feeding into custom HTML parsers or schema extraction tools that expect mostly clean, rendered HTML.
        *   **Request structure (`HTMLRequest`):**
            *   `url (str)`: The URL to fetch.
        *   **Response structure:**
            *   `html (str)`: The preprocessed HTML content.
            *   `url (str)`: The original URL requested.
            *   `success (bool)`: Indicates if the operation was successful.
        *   *Example: Use case: You have an external tool that extracts microdata from HTML. Use `/html` to get the rendered HTML for this tool.*
            ```bash
            # curl -X POST "http://localhost:11235/html" \
            #      -H "Content-Type: application/json" \
            #      -H "Authorization: Bearer $C4AI_TOKEN" \
            #      -d '{"url": "https://example.com/dynamic-page"}'
            ```
    *   3.7.2. `/screenshot`: Capturing Web Pages
        *   **Purpose:** To obtain a visual snapshot (PNG) of a web page as it's rendered by the browser. Useful for archiving, visual verification, or when textual content alone isn't sufficient.
        *   **Key parameters (`ScreenshotRequest`):**
            *   `url (str)`: The URL to capture.
            *   `screenshot_wait_for (Optional[float])`: Seconds to wait after page load *before* taking the screenshot.
                *   **How to use:** Essential for pages with animations, delayed content loading via JS, or elements that appear after a short interval. Set this to a few seconds (e.g., `2.0` or `5.0`) to allow such content to render.
            *   `output_path (Optional[str])`:
                *   If provided (e.g., `"./screenshots/page.png"`), the server saves the screenshot to this path *relative to the server's filesystem*. The response will contain the absolute path.
                *   If `null` or omitted, the screenshot is returned as a base64-encoded string in the JSON response.
                *   **Decision:** Use `output_path` if the server has persistent storage and you want files saved directly. Omit it if the client needs to receive and handle the image data.
        *   **Response structure:**
            *   `success (bool)`
            *   `path (str)`: (If `output_path` was provided) Absolute path to the saved screenshot on the server.
            *   `screenshot (str)`: (If `output_path` was *not* provided) Base64 encoded PNG data.
        *   *Example: Capturing a screenshot of a dynamic page after a 2-second delay and receiving it as base64.*
            ```bash
            # curl -X POST "http://localhost:11235/screenshot" \
            #      -H "Content-Type: application/json" \
            #      -H "Authorization: Bearer $C4AI_TOKEN" \
            #      -d '{"url": "https://example.com/animated-chart", "screenshot_wait_for": 2.0}'
            ```
    *   3.7.3. `/pdf`: Generating PDFs
        *   **Purpose:** To create a PDF document from a rendered web page. Useful for printable versions, archiving, or offline reading.
        *   **Key parameters (`PDFRequest`):**
            *   `url (str)`: The URL to convert to PDF.
            *   `output_path (Optional[str])`: Similar to `/screenshot`, if provided, saves the PDF to this server-side path. Otherwise, returns base64 PDF data.
        *   **Response structure:**
            *   `success (bool)`
            *   `path (str)`: (If `output_path` was provided) Absolute path to the saved PDF on the server.
            *   `pdf (str)`: (If `output_path` was *not* provided) Base64 encoded PDF data.
        *   *Example: Generating a PDF for documentation and saving it on the server.*
            ```bash
            # curl -X POST "http://localhost:11235/pdf" \
            #      -H "Content-Type: application/json" \
            #      -H "Authorization: Bearer $C4AI_TOKEN" \
            #      -d '{"url": "https://crawl4ai.com/docs", "output_path": "/app_data/pdfs/crawl4ai_docs.pdf"}'
            ```
    *   3.7.4. `/execute_js`: Running Custom JavaScript
        *   **Purpose:** This is a powerful endpoint for advanced page interactions. Use it when you need to:
            *   Click buttons, fill forms, or trigger other UI events programmatically.
            *   Extract data that is only available after certain JS execution (e.g., from dynamically generated DOM elements).
            *   Modify the page content or state before further processing or screenshotting.
        *   **Key parameters (`JSEndpointRequest`):**
            *   `url (str)`: The URL on which to execute the scripts.
            *   `scripts (List[str])`: A list of JavaScript code snippets to execute in order.
            *   **Best practices for JS snippets:**
                *   Each script in the list should be an **expression that returns a value**, or an IIFE (Immediately Invoked Function Expression).
                *   If a script is asynchronous (e.g., involves `fetch` or `setTimeout`), it **must** return a `Promise`. Crawl4ai will `await` this promise.
                *   Keep snippets focused. For complex logic, consider breaking it into multiple steps in the `scripts` list.
                *   Be mindful of the page's context. Your script runs within the browser's environment for that page.
                *   *Example of a good snippet:* `async () => { await new Promise(r => setTimeout(r, 1000)); return document.title; }`
                *   *Example of a snippet that might not work as expected if not returning a promise for async ops:* `setTimeout(() => { console.log('done'); }, 1000);` (Crawl4ai might not wait for this).
        *   **Response structure:** The full `CrawlResult` object (as a JSON serializable dictionary). The results of your JS executions will be in the `js_execution_result` field of the `CrawlResult`. This field will be a dictionary where keys are `script_0`, `script_1`, etc., and values are the return values of your corresponding scripts.
            *   **How to access:** `response_json['results'][0]['js_execution_result']['script_0']`
        *   *Example: Clicking a "Load More" button and then extracting the count of new items.*
            ```python
            # Python client example
            # js_scripts = [
            #     "document.querySelector('#load-more-btn').click();",
            #     "async () => { await new Promise(r => setTimeout(r, 2000)); return document.querySelectorAll('.item').length; }"
            # ]
            # payload = {"url": "https://example.com/infinite-scroll", "scripts": js_scripts}
            # # ... make request to /execute_js ...
            # # new_item_count = response_data['results'][0]['js_execution_result']['script_1']
            ```
    *   3.7.5. `/ask` (or `/library-context`): Retrieving Library Context for AI
        *   **Purpose:** This endpoint is designed to provide contextual information about the Crawl4ai library itself. It's intended to be used by AI assistants (like code generation copilots or RAG systems) to help them understand Crawl4ai's API, features, and documentation, enabling them to generate more accurate code snippets or provide better assistance.
        *   **Key parameters:**
            *   `context_type (str)`: `"code"`, `"doc"`, or `"all"`.
                *   **When to use:**
                    *   `"code"`: For fetching relevant code snippets (functions, classes).
                    *   `"doc"`: For fetching relevant documentation sections.
                    *   `"all"`: For fetching both.
            *   `query (Optional[str])`: A natural language query or keywords. The endpoint uses BM25 (a text retrieval algorithm) to find relevant chunks of code or documentation based on this query.
                *   **How to formulate:** Be specific. E.g., "how to set proxy in BrowserConfig", "CrawlerRunConfig screenshot options".
            *   `score_ratio (float, default: 0.5)`: A value between 0.0 and 1.0. It filters results based on their BM25 score relative to the maximum possible score for the query. A higher `score_ratio` means more stringent filtering (fewer, more relevant results).
                *   **Understanding its impact:** Start with the default. If you get too few results, lower it. If too many irrelevant results, increase it.
            *   `max_results (int, default: 20)`: The maximum number of code chunks or documentation sections to return.
        *   **Response structure:** A JSON object containing:
            *   `code_results (List[Dict])`: If `context_type` includes "code". Each dict has `"text"` (the code chunk) and `"score"`.
            *   `doc_results (List[Dict])`: If `context_type` includes "doc". Each dict has `"text"` (the documentation chunk) and `"score"`.
        *   *Example: Using `/ask` to get information about `BrowserConfig` for an AI assistant.*
            ```bash
            # curl -X GET "http://localhost:11235/ask?context_type=all&query=BrowserConfig%20proxy%20settings&max_results=3" \
            #      -H "Authorization: Bearer $C4AI_TOKEN"
            ```
            This would return code snippets and documentation sections related to proxy settings in `BrowserConfig`.

*   3.8. MCP (Model Context Protocol) Integration
    *   3.8.1. What is MCP and Why Use It?
        *   **Explanation:** MCP (Model Context Protocol) is a standardized way for AI models and development tools (like IDE extensions) to interact with external services and fetch context. Crawl4ai's MCP support allows AI tools that understand MCP (e.g., Anthropic's Claude Code extension for VS Code) to directly use Crawl4ai's functionalities.
        *   **Benefits:**
            *   **Seamless Tool Integration:** AI tools can discover and use Crawl4ai's capabilities without custom API integrations for each tool.
            *   **Contextual Awareness:** The AI model gets structured information about what a tool can do, its parameters, and how to interpret its output.
            *   **Enhanced AI Assistance:** Enables AI to, for example, suggest Crawl4ai code, execute crawls, or get information from web pages directly within the development environment.
    *   3.8.2. Connection Endpoints: `/mcp/sse` and `/mcp/ws`
        *   **SSE (Server-Sent Events - `/mcp/sse`):** A unidirectional stream from server to client. Simpler for many MCP use cases where the tool primarily sends a request and awaits a response or stream of updates.
        *   **WebSockets (`/mcp/ws`):** A bidirectional, persistent connection. More suitable for highly interactive tools or when continuous two-way communication is needed.
        *   **When to choose:** For most current MCP integrations (like with Claude Code), SSE is often sufficient and simpler to implement on the client-tool side.
    *   3.8.3. **How-to:** Integrating with Claude Code
        *   The `claude mcp add` command registers an MCP-compliant service with your Claude Code extension.
        *   *Example:*
            ```bash
            # Assuming your Crawl4ai server is running locally
            claude mcp add -t sse c4ai-mcp-service http://localhost:11235/mcp/sse
            ```
            *Replace `c4ai-mcp-service` with a name of your choice for this tool in Claude.*
        *   **Illustrative workflow:**
            1.  Add the Crawl4ai MCP service to Claude Code.
            2.  In your code editor, you might ask Claude: "@c4ai-mcp-service Get the Markdown for example.com".
            3.  Claude, understanding MCP, would interact with the `/mcp/sse` endpoint, invoke the appropriate Crawl4ai tool (likely the `md` or `crawl` tool), and return the result to you in the editor.
    *   3.8.4. Available MCP Tools and Their Use Cases
        *   The tools exposed via MCP largely mirror the additional API endpoints:
            *   `md`: Get Markdown content for a URL. **Use case:** Quickly summarize a page for an LLM.
            *   `html`: Get preprocessed HTML. **Use case:** Provide cleaner HTML to an AI for parsing.
            *   `screenshot`: Get a screenshot. **Use case:** Visual context for an AI, or for documentation.
            *   `pdf`: Get a PDF. **Use case:** Archival or providing document context.
            *   `execute_js`: Run JavaScript on a page. **Use case:** Interact with dynamic elements before an AI processes the page.
            *   `crawl`: Perform a full crawl operation. **Use case:** Comprehensive data gathering directed by an AI.
            *   `ask`: Query library context. **Use case:** AI asks Crawl4ai about its own capabilities to generate better code.
    *   3.8.5. Testing MCP Connections and Tool Usage
        *   **Simple methods:**
            *   Use `curl` with the `-N` (no-buffering) flag for SSE to see the event stream:
                ```bash
                # Example: Test list_tools via MCP/SSE
                # You'd typically send a JSON-RPC request in the first message after connection.
                # This is a simplified conceptual test.
                # curl -N -H "Content-Type: application/json" http://localhost:11235/mcp/sse
                # (Then send a JSON-RPC request for list_tools on the established connection if the tool supports it interactively)
                ```
            *   Use a WebSocket client (like `wscat` or a browser's developer console) to connect to `/mcp/ws` and send JSON-RPC messages.
            *   The best way to test is often through an MCP-compliant client tool like the Claude Code extension.
    *   3.8.6. Accessing MCP Schemas (`/mcp/schema`)
        *   **How this helps:** This endpoint returns a JSON schema describing all available MCP tools, their methods, parameters, and return types. This is how MCP client tools (like Claude Code) discover what Crawl4ai can do via MCP. It's crucial for the self-describing nature of MCP.

*   3.9. Monitoring Your Crawl4ai Server
    *   3.9.1. Health Checks with `/health`
        *   **Purpose:** A simple endpoint to verify that the Crawl4ai server is running and responsive. Commonly used by load balancers, container orchestrators (like Kubernetes), or uptime monitoring services.
        *   **Interpreting the response:**
            *   A `200 OK` response with JSON like `{"status": "ok", "timestamp": ..., "version": "..."}` indicates the server is healthy.
            *   Any other status code or an inability to connect suggests a problem.
    *   3.9.2. Prometheus Metrics with `/metrics`
        *   **How to integrate:** If `observability.prometheus.enabled: true` in `config.yml` (default is true), this endpoint exposes metrics in Prometheus format. Configure your Prometheus server to scrape this endpoint.
        *   **Overview of important metrics (inferred from `prometheus_fastapi_instrumentator` usage):**
            *   Request counts, latencies, and error rates for API endpoints.
            *   Python process information (CPU, memory - if default instrumentator collectors are active).
            *   Potentially custom metrics related to crawl queue length, active browser instances, etc. (though these might need explicit addition in `server.py`).
        *   **Why use:** Essential for understanding server load, performance bottlenecks, error trends, and for setting up alerts.

*   3.10. Understanding the Server's Inner Workings (High-Level for Users)
    Understanding these components can help you configure the server optimally and troubleshoot issues.
    *   3.10.1. FastAPI Application: The Core of the Server
        *   **Role:** FastAPI is a modern, fast web framework for building APIs with Python. It handles incoming HTTP requests, routing, request validation, and response serialization for all Crawl4ai API endpoints.
        *   **Why it's used:** Its performance, ease of use, and automatic data validation/serialization make it well-suited for building robust APIs like Crawl4ai's.
    *   3.10.2. Managing Browser Instances with `crawler_pool`
        *   **Role:** The `crawler_pool` (likely an instance of `BrowserManager` or a similar custom pool) is responsible for managing a collection of `AsyncWebCrawler` instances.
        *   `get_crawler`: When an API request needs a browser, this function provides an available (and potentially pre-warmed) `AsyncWebCrawler` instance from the pool. If all instances are busy, it might create a new one up to a limit, or wait.
        *   `close_all` and `janitor`: These are crucial for resource management.
            *   `close_all` is typically called on server shutdown to gracefully close all browser instances.
            *   The `janitor` task (referenced in `lifespan`) periodically checks for idle browser instances in the pool and closes them if they've exceeded their `idle_ttl_sec` (configured in `config.yml`).
        *   **Impact:** Proper pool management prevents resource leaks (e.g., too many zombie browser processes) and optimizes browser startup times by reusing instances.
    *   3.10.3. Capping Concurrent Pages with `GLOBAL_SEM`
        *   **Role:** `GLOBAL_SEM` (an `asyncio.Semaphore`) acts as a server-wide gatekeeper, limiting the total number of browser pages that can be concurrently active across all `AsyncWebCrawler` instances.
        *   **Why this is important:** Each browser page consumes significant memory and CPU. Without a cap, a high volume of requests could easily overwhelm the server, leading to crashes or extreme slowdowns.
        *   **How `crawler.pool.max_pages` in `config.yml` relates:** This configuration value directly sets the limit for `GLOBAL_SEM`.
        *   **Decision:** Adjust `max_pages` carefully based on your server's RAM. If you see `asyncio.TimeoutError` or tasks getting stuck waiting for the semaphore, you might have too many concurrent requests for your `max_pages` setting, or individual crawls are taking too long.
    *   3.10.4. Asynchronous Task Management (Job Router - `api.py` based)
        *   **Role:** For operations that can be time-consuming (like a crawl involving many URLs, or an LLM extraction that requires multiple API calls), Crawl4ai often offloads these to background tasks. This is especially true for non-streaming `/crawl` or `/llm/{url_or_task_id}` endpoints.
        *   The "job router" (conceptually, parts of `api.py` and `job.py`) handles:
            1.  Receiving the initial request.
            2.  Assigning a unique `task_id`.
            3.  Storing initial task metadata (URL, status: PENDING/PROCESSING) often in Redis.
            4.  Adding the actual work (e.g., `process_llm_extraction` or `handle_crawl_job`) to a FastAPI `BackgroundTasks` queue or a more robust Celery/RQ queue (if integrated).
            5.  Returning the `task_id` to the client immediately.
            6.  The client then polls a status endpoint (e.g., `/task/{task_id}`) to check progress.
            7.  Once the background task completes, it updates the task's status and result in Redis.
        *   **Role of Redis:**
            *   Stores task state (status, result, error).
            *   Can act as a message broker for task queues in more advanced setups.
        *   **User Interaction:** You submit a job, get a task ID, and then poll for completion. This prevents HTTP timeouts for long-running operations.
    *   3.10.5. Rate Limiting and Security Middleware
        *   **How `config.yml` settings are applied:** FastAPI allows "middleware" to process requests before they hit your main endpoint logic and before responses are sent.
            *   **Rate Limiting:** The `slowapi` library is used. Middleware intercepts each request, checks the client's IP (or token identity) against configured limits (e.g., "1000/minute" from `config.yml`) stored in memory or Redis. If limits are exceeded, it returns a `429 Too Many Requests` error.
            *   **Security:** Middleware like `HTTPSRedirectMiddleware` and `TrustedHostMiddleware` enforce security policies (redirecting HTTP to HTTPS, validating Host headers). Security headers are added to outgoing responses.
        *   **Protections offered:**
            *   Rate limiting: Prevents abuse and server overload.
            *   HTTPS redirect: Enforces secure connections.
            *   Trusted hosts: Mitigates host header injection attacks.
            *   Security headers: Protect against common web vulnerabilities like XSS, clickjacking.
    *   3.10.6. Mapping API Requests to `AsyncWebCrawler`
        *   1.  An HTTP request hits a FastAPI endpoint (e.g., `POST /crawl`).
        *   2.  FastAPI, using Pydantic, validates and parses the JSON request body into a `CrawlRequest` Pydantic model. This model contains `urls`, `browser_config` (as a dict), and `crawler_config` (as a dict).
        *   3.  The endpoint logic uses `BrowserConfig.load(browser_config_dict)` and `CrawlerRunConfig.load(crawler_config_dict)` to convert these dictionaries back into their respective Python configuration objects.
        *   4.  It then calls `await crawler_pool.get_crawler(browser_config_object)` to obtain an appropriate `AsyncWebCrawler` instance. The pool might reuse an existing compatible instance or create a new one.
        *   5.  Finally, `await crawler_instance.arun(url=..., config=crawler_run_config_object)` or `await crawler_instance.arun_many(...)` is called to perform the actual crawl.
        *   **Key takeaway:** The `{"type": ..., "params": ...}` JSON structure is crucial for the server to correctly deserialize configurations passed from clients into the Python objects `AsyncWebCrawler` expects. The `.dump()` methods on config objects are the Pythonic way to generate these serializable dicts.

## 4. Understanding Crawl4ai Versioning

Crawl4ai follows Semantic Versioning (SemVer) to help you manage updates and understand the implications of new releases.

*   4.1. Semantic Versioning (`MAJOR.MINOR.PATCH`)
    *   **`MAJOR` (e.g., `0.x.x` -> `1.x.x`):** Incremented for **incompatible API changes** (breaking changes). You will likely need to update your code when upgrading to a new major version.
        *   *Why it matters:* Pay close attention when a MAJOR version changes. Read release notes carefully.
    *   **`MINOR` (e.g., `0.5.x` -> `0.6.x`):** Incremented for **new functionality added in a backward-compatible manner**. Your existing code should continue to work.
        *   *Why it matters:* You can usually upgrade minor versions safely to get new features and improvements.
    *   **`PATCH` (e.g., `0.6.0` -> `0.6.1`):** Incremented for **backward-compatible bug fixes**.
        *   *Why it matters:* It's generally safe and recommended to apply patch updates.
    *   **Why this is important for users:** SemVer provides predictability. You can configure your dependency management (e.g., in `requirements.txt` or `pyproject.toml`) to allow automatic patch and minor updates (e.g., `crawl4ai~=0.6.0`) but require manual intervention for major updates.

*   4.2. Pre-release Suffixes
    Crawl4ai uses standard suffixes for pre-release versions, allowing users to test upcoming features.
    *   `dev` (e.g., `0.7.0.dev1`): **Development versions.** These are typically built automatically from the main development branch. They are the most cutting-edge but can be unstable and are not recommended for production.
    *   `a` (alpha, e.g., `0.7.0a1`): **Alpha releases.** Early previews of new major or minor versions. Features might be incomplete or buggy. Use for testing and providing early feedback.
    *   `b` (beta, e.g., `0.7.0b1`): **Beta releases.** Feature-set is largely complete, but the release is still undergoing testing and refinement. More stable than alpha but may still contain bugs.
    *   `rc` (release candidate, e.g., `0.7.0rc1`): **Release candidates.** Believed to be stable and ready for final release, pending final testing. Good for testing in staging environments.
    *   **Guidance on when to use pre-release versions:**
        *   Use `dev`, `a`, or `b` if you want to experiment with upcoming features or contribute to testing, but be prepared for instability.
        *   Use `rc` if you want to test the very latest potentially stable version before its official release.
        *   For production, always stick to stable releases (no suffix).
        *   To install pre-releases: `pip install crawl4ai --pre`.

## 5. Troubleshooting Common Deployment Issues

Here are some common issues you might encounter and how to approach them:

*   5.1. Library Installation Problems
    *   **Playwright browser download failures:**
        *   **Symptom:** `crawl4ai-setup` or `playwright install` fails with network errors or messages about not being able to download browsers.
        *   **Reasoning:** Often due to network connectivity issues, firewalls, or proxies blocking the download. Playwright needs to download browser binaries which can be large.
        *   **Solution:**
            *   Ensure stable internet connection.
            *   If behind a proxy, configure Playwright's proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`).
            *   Try running `playwright install --with-deps chromium` (or your browser of choice) manually to see more detailed error messages.
            *   Check Playwright's documentation for troubleshooting browser downloads.
    *   **Dependency conflicts:**
        *   **Symptom:** `pip install crawl4ai` fails with messages about conflicting package versions.
        *   **Reasoning:** Your existing Python environment might have packages with versions incompatible with Crawl4ai's dependencies.
        *   **Solution:**
            *   **Best Practice:** Use a virtual environment (e.g., `venv`, `conda`) for your Crawl4ai projects to isolate dependencies.
            *   Examine the error messages to identify the conflicting packages and try to resolve them, perhaps by upgrading/downgrading other packages or installing Crawl4ai in a fresh environment.

*   5.2. Docker Deployment Issues
    *   **Port conflicts:**
        *   **Symptom:** `docker run` or `docker-compose up` fails with an error like "port is already allocated."
        *   **Reasoning:** The default port for Crawl4ai (11235) is already in use by another application on your host machine.
        *   **Solution:**
            *   Stop the other application using the port.
            *   Map Crawl4ai to a different host port: `docker run -p <new_host_port>:11235 ...` (e.g., `-p 11236:11235`). Remember to update your client to use the new host port.
    *   **Incorrect environment variable setup for LLM API keys:**
        *   **Symptom:** LLM-dependent features (like `LLMExtractionStrategy`) fail, often with authentication errors from the LLM provider.
        *   **Reasoning:** The Docker container doesn't have access to the necessary API keys.
        *   **Solution:** Ensure you are correctly passing the `.llm.env` file when running the container (`--env-file .llm.env`) or that environment variables are set through Docker Compose or your orchestration platform. Double-check the variable names in your `.llm.env` file match what `config.yml` expects (e.g., `OPENAI_API_KEY`).
    *   **Memory allocation issues (`--shm-size`):**
        *   **Symptom:** Browsers inside Docker crash, pages fail to load with cryptic errors, or the container itself becomes unresponsive, especially under load.
        *   **Reasoning:** Chromium-based browsers use `/dev/shm` (shared memory) extensively. The Docker default for `/dev/shm` (often 64MB) is usually too small for multiple or complex browser tabs.
        *   **Solution:** Always run your Crawl4ai Docker container with an increased shared memory size. Start with `--shm-size=1g`. If issues persist, try `2g`. The `docker-compose.yml` provided in the Crawl4ai repository typically includes a volume mount for `/dev/shm` which effectively does the same.
    *   **Problems building local Docker images:**
        *   **Symptom:** `docker build` or `docker-compose build` fails.
        *   **Reasoning:** Could be network issues during dependency downloads, incorrect build arguments, problems with the Dockerfile syntax (if modified), or insufficient disk space.
        *   **Solution:**
            *   Check your internet connection.
            *   Carefully review the build arguments you're passing (`INSTALL_TYPE`, `ENABLE_GPU`, etc.).
            *   Examine the Docker build output for specific error messages.
            *   Ensure you have enough disk space.

*   5.3. Server Configuration (`config.yml`) Errors
    *   **YAML syntax errors:**
        *   **Symptom:** Server fails to start, with errors related to parsing `config.yml`.
        *   **Reasoning:** Incorrect indentation, missing colons, or other YAML syntax issues.
        *   **Solution:** Use a YAML linter or validator to check your `config.yml` file. Pay close attention to indentation (spaces, not tabs).
    *   **Misconfigured JWT settings:**
        *   **Symptom:** If `jwt_enabled: true`, clients might get `401 Unauthorized` or `403 Forbidden` errors even with what seems like a correct token.
        *   **Reasoning:** Issues with secret key consistency (if applicable, though Crawl4ai uses a fixed default or one configurable via env var), token expiration, or incorrect algorithm settings (though Crawl4ai handles this internally).
        *   **Solution:** Ensure clients are sending the token correctly in the `Authorization: Bearer <token>` header. Regenerate tokens if they might have expired. For complex JWT issues, you might need to debug the token generation/validation logic if you've heavily customized the server.

*   5.4. API Interaction Problems
    *   **Authentication failures:**
        *   **Symptom:** Client receives `401` or `403` errors.
        *   **Reasoning:** JWT is enabled on the server, but the client is not sending a valid token, or the token has expired.
        *   **Solution:** Ensure your client correctly obtains a token from `/token` and includes it in the `Authorization` header for subsequent requests.
    *   **Incorrectly structured request payloads:**
        *   **Symptom:** Client receives `422 Unprocessable Entity` errors.
        *   **Reasoning:** The JSON payload sent to endpoints like `/crawl` does not match the expected Pydantic schema (e.g., missing required fields, incorrect data types, wrong `{"type": ..., "params": ...}` structure for configs).
        *   **Solution:** Refer to the `/playground` (Swagger UI) for the correct request schemas. Use the `dump()` method of `BrowserConfig` and `CrawlerRunConfig` if constructing payloads in Python to ensure correct serialization.
    *   **Understanding error responses from the API:**
        *   The API usually returns JSON error responses with a `detail` field explaining the issue. Pay attention to this field.
        *   HTTP status codes also provide clues (400 for bad request, 401/403 for auth, 404 for not found, 422 for validation, 500 for server errors).

*   5.5. When to Check Server Logs
    *   **How to access Docker container logs:**
        ```bash
        docker logs crawl4ai-server # Replace crawl4ai-server with your container name/ID
        docker logs -f crawl4ai-server # To follow logs in real-time
        ```
        If using Docker Compose:
        ```bash
        docker-compose logs crawl4ai # Assuming 'crawl4ai' is the service name in docker-compose.yml
        ```
    *   **What to look for:**
        *   Python tracebacks indicating exceptions within the server code.
        *   Log messages from `crawl4ai` itself (often prefixed with tags like `[CRAWLER]`, `[ERROR]`, `[CONFIG]`).
        *   Uvicorn/FastAPI startup messages and request logs.
        *   Any messages related to resource limits (memory, file descriptors).
        *   Playwright browser errors if they are not caught and handled by the application.

## 6. Best Practices for Deployment

*   6.1. **Choosing the Right Deployment Method:**
    *   **Library:** For quick scripts, Python-centric projects, or when direct integration is paramount.
    *   **Docker (Pre-built):** For ease of use, standard deployments, and quick server setup.
    *   **Docker Compose:** For managing Crawl4ai with other services (like Redis) or for simplified local builds with custom arguments.
    *   **Docker (Manual Build):** For full customization, development, or specific CI/CD needs.
*   6.2. **Security Considerations for Server Deployment:**
    *   **Always enable JWT (`security.jwt_enabled: true`)** if the server is accessible beyond your local machine.
    *   Use strong, unique secrets for JWT if you customize it (though Crawl4ai has a default mechanism).
    *   Configure `security.trusted_hosts` to specific domains in production.
    *   Use a reverse proxy (like Nginx or Traefik) to handle SSL/TLS termination and potentially add another layer of security (WAF, IP blocking).
    *   Keep API keys and sensitive configurations out of version control; use `.llm.env` or environment variables.
*   6.3. **Monitoring and Scaling Your Dockerized Server:**
    *   Utilize the `/health` endpoint for liveness/readiness probes in orchestrators.
    *   Integrate `/metrics` with Prometheus and Grafana for performance monitoring and alerting.
    *   Scale horizontally (more container instances) behind a load balancer for high availability and increased throughput.
    *   Adjust `crawler.pool.max_pages` and container resources (CPU, RAM, `--shm-size`) based on observed load and performance.
*   6.4. **Managing Dependencies and Upgrades:**
    *   For library usage, use virtual environments.
    *   For Docker, pin to specific image versions (e.g., `unclecode/crawl4ai:0.6.0`) in production to avoid unexpected updates.
    *   Read release notes carefully before upgrading `MAJOR` or `MINOR` versions.
*   6.5. **Leveraging Configuration for Optimal Performance and Cost-Effectiveness:**
    *   Use appropriate `CacheMode` settings in `CrawlerRunConfig` to avoid re-crawling unchanged content.
    *   Fine-tune `word_count_threshold` and content filters to process only relevant data, especially before sending to costly LLMs.
    *   If using LLM extraction, design efficient prompts and schemas. Consider if a simpler CSS/XPath extraction can achieve the same for some fields.
    *   Adjust `crawler.pool.idle_ttl_sec` to balance resource usage and browser startup latency.

## 7. Next Steps & Further Learning

With a solid understanding of deployment, you're ready to explore more advanced capabilities:

*   7.1. **Exploring Advanced Crawler Configuration (`CrawlerRunConfig`):** Dive into parameters like `js_code`, `wait_for`, various filters (`word_count_threshold`, `exclude_paths`), and media handling options.
*   7.2. **Diving Deeper into Extraction Strategies:** Learn about `LLMExtractionStrategy`, `JsomCssExtractionStrategy`, and how to build custom schemas for precise data extraction.
*   7.3. **Advanced Page Interaction Techniques:** Master the use of `js_code` for complex interactions, form submissions, and handling dynamic content that simple waits can't manage.
*   7.4. **Contributing to Crawl4ai:** If you're interested in improving Crawl4ai, check out the [contribution guidelines](https://github.com/unclecode/crawl4ai/blob/main/CONTRIBUTORS.md) and open issues/PRs.

This deployment guide should provide a strong foundation. Remember that the best configuration often comes from understanding your specific use case, experimenting, and monitoring performance. Happy Crawling!
```

## Content (Examples)

```markdown
# Examples for `crawl4ai` - Deployment Component

**Target Document Type:** Examples Collection
**Target Output Filename Suggestion:** `llm_examples_deployment.md`
**Library Version Context:** 0.5.1-d1
**Outline Generation Date:** 2025-05-24
---

This document provides runnable code examples showcasing the diverse usage patterns and configurations of the `crawl4ai` deployment component. The examples primarily focus on interacting with the API provided by a deployed Crawl4ai instance.

## I. Introduction to Crawl4ai Deployment Examples

### 1.1. Overview of the API and common interaction patterns (e.g., using `requests` library).
The Crawl4ai deployment exposes a FastAPI backend. Most examples will use the `requests` library for synchronous calls and `httpx` for asynchronous calls to interact with these API endpoints. The base URL for a local deployment is typically `http://localhost:11235`.

```python
import requests
import httpx # For async examples later
import asyncio
import json
import time
import os
import base64

# Assume the Crawl4ai API is running locally
BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
API_TOKEN = os.environ.get("CRAWL4AI_API_TOKEN") # Set if your API requires auth

def get_headers():
    if API_TOKEN:
        return {"Authorization": f"Bearer {API_TOKEN}"}
    return {}

print(f"Crawl4AI API Base URL: {BASE_URL}")
if API_TOKEN:
    print("API Token will be used for authenticated requests.")
else:
    print("No API Token found in env; assuming API does not require authentication for these examples.")

# A simple synchronous GET request
try:
    response = requests.get(f"{BASE_URL}/health")
    response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
    print(f"Health check successful: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Error connecting to Crawl4AI API: {e}")
    print("Please ensure the Crawl4AI Docker container or server is running.")
```

### 1.2. Note on Authentication: Brief explanation of when and how to use API tokens.
If JWT authentication is enabled in `config.yml` (via `security.jwt_enabled: true`), most API endpoints will require an `Authorization: Bearer <YOUR_TOKEN>` header. You can obtain a token from the `/token` endpoint using a whitelisted email address. The `get_headers()` helper function in the examples will attempt to use `CRAWL4AI_API_TOKEN` if set.

---
## II. Docker and Docker-Compose

### 2.1. Building the Docker Image

#### 2.1.1. Example: Basic `docker build` command.
This command builds the default Docker image from the root of the `crawl4ai` repository.
```bash
# Navigate to the root of the crawl4ai repository
# cd /path/to/crawl4ai
docker build -t crawl4ai:latest .
```

#### 2.1.2. Example: Building with `INSTALL_TYPE=all` build argument.
This installs all optional dependencies, including those for advanced AI/ML features.
```bash
# Navigate to the root of the crawl4ai repository
# cd /path/to/crawl4ai
docker build --build-arg INSTALL_TYPE=all -t crawl4ai:all-features .
```

#### 2.1.3. Example: Building with `ENABLE_GPU=true` build argument (conceptual, as GPU usage is complex).
This attempts to include GPU support (e.g., CUDA toolkits) if the base image and host support it.
```bash
# Navigate to the root of the crawl4ai repository
# cd /path/to/crawl4ai
# Ensure your Docker daemon and host are configured for GPU passthrough
docker build --build-arg ENABLE_GPU=true --build-arg TARGETARCH=amd64 -t crawl4ai:gpu-amd64 .
# For ARM64 with GPU (e.g., NVIDIA Jetson), you might need specific base images or configurations.
# docker build --build-arg ENABLE_GPU=true --build-arg TARGETARCH=arm64 -t crawl4ai:gpu-arm64 .
```
**Note:** Full GPU support in Docker can be complex and depends on your host system, NVIDIA drivers, and Docker version. The `Dockerfile` provides a basic attempt.

---
### 2.2. Running with Docker Compose

#### 2.2.1. Example: Basic `docker-compose up` using the provided `docker-compose.yml`.
This starts the Crawl4ai service as defined in the `docker-compose.yml` file.
```bash
# Navigate to the directory containing docker-compose.yml
# cd /path/to/crawl4ai
docker-compose up -d
```

#### 2.2.2. Example: Overriding image tag in `docker-compose` via environment variable `TAG`.
You can specify a different image tag for the `crawl4ai` service.
```bash
# Example: Using a specific version tag
TAG=0.6.0 docker-compose up -d

# Example: Using a custom built tag
# TAG=my-custom-crawl4ai-build docker-compose up -d
```

#### 2.2.3. Example: Overriding `INSTALL_TYPE` in `docker-compose` via environment variable.
If your `docker-compose.yml` is set up to use build arguments from environment variables, you can override `INSTALL_TYPE`.
```bash
# Assuming docker-compose.yml uses INSTALL_TYPE from env for the build context:
# (The provided docker-compose.yml directly passes it as a build arg)
# If you modify docker-compose.yml to pick up an env var for INSTALL_TYPE:
# INSTALL_TYPE=all docker-compose up -d --build
```
**Note:** The provided `docker-compose.yml` directly sets `INSTALL_TYPE` in the `args` section. To make it environment-variable driven like `TAG`, you would modify the `docker-compose.yml`'s `build.args` section.

---
### 2.3. Configuration via Environment Variables & `.llm.env`

#### 2.3.1. Example: Setting `OPENAI_API_KEY` using an `.llm.env` file.
Create a `.llm.env` file in the same directory as `docker-compose.yml` or where you run the server.
```text
# Contents of .llm.env
OPENAI_API_KEY="sk-your_openai_api_key_here"
```
The `docker-compose.yml` (or server if run directly) will load this file.

#### 2.3.2. Example: Showing how to pass multiple LLM API keys via `.llm.env`.
You can add keys for various supported LLM providers.
```text
# Contents of .llm.env
OPENAI_API_KEY="sk-your_openai_api_key_here"
ANTHROPIC_API_KEY="sk-ant-your_anthropic_api_key_here"
GROQ_API_KEY="gsk_your_groq_api_key_here"
# ...and other keys supported by LiteLLM
```

---
### 2.4. Accessing the Deployed Service

#### 2.4.1. Example: Python script to perform a basic health check (`/health`) on the locally deployed service.
```python
import requests
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")

try:
    response = requests.get(f"{BASE_URL}/health")
    response.raise_for_status()
    data = response.json()
    print(f"Service is healthy. Version: {data.get('version')}, Timestamp: {data.get('timestamp')}")
except requests.exceptions.RequestException as e:
    print(f"Failed to connect or health check failed: {e}")
```

#### 2.4.2. Example: Accessing the API playground at `/playground`.
Open your web browser and navigate to `http://localhost:11235/playground` (or your deployed URL + `/playground`). This will show the FastAPI interactive API documentation.

---
### 2.5. Understanding Shared Memory

#### 2.5.1. Explanation: Importance of `/dev/shm` for Chromium performance and how it's configured in `docker-compose.yml`.
Chromium-based browsers (like Chrome, Edge) use `/dev/shm` (shared memory) extensively. If the default Docker limit for `/dev/shm` (often 64MB) is too small, browser instances can crash or perform poorly. The `docker-compose.yml` provided with Crawl4ai typically increases this:
```yaml
# Snippet from a typical docker-compose.yml for crawl4ai
# services:
#   crawl4ai:
#     # ... other configurations ...
#     shm_size: '1g' # Or '2g', depending on expected load
#     # Alternatively, for more flexibility but less security:
#     # volumes:
#     #   - /dev/shm:/dev/shm
```
Setting `shm_size` or mounting `/dev/shm` directly from the host provides more shared memory, preventing common browser crashes within Docker. The `Dockerfile` also sets `ENV DEBIAN_FRONTEND=noninteractive` and browser flags like `--disable-dev-shm-usage` to mitigate some issues, but adequate shared memory is still crucial.

---
## III. Interacting with the Crawl4ai API Endpoints

### A. Authentication (`/token`)

#### A.1. Example: Python script to obtain an API token using a valid email.
This example assumes JWT authentication is enabled and "user@example.com" is whitelisted (this is illustrative, actual whitelisting is not part of the default config).
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")

# This email domain would need to be configured as allowed in your security settings
# if verify_email_domain is used.
email_to_test = "user@example.com" # Replace with a valid email if your server uses domain verification

payload = {"email": email_to_test}
try:
    response = requests.post(f"{BASE_URL}/token", json=payload)
    if response.status_code == 200:
        token_data = response.json()
        print(f"Successfully obtained token for {email_to_test}:")
        print(json.dumps(token_data, indent=2))
        # Store this token for subsequent authenticated requests
        # API_TOKEN = token_data["access_token"]
    else:
        print(f"Failed to obtain token for {email_to_test}. Status: {response.status_code}, Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error connecting to /token endpoint: {e}")
```
**Note:** The default `config.yml` has `security.jwt_enabled: false`. For this example to fully work, you would need to enable JWT and potentially configure allowed email domains.

#### A.2. Example: Python script attempting to obtain a token with an invalid email domain and handling the error.
```python
import requests
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")

# Assuming "invalid-domain.com" is not whitelisted.
# The default Crawl4AI config doesn't whitelist specific domains for /token,
# but if `verify_email_domain` were true in auth.py, this would be relevant.
# For now, this will likely succeed if jwt_enabled is false, or fail if jwt_enabled is true
# and no user exists, or pass if jwt_enabled is true and any email can get a token.
payload = {"email": "test@invalid-domain.com"}
try:
    response = requests.post(f"{BASE_URL}/token", json=payload)
    if response.status_code == 400 and "Invalid email domain" in response.text:
        print(f"Correctly failed to obtain token for invalid domain: {response.text}")
    elif response.status_code == 200:
        print(f"Obtained token (unexpected if domain verification is strict): {response.json()}")
    else:
        print(f"Token request status: {response.status_code}, Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error connecting to /token endpoint: {e}")
```

#### A.3. Example: Python script making an authenticated request to a protected endpoint.
This example assumes an endpoint like `/md` is protected and requires a token.
```python
import requests
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
# First, obtain a token (replace with actual token for a real protected setup)
# For this example, we'll use a placeholder. If API_TOKEN is set in env, it will be used.
# If not, and the endpoint is truly protected, this will fail.
# API_TOKEN = "your_manually_obtained_token_or_from_previous_step"

headers = get_headers() # Uses API_TOKEN from environment if set

md_payload = {"url": "https://example.com"}
try:
    response = requests.post(f"{BASE_URL}/md", json=md_payload, headers=headers)
    if response.status_code == 200:
        print("Successfully accessed protected /md endpoint.")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:500] + "...")
    elif response.status_code == 401 or response.status_code == 403:
        print(f"Authentication/Authorization failed for /md: {response.status_code} - {response.text}")
        print("Ensure JWT is enabled and you have a valid token if this endpoint is protected.")
    else:
        print(f"Request to /md failed: {response.status_code} - {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error connecting to /md endpoint: {e}")
```
**Note:** By default, most Crawl4ai endpoints are not protected by JWT even if `jwt_enabled` is true, unless explicitly decorated with `Depends(token_dep)`.

---
### B. Core Crawling Endpoints

#### B.1. `/crawl` (Asynchronous Job-based Crawling via Redis)

The `/crawl` endpoint submits a job to a Redis queue. You then poll the `/task/{task_id}` endpoint to get the status and results.

##### B.1.1. Example: Submitting a single URL crawl job and getting a `task_id`.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "urls": ["https://example.com"],
    # browser_config and crawler_config are optional, defaults will be used
}

try:
    response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
    response.raise_for_status()
    job_data = response.json()
    task_id = job_data.get("task_id")
    if task_id:
        print(f"Crawl job submitted successfully. Task ID: {task_id}")
        print(f"Poll status at: {BASE_URL}/task/{task_id}")
    else:
        print(f"Failed to submit job or get task_id: {job_data}")
except requests.exceptions.RequestException as e:
    print(f"Error submitting crawl job: {e}")
```

##### B.1.2. Example: Submitting multiple URLs as a single crawl job.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "urls": ["https://example.com", "https://www.python.org"],
}

try:
    response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
    response.raise_for_status()
    job_data = response.json()
    task_id = job_data.get("task_id")
    if task_id:
        print(f"Multi-URL crawl job submitted. Task ID: {task_id}")
    else:
        print(f"Failed to submit job: {job_data}")
except requests.exceptions.RequestException as e:
    print(f"Error submitting multi-URL crawl job: {e}")

```

##### B.1.3. Example: Submitting a crawl job with a custom `browser_config` (e.g., headless false).
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "urls": ["https://example.com"],
    "browser_config": {
        "headless": False, # Run browser in visible mode (if server environment supports UI)
        "viewport_width": 800,
        "viewport_height": 600
    }
}

try:
    response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
    response.raise_for_status()
    job_data = response.json()
    task_id = job_data.get("task_id")
    if task_id:
        print(f"Crawl job with custom browser_config submitted. Task ID: {task_id}")
    else:
        print(f"Failed to submit job: {job_data}")
except requests.exceptions.RequestException as e:
    print(f"Error submitting crawl job with custom browser_config: {e}")
```

##### B.1.4. Example: Submitting a crawl job with a custom `crawler_config` (e.g., specific `word_count_threshold`).
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "urls": ["https://example.com"],
    "crawler_config": {
        "word_count_threshold": 50, # Only process content blocks with more than 50 words
        "screenshot": True # Also take a screenshot
    }
}

try:
    response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
    response.raise_for_status()
    job_data = response.json()
    task_id = job_data.get("task_id")
    if task_id:
        print(f"Crawl job with custom crawler_config submitted. Task ID: {task_id}")
    else:
        print(f"Failed to submit job: {job_data}")
except requests.exceptions.RequestException as e:
    print(f"Error submitting crawl job with custom crawler_config: {e}")
```

##### B.1.5. Example: Submitting a job that uses a specific `CacheMode` (e.g., `BYPASS`).
`CacheMode` values are typically: "DISABLED", "ENABLED", "BYPASS", "READ_ONLY", "WRITE_ONLY".
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "urls": ["https://example.com"],
    "crawler_config": {
        "cache_mode": "BYPASS" # Force a fresh crawl, ignore existing cache, don't write to cache
    }
}

try:
    response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
    response.raise_for_status()
    job_data = response.json()
    task_id = job_data.get("task_id")
    if task_id:
        print(f"Crawl job with CacheMode.BYPASS submitted. Task ID: {task_id}")
    else:
        print(f"Failed to submit job: {job_data}")
except requests.exceptions.RequestException as e:
    print(f"Error submitting crawl job with CacheMode.BYPASS: {e}")
```

##### B.1.6. Example: Submitting a job to extract PDF content from a URL.
(This assumes the URL points directly to a PDF or the page leads to a PDF download that the crawler handles).
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

# URL of a sample PDF file
pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

payload = {
    "urls": [pdf_url],
    "crawler_config": {
        # Crawl4ai should auto-detect PDF content type and use appropriate processor
        "pdf": True # Explicitly enabling PDF processing, though often auto-detected
    }
}

try:
    response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
    response.raise_for_status()
    job_data = response.json()
    task_id = job_data.get("task_id")
    if task_id:
        print(f"PDF crawl job submitted for {pdf_url}. Task ID: {task_id}")
        print(f"Poll status at: {BASE_URL}/task/{task_id}")
    else:
        print(f"Failed to submit PDF crawl job: {job_data}")
except requests.exceptions.RequestException as e:
    print(f"Error submitting PDF crawl job: {e}")
```

##### B.1.7. Example: Submitting a job to take a screenshot from a URL.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "urls": ["https://example.com"],
    "crawler_config": {
        "screenshot": True,
        "screenshot_wait_for": 2 # wait 2 seconds after page load before screenshot
    }
}

try:
    response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
    response.raise_for_status()
    job_data = response.json()
    task_id = job_data.get("task_id")
    if task_id:
        print(f"Screenshot job submitted for example.com. Task ID: {task_id}")
        print(f"Poll status at: {BASE_URL}/task/{task_id}")
    else:
        print(f"Failed to submit screenshot job: {job_data}")
except requests.exceptions.RequestException as e:
    print(f"Error submitting screenshot job: {e}")
```

---
#### B.2. `/task/{task_id}` (Job Status and Results)

##### B.2.1. Example: Python script to poll the `/task/{task_id}` endpoint for PENDING status.
```python
import requests
import time
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

# Assume task_id is obtained from a previous /crawl request
# For this example, we'll submit a quick job first
submit_payload = {"urls": ["http://example.com/nonexistent-page-for-quick-fail-or-processing"]}
task_id = None
try:
    submit_response = requests.post(f"{BASE_URL}/crawl", json=submit_payload, headers=headers)
    submit_response.raise_for_status()
    task_id = submit_response.json().get("task_id")
except requests.exceptions.RequestException as e:
    print(f"Failed to submit initial job for polling example: {e}")

if task_id:
    print(f"Polling for task: {task_id}")
    for _ in range(5): # Poll a few times
        try:
            status_response = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            print(f"Current status: {status_data.get('status')}")
            if status_data.get('status') in ["COMPLETED", "FAILED"]:
                break
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"Error polling task status: {e}")
            break
else:
    print("No task ID to poll.")
```

##### B.2.2. Example: Python script to retrieve results for a COMPLETED job.
```python
import requests
import time
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

# Submit a job that should complete successfully
submit_payload = {"urls": ["https://example.com"]}
task_id = None
try:
    submit_response = requests.post(f"{BASE_URL}/crawl", json=submit_payload, headers=headers)
    submit_response.raise_for_status()
    task_id = submit_response.json().get("task_id")
except requests.exceptions.RequestException as e:
    print(f"Failed to submit job for result retrieval example: {e}")


if task_id:
    print(f"Waiting for task {task_id} to complete...")
    while True:
        try:
            status_response = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            current_status = status_data.get('status')
            print(f"Task status: {current_status}")

            if current_status == "COMPLETED":
                print("\nJob COMPLETED. Results:")
                # The 'result' field contains the JSON string of the CrawlResult model(s)
                # For a single URL job, it's typically a dict. For multiple, a list of dicts.
                # The structure from api.py suggests `result` field in Redis is a JSON string
                # of a dictionary which itself contains a 'results' key (list of CrawlResult dicts).
                
                # This is based on how handle_crawl_job in api.py stores results
                # and how the /task/{task_id} endpoint decodes it.
                # The 'result' from /task/{task_id} should already be a parsed dict.
                
                crawl_results_wrapper = status_data.get("result")
                if crawl_results_wrapper and "results" in crawl_results_wrapper:
                    actual_results = crawl_results_wrapper["results"]
                    for i, res_item in enumerate(actual_results):
                        print(f"\n--- Result for URL {i+1} ({res_item.get('url', 'N/A')}) ---")
                        print(f"  Success: {res_item.get('success')}")
                        print(f"  Markdown (first 100 chars): {res_item.get('markdown', {}).get('raw_markdown', '')[:100]}...")
                        if res_item.get('screenshot'):
                             print("  Screenshot captured (base64 data not printed).")
                else:
                     print(f"Unexpected result structure: {crawl_results_wrapper}")
                break
            elif current_status == "FAILED":
                print(f"\nJob FAILED. Error: {status_data.get('error')}")
                break
            
            time.sleep(3) # Poll every 3 seconds
        except requests.exceptions.RequestException as e:
            print(f"Error polling task status: {e}")
            break
        except KeyboardInterrupt:
            print("\nPolling interrupted.")
            break
else:
    print("No task ID to retrieve results for.")

```

##### B.2.3. Example: Python script to get error details for a FAILED job.
```python
import requests
import time
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

# Submit a job that is likely to fail (e.g., invalid URL or one that times out quickly)
submit_payload = {"urls": ["http://nonexistentdomain1234567890.com"]}
task_id = None
try:
    submit_response = requests.post(f"{BASE_URL}/crawl", json=submit_payload, headers=headers)
    submit_response.raise_for_status()
    task_id = submit_response.json().get("task_id")
except requests.exceptions.RequestException as e:
    print(f"Failed to submit job for failure example: {e}")

if task_id:
    print(f"Waiting for task {task_id} (expected to fail)...")
    while True:
        try:
            status_response = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            current_status = status_data.get('status')
            print(f"Task status: {current_status}")

            if current_status == "FAILED":
                print("\nJob FAILED as expected.")
                error_message = status_data.get('error', 'No error message provided.')
                print(f"Error details: {error_message}")
                break
            elif current_status == "COMPLETED":
                print("\nJob COMPLETED unexpectedly.")
                break
            
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"Error polling task status: {e}")
            break
        except KeyboardInterrupt:
            print("\nPolling interrupted.")
            break
else:
    print("No task ID to check for failure.")
```

##### B.2.4. Example: Full workflow - submit job, poll status, retrieve results or error.
This combines the above examples into a more complete client script.
```python
import requests
import time
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

def submit_and_poll(payload, timeout_seconds=60):
    task_id = None
    try:
        # Submit the job
        print(f"Submitting job with payload: {payload}")
        submit_response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
        submit_response.raise_for_status()
        task_id = submit_response.json().get("task_id")
        if not task_id:
            print("Error: No task_id received.")
            return None
        print(f"Job submitted. Task ID: {task_id}. Polling for completion...")

        # Poll for status
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            status_response = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            current_status = status_data.get('status')
            print(f"  Task {task_id} status: {current_status} (elapsed: {time.time() - start_time:.1f}s)")

            if current_status == "COMPLETED":
                print(f"Task {task_id} COMPLETED.")
                return status_data.get("result") # This should be the parsed JSON result
            elif current_status == "FAILED":
                print(f"Task {task_id} FAILED.")
                print(f"Error: {status_data.get('error')}")
                return None
            time.sleep(5) # Poll interval
        
        print(f"Task {task_id} timed out after {timeout_seconds} seconds.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    crawl_payload = {
        "urls": ["https://www.python.org/about/"],
        "crawler_config": {"screenshot": False}
    }
    results_data = submit_and_poll(crawl_payload)

    if results_data and "results" in results_data:
        for i, res_item in enumerate(results_data["results"]):
            print(f"\n--- Result for URL {res_item.get('url', 'N/A')} ---")
            print(f"  Success: {res_item.get('success')}")
            print(f"  Markdown (first 200 chars): {res_item.get('markdown', {}).get('raw_markdown', '')[:200]}...")
    elif results_data: # If result isn't in the expected wrapper structure
        print(f"\nReceived result data (unexpected structure):")
        print(json.dumps(results_data, indent=2, ensure_ascii=False))

```

---
#### B.3. `/crawl/stream` (Streaming Crawl Results)

##### B.3.1. Example: Python script to stream crawl results for a single URL and process NDJSON.
```python
import requests
import json
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()
headers['Accept'] = 'application/x-ndjson' # Important for streaming

payload = {
    "urls": ["https://example.com"],
    "crawler_config": {"stream": True} # Ensure stream is True in config
}

print(f"Streaming results for {payload['urls'][0]}...")
try:
    with requests.post(f"{BASE_URL}/crawl/stream", json=payload, headers=headers, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                try:
                    result_chunk = json.loads(line.decode('utf-8'))
                    if "status" in result_chunk and result_chunk["status"] == "completed":
                        print("\nStream finished.")
                        break
                    print("\nReceived chunk:")
                    # Print some key info from the chunk
                    print(f"  URL: {result_chunk.get('url', 'N/A')}")
                    print(f"  Success: {result_chunk.get('success')}")
                    if 'markdown' in result_chunk and isinstance(result_chunk['markdown'], dict):
                         print(f"  Markdown (snippet): {result_chunk['markdown'].get('raw_markdown', '')[:100]}...")
                    else:
                         print(f"  Markdown (snippet): {str(result_chunk.get('markdown', ''))[:100]}...")
                    if result_chunk.get('error_message'):
                        print(f"  Error: {result_chunk.get('error_message')}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON line: {e} - Line: {line.decode('utf-8')}")
except requests.exceptions.RequestException as e:
    print(f"Error during streaming request: {e}")

```

##### B.3.2. Example: Python script to stream crawl results for multiple URLs.
```python
import requests
import json
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()
headers['Accept'] = 'application/x-ndjson'

payload = {
    "urls": ["https://example.com", "https://www.python.org/doc/"],
    "crawler_config": {"stream": True}
}

print(f"Streaming results for multiple URLs...")
try:
    with requests.post(f"{BASE_URL}/crawl/stream", json=payload, headers=headers, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                try:
                    result_chunk = json.loads(line.decode('utf-8'))
                    if "status" in result_chunk and result_chunk["status"] == "completed":
                        print("\nStream finished for all URLs.")
                        break
                    print(f"\nChunk for URL: {result_chunk.get('url', 'N/A')}")
                    # Process or display part of the result
                    print(f"  Success: {result_chunk.get('success')}")
                    if 'markdown' in result_chunk and isinstance(result_chunk['markdown'], dict):
                         print(f"  Markdown (snippet): {result_chunk['markdown'].get('raw_markdown', '')[:70]}...")
                    else:
                         print(f"  Markdown (snippet): {str(result_chunk.get('markdown', ''))[:70]}...")

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON line: {e} - Line: {line.decode('utf-8')}")
except requests.exceptions.RequestException as e:
    print(f"Error during streaming request: {e}")
```

##### B.3.3. Example: Streaming crawl results with custom `browser_config` and `crawler_config`.
```python
import requests
import json
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()
headers['Accept'] = 'application/x-ndjson'

payload = {
    "urls": ["https://example.com"],
    "browser_config": {
        "headless": True,
        "user_agent": "Crawl4AI-Stream-Tester/1.0"
    },
    "crawler_config": {
        "stream": True,
        "word_count_threshold": 10 # Lower threshold for this example
    }
}

print(f"Streaming results with custom configs for {payload['urls'][0]}...")
try:
    with requests.post(f"{BASE_URL}/crawl/stream", json=payload, headers=headers, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                result_chunk = json.loads(line.decode('utf-8'))
                if "status" in result_chunk and result_chunk["status"] == "completed":
                    print("\nStream finished.")
                    break
                print("\nReceived chunk with custom config:")
                print(f"  URL: {result_chunk.get('url')}")
                print(f"  Word count threshold was: {payload['crawler_config']['word_count_threshold']}")
                if 'markdown' in result_chunk and isinstance(result_chunk['markdown'], dict):
                     print(f"  Markdown (snippet): {result_chunk['markdown'].get('raw_markdown', '')[:70]}...")
                else:
                     print(f"  Markdown (snippet): {str(result_chunk.get('markdown', ''))[:70]}...")
except requests.exceptions.RequestException as e:
    print(f"Error during streaming request: {e}")
```

##### B.3.4. Example: Handling connection closure or errors during streaming.
```python
import requests
import json
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()
headers['Accept'] = 'application/x-ndjson'

payload = {
    "urls": ["https://thissitedoesnotexist12345.com", "https://example.com"], # First URL will fail
    "crawler_config": {"stream": True}
}

print(f"Streaming with a URL expected to fail...")
try:
    with requests.post(f"{BASE_URL}/crawl/stream", json=payload, headers=headers, stream=True) as response:
        # We might not get a non-200 status code immediately if the connection itself is established
        # Errors for individual URLs will be part of the NDJSON stream
        for line in response.iter_lines():
            if line:
                try:
                    result_chunk = json.loads(line.decode('utf-8'))
                    print(f"\nReceived data: {result_chunk.get('url', 'N/A')}")
                    if "status" in result_chunk and result_chunk["status"] == "completed":
                        print("Stream finished.")
                        break
                    if result_chunk.get('error_message'):
                        print(f"  ERROR for {result_chunk.get('url')}: {result_chunk.get('error_message')}")
                    elif result_chunk.get('success'):
                        print(f"  SUCCESS for {result_chunk.get('url')}")
                except json.JSONDecodeError as e:
                    print(f"  Error decoding JSON line: {e}")
except requests.exceptions.ChunkedEncodingError:
    print("Connection closed unexpectedly by server during streaming (ChunkedEncodingError).")
except requests.exceptions.RequestException as e:
    print(f"General error during streaming request: {e}")
```

---
### C. Content Transformation & Utility Endpoints

#### C.1. `/md` (Markdown Generation)

##### C.1.1. Example: Getting raw Markdown for a URL (default filter).
The default filter is `FIT` if no filter is specified.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {"url": "https://example.com", "f": "RAW"} # 'f' is for filter_type
try:
    response = requests.post(f"{BASE_URL}/md", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Markdown (RAW filter - first 300 chars):")
    print(data.get("markdown", "")[:300] + "...")
except requests.exceptions.RequestException as e:
    print(f"Error fetching Markdown: {e}")
```

##### C.1.2. Example: Getting Markdown using the `FIT` filter type.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {"url": "https://example.com", "f": "FIT"}
try:
    response = requests.post(f"{BASE_URL}/md", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Markdown (FIT filter - first 300 chars):")
    print(data.get("markdown", "")[:300] + "...")
except requests.exceptions.RequestException as e:
    print(f"Error fetching Markdown: {e}")
```

##### C.1.3. Example: Getting Markdown using the `BM25` filter type with a specific query.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)", 
    "f": "BM25",
    "q": "What are the key features of Python?" # Query for BM25 filtering
}
try:
    response = requests.post(f"{BASE_URL}/md", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(f"Markdown (BM25 filter, query='{payload['q']}' - first 300 chars):")
    print(data.get("markdown", "")[:300] + "...")
except requests.exceptions.RequestException as e:
    print(f"Error fetching Markdown: {e}")
```

##### C.1.4. Example: Getting Markdown using the `LLM` filter type with a query (conceptual, requires LLM setup).
This requires an LLM provider (like OpenAI) to be configured in `config.yml` or via environment variables loaded by the server.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "f": "LLM",
    "q": "Summarize the history of Python" # Query for LLM to focus on
}
print("Attempting LLM-filtered Markdown (this may take a moment and requires LLM config)...")
try:
    # LLM requests can take longer
    response = requests.post(f"{BASE_URL}/md", json=payload, headers=headers, timeout=120) 
    response.raise_for_status()
    data = response.json()
    print(f"Markdown (LLM filter, query='{payload['q']}' - first 300 chars):")
    print(data.get("markdown", "")[:300] + "...")
except requests.exceptions.RequestException as e:
    print(f"Error fetching LLM-filtered Markdown: {e}")
    print("Ensure your LLM provider (e.g., OPENAI_API_KEY) is configured for the server.")
```

##### C.1.5. Example: Demonstrating cache usage with the `/md` endpoint (`c` parameter).
The `c` parameter can be "0" (bypass write, read if available - effectively WRITE_ONLY for this endpoint if no cache exists), "1" (force refresh, write - effectively ENABLED for this endpoint), or other numbers for revision control (not shown here).
```python
import requests
import os
import json
import time

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()
test_url = "https://example.com"

# First call: cache miss, should fetch and write to cache
print("First call (cache_mode=ENABLED implied by 'c=1', or default if 'c' omitted)")
payload1 = {"url": test_url, "f": "RAW", "c": "1"} # c="1" forces refresh and writes
start_time = time.time()
response1 = requests.post(f"{BASE_URL}/md", json=payload1, headers=headers)
duration1 = time.time() - start_time
response1.raise_for_status()
print(f"First call duration: {duration1:.2f}s. Markdown length: {len(response1.json().get('markdown', ''))}")

# Second call: should be a cache hit if c="0" or c is omitted and cache is fresh
print("\nSecond call (cache_mode=READ_ONLY implied by 'c=0', or default if 'c' omitted and cache fresh)")
payload2 = {"url": test_url, "f": "RAW", "c": "0"} # c="0" attempts to read from cache
start_time = time.time()
response2 = requests.post(f"{BASE_URL}/md", json=payload2, headers=headers)
duration2 = time.time() - start_time
response2.raise_for_status()
print(f"Second call duration: {duration2:.2f}s. Markdown length: {len(response2.json().get('markdown', ''))}")

if duration2 < duration1 / 2 and duration1 > 0.1 : # Heuristic for cache hit
    print("Second call was significantly faster, likely a cache hit.")
else:
    print("Cache behavior inconclusive or first call was very fast.")
```

---
#### C.2. `/html` (Preprocessed HTML)

##### C.2.1. Example: Fetching preprocessed HTML for a URL suitable for schema extraction.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {"url": "https://example.com"}
try:
    response = requests.post(f"{BASE_URL}/html", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Preprocessed HTML (first 500 chars):")
    print(data.get("html", "")[:500] + "...")
    print(f"\nOriginal URL: {data.get('url')}")
except requests.exceptions.RequestException as e:
    print(f"Error fetching preprocessed HTML: {e}")
```

---
#### C.3. `/screenshot`

##### C.3.1. Example: Generating a PNG screenshot for a URL and receiving base64 data.
```python
import requests
import os
import base64
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {"url": "https://example.com"}
try:
    response = requests.post(f"{BASE_URL}/screenshot", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data.get("screenshot"):
        print("Screenshot received (base64 data).")
        # To save the image:
        # image_data = base64.b64decode(data["screenshot"])
        # with open("example_screenshot.png", "wb") as f:
        #     f.write(image_data)
        # print("Screenshot saved as example_screenshot.png")
    else:
        print(f"Screenshot generation failed or no data returned: {data}")
except requests.exceptions.RequestException as e:
    print(f"Error generating screenshot: {e}")
```

##### C.3.2. Example: Generating a screenshot with a custom `screenshot_wait_for` delay.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "url": "https://example.com",
    "screenshot_wait_for": 3  # Wait 3 seconds after page load
}
try:
    response = requests.post(f"{BASE_URL}/screenshot", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data.get("screenshot"):
        print(f"Screenshot with {payload['screenshot_wait_for']}s delay received.")
    else:
        print(f"Screenshot generation failed: {data}")
except requests.exceptions.RequestException as e:
    print(f"Error generating screenshot with delay: {e}")
```

##### C.3.3. Example: Saving screenshot to server-side path via `output_path`.
**Note:** This requires `output_path` to be a path accessible and writable by the server process. For Docker, this usually means a mounted volume.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

# This path needs to be valid from the server's perspective
# e.g., if running in Docker, it might be a path inside the container
# that is mapped to a host volume.
server_side_path = "/app/screenshots/example_com.png" # Example path

payload = {
    "url": "https://example.com",
    "output_path": server_side_path
}
try:
    response = requests.post(f"{BASE_URL}/screenshot", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data.get("success") and data.get("path"):
        print(f"Screenshot successfully saved to server path: {data.get('path')}")
        print("Note: This file is on the server, not the client machine unless paths are mapped.")
    else:
        print(f"Failed to save screenshot to server: {data}")
except requests.exceptions.RequestException as e:
    print(f"Error saving screenshot to server: {e}")
```

---
#### C.4. `/pdf`

##### C.4.1. Example: Generating a PDF for a URL and receiving base64 data.
```python
import requests
import os
import base64
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {"url": "https://example.com"}
try:
    response = requests.post(f"{BASE_URL}/pdf", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data.get("pdf"):
        print("PDF received (base64 data).")
        # To save the PDF:
        # pdf_data = base64.b64decode(data["pdf"])
        # with open("example_page.pdf", "wb") as f:
        #     f.write(pdf_data)
        # print("PDF saved as example_page.pdf")
    else:
        print(f"PDF generation failed or no data returned: {data}")
except requests.exceptions.RequestException as e:
    print(f"Error generating PDF: {e}")
```

##### C.4.2. Example: Saving PDF to server-side path via `output_path`.
**Note:** Similar to screenshots, `output_path` must be server-accessible.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

server_side_path = "/app/pdfs/example_com.pdf" # Example path

payload = {
    "url": "https://example.com",
    "output_path": server_side_path
}
try:
    response = requests.post(f"{BASE_URL}/pdf", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data.get("success") and data.get("path"):
        print(f"PDF successfully saved to server path: {data.get('path')}")
    else:
        print(f"Failed to save PDF to server: {data}")
except requests.exceptions.RequestException as e:
    print(f"Error saving PDF to server: {e}")

```

---
#### C.5. `/execute_js`

##### C.5.1. Example: Executing a simple JavaScript snippet (e.g., `return document.title;`) on a page.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "url": "https://example.com",
    "scripts": ["return document.title;"]
}
try:
    response = requests.post(f"{BASE_URL}/execute_js", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json() # This is the full CrawlResult model as JSON
    print("Full CrawlResult from /execute_js:")
    # print(json.dumps(data, indent=2, ensure_ascii=False)) # Can be very long
    
    js_results = data.get("js_execution_result")
    if js_results and js_results.get("script_0"):
        print(f"\nResult of script 0 (document.title): {js_results['script_0']}")
    else:
        print(f"\nCould not find JS execution result: {js_results}")

except requests.exceptions.RequestException as e:
    print(f"Error executing JS: {e}")
```

##### C.5.2. Example: Executing multiple JavaScript snippets sequentially.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "url": "https://example.com",
    "scripts": [
        "return document.title;",
        "return document.querySelectorAll('p').length;",
        "() => { const h1 = document.querySelector('h1'); return h1 ? h1.innerText : 'No H1'; }()"
    ]
}
try:
    response = requests.post(f"{BASE_URL}/execute_js", json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    js_results = data.get("js_execution_result")
    if js_results:
        print("\nResults of JS snippets:")
        print(f"  Script 0 (Title): {js_results.get('script_0')}")
        print(f"  Script 1 (Paragraph count): {js_results.get('script_1')}")
        print(f"  Script 2 (H1 text): {js_results.get('script_2')}")
    else:
        print(f"\nCould not find JS execution results: {js_results}")

except requests.exceptions.RequestException as e:
    print(f"Error executing multiple JS snippets: {e}")
```

##### C.5.3. Example: Demonstrating how the full `CrawlResult` (JSON of model) is returned.
The `/execute_js` endpoint returns the entire `CrawlResult` object, serialized to JSON. This includes HTML, Markdown, links, etc., in addition to the `js_execution_result`.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

payload = {
    "url": "https://example.com",
    "scripts": ["return window.location.href;"]
}
try:
    response = requests.post(f"{BASE_URL}/execute_js", json=payload, headers=headers)
    response.raise_for_status()
    crawl_result_data = response.json()
    
    print("Demonstrating full CrawlResult structure from /execute_js:")
    print(f"  URL crawled: {crawl_result_data.get('url')}")
    print(f"  Success: {crawl_result_data.get('success')}")
    print(f"  HTML (snippet): {crawl_result_data.get('html', '')[:100]}...")
    if isinstance(crawl_result_data.get('markdown'), dict):
        print(f"  Markdown (snippet): {crawl_result_data['markdown'].get('raw_markdown', '')[:100]}...")
    else:
        print(f"  Markdown (snippet): {str(crawl_result_data.get('markdown', ''))[:100]}...")

    js_result = crawl_result_data.get("js_execution_result", {}).get("script_0")
    print(f"  Result of JS (window.location.href): {js_result}")

except requests.exceptions.RequestException as e:
    print(f"Error demonstrating full CrawlResult: {e}")
```

---
### D. Contextual Endpoints

#### D.1. `/ask` (RAG-like Context Retrieval)
The `/ask` endpoint uses local Markdown files (`c4ai-code-context.md` and `c4ai-doc-context.md`, which should be in the same directory as `server.py`) for retrieval.

##### D.1.1. Example: Asking a general question to retrieve "code" context.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

params = {
    "context_type": "code",
    "query": "How to handle Playwright installation?" # General query
}
try:
    response = requests.get(f"{BASE_URL}/ask", params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Retrieved 'code' context for 'How to handle Playwright installation?':")
    if "code_results" in data:
        for i, item in enumerate(data["code_results"][:2]): # Show first 2 results
            print(f"\n--- Code Result {i+1} (Score: {item.get('score', 'N/A'):.2f}) ---")
            print(item.get("text", "")[:300] + "...")
    else:
        print(json.dumps(data, indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error asking for code context: {e}")
```

##### D.1.2. Example: Asking a general question to retrieve "doc" context.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

params = {
    "context_type": "doc",
    "query": "Explain Crawl4ai API endpoints"
}
try:
    response = requests.get(f"{BASE_URL}/ask", params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Retrieved 'doc' context for 'Explain Crawl4ai API endpoints':")
    if "doc_results" in data:
        for i, item in enumerate(data["doc_results"][:2]):
            print(f"\n--- Doc Result {i+1} (Score: {item.get('score', 'N/A'):.2f}) ---")
            print(item.get("text", "")[:300] + "...")
    else:
        print(json.dumps(data, indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error asking for doc context: {e}")
```

##### D.1.3. Example: Using the `query` parameter to filter context related to a specific function.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

params = {
    "context_type": "all", # Search both code and docs
    "query": "AsyncWebCrawler arun method"
}
try:
    response = requests.get(f"{BASE_URL}/ask", params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(f"Retrieved 'all' context for query: '{params['query']}'")
    if "code_results" in data:
        print(f"\nFound {len(data['code_results'])} code results.")
        # Optionally print snippets
    if "doc_results" in data:
        print(f"Found {len(data['doc_results'])} doc results.")
        # Optionally print snippets
    # print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
except requests.exceptions.RequestException as e:
    print(f"Error asking with specific query: {e}")

```

##### D.1.4. Example: Adjusting `score_ratio` to change result sensitivity.
A lower `score_ratio` (e.g., 0.1) will return more, less relevant results. A higher one (e.g., 0.8) will be more strict. Default is 0.5.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

params_strict = {
    "context_type": "code",
    "query": "Playwright browser installation",
    "score_ratio": 0.8 # Higher, more strict
}
params_loose = {
    "context_type": "code",
    "query": "Playwright browser installation",
    "score_ratio": 0.2 # Lower, less strict
}

try:
    response_strict = requests.get(f"{BASE_URL}/ask", params=params_strict, headers=headers)
    response_strict.raise_for_status()
    data_strict = response_strict.json()
    print(f"Results with score_ratio=0.8: {len(data_strict.get('code_results', []))}")

    response_loose = requests.get(f"{BASE_URL}/ask", params=params_loose, headers=headers)
    response_loose.raise_for_status()
    data_loose = response_loose.json()
    print(f"Results with score_ratio=0.2: {len(data_loose.get('code_results', []))}")

except requests.exceptions.RequestException as e:
    print(f"Error adjusting score_ratio: {e}")
```

##### D.1.5. Example: Limiting results with `max_results`.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

params = {
    "context_type": "doc",
    "query": "crawl4ai features",
    "max_results": 3 # Limit to top 3 results
}
try:
    response = requests.get(f"{BASE_URL}/ask", params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(f"Retrieved max {params['max_results']} doc_results for 'crawl4ai features':")
    if "doc_results" in data:
        print(f"Actual results returned: {len(data['doc_results'])}")
        for item in data["doc_results"]:
            print(f"  - Score: {item.get('score', 0):.2f}, Text (snippet): {item.get('text', '')[:50]}...")
    else:
        print("No doc_results found.")
except requests.exceptions.RequestException as e:
    print(f"Error limiting results: {e}")
```

---
### E. Server & Configuration Information

#### E.1. `/config/dump`

##### E.1.1. Example: Dumping a `CrawlerRunConfig` Python object representation to its JSON equivalent via the API.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

# This is a Python-style string representation of a CrawlerRunConfig
# that the server's _safe_eval_config can parse.
config_string = "CrawlerRunConfig(word_count_threshold=50, screenshot=True, cache_mode=CacheMode.BYPASS)"

payload = {"code": config_string}
try:
    response = requests.post(f"{BASE_URL}/config/dump", json=payload, headers=headers)
    response.raise_for_status()
    dumped_json = response.json()
    print("Dumped CrawlerRunConfig JSON:")
    print(json.dumps(dumped_json, indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error dumping CrawlerRunConfig: {e}")
```

##### E.1.2. Example: Dumping a `BrowserConfig` Python object representation to its JSON equivalent via the API.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

config_string = "BrowserConfig(headless=False, user_agent='MyTestAgent/1.0')"
payload = {"code": config_string}
try:
    response = requests.post(f"{BASE_URL}/config/dump", json=payload, headers=headers)
    response.raise_for_status()
    dumped_json = response.json()
    print("Dumped BrowserConfig JSON:")
    print(json.dumps(dumped_json, indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error dumping BrowserConfig: {e}")
```

##### E.1.3. Example: Attempting to dump an invalid or non-serializable configuration string.
```python
import requests
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

# Invalid: not a recognized Crawl4AI config class
invalid_config_string = "MyCustomClass(param=1)"
payload = {"code": invalid_config_string}
try:
    response = requests.post(f"{BASE_URL}/config/dump", json=payload, headers=headers)
    if response.status_code == 400:
        print(f"Correctly failed to dump invalid config string. Server response: {response.json()}")
    else:
        print(f"Unexpected response for invalid config: {response.status_code} - {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error attempting to dump invalid config: {e}")

# Invalid: nested function call (security restriction)
unsafe_config_string = "CrawlerRunConfig(word_count_threshold=__import__('os').system('echo unsafe'))"
payload_unsafe = {"code": unsafe_config_string}
try:
    response_unsafe = requests.post(f"{BASE_URL}/config/dump", json=payload_unsafe, headers=headers)
    if response_unsafe.status_code == 400:
        print(f"Correctly failed to dump unsafe config string. Server response: {response_unsafe.json()}")
    else:
        print(f"Unexpected response for unsafe config: {response_unsafe.status_code} - {response_unsafe.text}")
except requests.exceptions.RequestException as e:
    print(f"Error attempting to dump unsafe config: {e}")
```

---
#### E.2. `/schema`

##### E.2.1. Example: Fetching the default JSON schemas for `BrowserConfig` and `CrawlerRunConfig`.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

try:
    response = requests.get(f"{BASE_URL}/schema", headers=headers)
    response.raise_for_status()
    schemas = response.json()
    
    print("BrowserConfig Schema (sample):")
    # print(json.dumps(schemas.get("browser"), indent=2)) # Full schema can be long
    if "browser" in schemas and "properties" in schemas["browser"]:
        print(f"  BrowserConfig has {len(schemas['browser']['properties'])} properties.")
        print(f"  Example property 'headless': {schemas['browser']['properties'].get('headless')}")

    print("\nCrawlerRunConfig Schema (sample):")
    # print(json.dumps(schemas.get("crawler"), indent=2))
    if "crawler" in schemas and "properties" in schemas["crawler"]:
        print(f"  CrawlerRunConfig has {len(schemas['crawler']['properties'])} properties.")
        print(f"  Example property 'word_count_threshold': {schemas['crawler']['properties'].get('word_count_threshold')}")

except requests.exceptions.RequestException as e:
    print(f"Error fetching schemas: {e}")
```

---
#### E.3. `/health` & `/metrics`

##### E.3.1. Example: Python script to programmatically check the `/health` endpoint.
(Similar to example 2.4.1, but reiterated here for completeness of this section)
```python
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

try:
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    response.raise_for_status()
    health_data = response.json()
    print("Health Check:")
    print(f"  Status: {health_data.get('status')}")
    print(f"  Version: {health_data.get('version')}")
    ts = health_data.get('timestamp')
    if ts:
        print(f"  Timestamp: {ts} (UTC: {datetime.utcfromtimestamp(ts).isoformat()})")
except requests.exceptions.RequestException as e:
    print(f"Error checking health: {e}")
```

##### E.3.2. Example: Accessing Prometheus metrics at `/metrics` (assuming Prometheus is enabled in `config.yml`).
This typically involves pointing a Prometheus scraper at the endpoint or manually fetching.
```python
import requests
import os

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
# Prometheus metrics are usually at /metrics, but the server.py config uses
# config["observability"]["prometheus"]["endpoint"] which defaults to "/metrics"
METRICS_ENDPOINT = "/metrics" # As per default config.yml
headers = get_headers()

try:
    # First, check if Prometheus is enabled in the server's config
    # This is a conceptual check, real check depends on your setup
    config_response = requests.get(f"{BASE_URL}/health", headers=headers) # Health often includes version
    # In a real scenario, you might have an endpoint to get active config or infer from behavior

    print(f"Attempting to fetch metrics from {BASE_URL}{METRICS_ENDPOINT}")
    response = requests.get(f"{BASE_URL}{METRICS_ENDPOINT}", headers=headers)
    if response.status_code == 200:
        print("Prometheus metrics response (first 500 chars):")
        print(response.text[:500] + "...")
    elif response.status_code == 404:
        print(f"Metrics endpoint {METRICS_ENDPOINT} not found. Ensure Prometheus is enabled in config.yml.")
    else:
        print(f"Error fetching metrics: {response.status_code} - {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Error connecting to metrics endpoint: {e}")
```
**Note:** For this to work, `observability.prometheus.enabled` must be `true` in the server's `config.yml`.

---
## IV. Configuring the Deployment (via `config.yml`)

### 4.1. Note: These examples primarily show snippets of `config.yml` and describe their effect, rather than Python code to modify the live configuration.
The `config.yml` file is read by the server on startup. Changes typically require a server restart.

### 4.2. Rate Limiting Configuration

#### 4.2.1. Example `config.yml` snippet: Enabling rate limiting with a custom limit (e.g., "10/second").
```yaml
# In your config.yml
rate_limiting:
  enabled: true
  default_limit: "10/second" # Allows 10 requests per second per client IP
  # trusted_proxies: ["127.0.0.1"] # If behind a reverse proxy
```

#### 4.2.2. Example `config.yml` snippet: Using Redis as a storage backend for rate limiting.
This is recommended for production if you have multiple server instances.
```yaml
# In your config.yml
rate_limiting:
  enabled: true
  default_limit: "1000/minute"
  storage_uri: "redis://localhost:6379" # Or your Redis server URI
  # Ensure your Redis server is running and accessible
```

---
### 4.3. Security Settings Configuration

#### 4.3.1. Example `config.yml` snippet: Enabling JWT authentication.
```yaml
# In your config.yml
security:
  enabled: true
  jwt_enabled: true
  # jwt_secret_key: "YOUR_VERY_SECRET_KEY" # Auto-generated if not set
  # jwt_algorithm: "HS256"
  # jwt_access_token_expire_minutes: 30
  # jwt_allowed_email_domains: ["example.com", "another.org"] # Optional: Restrict token issuance
```
**Note:** Enabling `jwt_enabled` means endpoints decorated with the token dependency will require authentication.

#### 4.3.2. Example `config.yml` snippet: Enabling HTTPS redirect.
This is useful if your server is behind a reverse proxy that handles TLS termination.
```yaml
# In your config.yml
security:
  enabled: true
  https_redirect: true # Adds middleware to redirect HTTP to HTTPS
```

#### 4.3.3. Example `config.yml` snippet: Setting custom trusted hosts.
Restricts which `Host` headers are accepted. Use `["*"]` to allow all (less secure).
```yaml
# In your config.yml
security:
  enabled: true
  trusted_hosts: ["api.example.com", "localhost", "127.0.0.1"]
```

#### 4.3.4. Example `config.yml` snippet: Configuring custom HTTP security headers (CSP, X-Frame-Options).
```yaml
# In your config.yml
security:
  enabled: true
  headers:
    x_content_type_options: "nosniff"
    x_frame_options: "DENY"
    content_security_policy: "default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none';"
    strict_transport_security: "max-age=31536000; includeSubDomains"
```

---
### 4.4. LLM Provider Configuration

#### 4.4.1. Example `config.yml` snippet: Setting the default LLM provider and API key env variable.
```yaml
# In your config.yml
llm:
  provider: "openai/gpt-4o-mini" # Default provider/model
  api_key_env: "OPENAI_API_KEY"  # Environment variable to read the API key from
```
The server will then expect the `OPENAI_API_KEY` environment variable to be set.

#### 4.4.2. Example `config.yml` snippet: Overriding the API key directly in the config (for testing/specific cases).
**Warning:** Not recommended for production due to security risks of hardcoding keys.
```yaml
# In your config.yml
llm:
  provider: "openai/gpt-3.5-turbo"
  api_key: "sk-this_is_a_test_key_do_not_use_in_prod" # Key directly in config
```

#### 4.4.3. Example `config.yml` snippet: Configuring for a different LiteLLM-supported provider (e.g., Groq).
```yaml
# In your config.yml
llm:
  provider: "groq/llama3-8b-8192"
  api_key_env: "GROQ_API_KEY" # Server will look for this env var
```

---
### 4.5. Default Crawler Settings
These settings in `config.yml` under the `crawler` key affect the default behavior if not overridden by specific `BrowserConfig` or `CrawlerRunConfig` in API requests.

#### 4.5.1. Example `config.yml` snippet: Modifying `crawler.base_config.simulate_user`.
```yaml
# In your config.yml
crawler:
  base_config:
    simulate_user: true # Enable user simulation features by default
```

#### 4.5.2. Example `config.yml` snippet: Adjusting `crawler.memory_threshold_percent`.
This is for the `MemoryAdaptiveDispatcher`.
```yaml
# In your config.yml
crawler:
  memory_threshold_percent: 85.0 # Pause new tasks if system memory usage exceeds 85%
```

#### 4.5.3. Example `config.yml` snippet: Configuring default `crawler.rate_limiter` parameters.
```yaml
# In your config.yml
crawler:
  rate_limiter:
    enabled: true
    base_delay: [0.5, 1.5] # Default delay between 0.5 and 1.5 seconds
```

#### 4.5.4. Example `config.yml` snippet: Adding default browser arguments to `crawler.browser.extra_args`.
```yaml
# In your config.yml
crawler:
  browser:
    # Default kwargs for BrowserConfig
    # headless: true
    # text_mode: false # etc.
    extra_args:
      - "--disable-gpu" # Already default, but shown for example
      - "--window-size=1920,1080"
      # Add other chromium flags as needed
```

#### 4.5.5. Example `config.yml` snippet: Changing `crawler.pool.max_pages` (global semaphore).
This controls the maximum number of concurrent browser pages globally for the server.
```yaml
# In your config.yml
crawler:
  pool:
    max_pages: 20 # Allow up to 20 concurrent browser pages
```

#### 4.5.6. Example `config.yml` snippet: Changing `crawler.pool.idle_ttl_sec` (janitor GC timeout).
This controls how long an idle browser instance in the pool will live before being closed.
```yaml
# In your config.yml
crawler:
  pool:
    idle_ttl_sec: 600 # Close idle browsers after 10 minutes (default is 30 min)
```

---
## V. Model-Controller-Presenter (MCP) Bridge Integration

### 5.1. Overview of MCP and its purpose with Crawl4ai.
The Model-Controller-Presenter (MCP) bridge allows AI tools and agents (like Claude Code, potentially others in the future) to interact with Crawl4ai's capabilities as "tools." Crawl4ai endpoints decorated with `@mcp_tool` become callable functions for these AI agents. This enables AIs to leverage web crawling and data extraction within their reasoning and task execution processes.

### 5.2. Accessing MCP Endpoints

#### 5.2.1. Example: Conceptual connection to the MCP WebSocket endpoint (`/mcp/ws`).
Connecting to `/mcp/ws` would typically be done by an MCP-compatible client library.
```python
# This is a conceptual Python example using a hypothetical MCP client library
# For actual MCP client usage, refer to the specific MCP tool's documentation.
# from mcp_client_library import MCPClient # Hypothetical library

# async def connect_mcp_ws():
#     mcp_url = f"{BASE_URL.replace('http', 'ws')}/mcp/ws"
#     async with MCPClient(mcp_url) as client:
#         print(f"Connected to MCP WebSocket at {mcp_url}")
#         # ... send/receive MCP messages ...
#         # e.g., await client.list_tools()
#         # e.g., await client.call_tool(tool_name="crawl", arguments={"urls": ["https://example.com"]})

# if __name__ == "__main__":
#     # asyncio.run(connect_mcp_ws()) # Uncomment if you have a client library
    print("MCP WebSocket conceptual connection. Real client library needed.")
```

#### 5.2.2. Example: Conceptual connection to the MCP SSE endpoint (`/mcp/sse`).
Server-Sent Events (SSE) is another transport for MCP.
```python
# Similar to WebSocket, an MCP-compatible SSE client would be used.
# from sseclient import SSEClient # A possible library for SSE

# def connect_mcp_sse():
#     mcp_sse_url = f"{BASE_URL}/mcp/sse"
#     print(f"Attempting to connect to MCP SSE at {mcp_sse_url} (conceptual)")
    # try:
    #     messages = SSEClient(mcp_sse_url) # This is synchronous, an async version would be better
    #     for msg in messages:
    #         print(f"MCP SSE Message: {msg.data}")
    #         if "some_condition_to_stop": # e.g. after init message
    #             break
    # except Exception as e:
    #     print(f"Error with MCP SSE: {e}")
    print("MCP SSE conceptual connection. Real client library needed.")

# if __name__ == "__main__":
    # connect_mcp_sse() # Uncomment if you have a client library
```

#### 5.2.3. Example: Fetching the MCP schema from `/mcp/schema` using `requests`.
This endpoint provides information about available MCP tools and resources.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

try:
    response = requests.get(f"{BASE_URL}/mcp/schema", headers=headers)
    response.raise_for_status()
    mcp_schema = response.json()
    print("MCP Schema:")
    # print(json.dumps(mcp_schema, indent=2)) # Can be verbose

    if "tools" in mcp_schema:
        print(f"\nAvailable MCP Tools ({len(mcp_schema['tools'])}):")
        for tool in mcp_schema["tools"][:3]: # Show first 3 tools
            print(f"  - Name: {tool.get('name')}, Description: {tool.get('description', '')[:50]}...")
    
    if "resources" in mcp_schema:
        print(f"\nAvailable MCP Resources ({len(mcp_schema['resources'])}):")
        for resource in mcp_schema["resources"][:3]: # Show first 3 resources
            print(f"  - Name: {resource.get('name')}, Description: {resource.get('description', '')[:50]}...")

except requests.exceptions.RequestException as e:
    print(f"Error fetching MCP schema: {e}")
```

### 5.3. Understanding MCP Tool Exposure

#### 5.3.1. Explanation: How endpoints decorated with `@mcp_tool` become available through the MCP bridge.
In `server.py`, FastAPI endpoints decorated with `@mcp_tool("tool_name")` are automatically registered with the MCP bridge. The MCP bridge then exposes these tools (like `/crawl`, `/md`, `/screenshot`, etc.) to connected MCP clients (e.g., AI agents). The arguments of the FastAPI endpoint function become the expected arguments for the MCP tool call.

#### 5.3.2. Example: Invoking a Crawl4ai tool (e.g., `/md`) through a simulated MCP client request structure (if simple enough to demonstrate with `requests`).
This is a conceptual illustration. A real MCP client would handle the JSON-RPC formatting for calls via WebSocket or SSE. The `/mcp/messages` endpoint is used by the SSE client to POST messages.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
# This requires a client_id which is usually established during SSE handshake
# For a simple test, if the server allows it, you might be able to send.
# However, this is highly dependent on the MCP server's transport implementation.

# This is a simplified, conceptual example of what an MCP call might look like
# if sent via a direct POST (which is how SSE clients send requests).
# A proper MCP client would handle session IDs and JSON-RPC framing.
mcp_tool_call_payload = {
    "jsonrpc": "2.0",
    "method": "call_tool",
    "params": {
        "name": "md", # The tool name, matches @mcp_tool("md")
        "arguments": { # These map to the FastAPI endpoint's Pydantic model or parameters
            "body": { # Matches the 'body: MarkdownRequest' in the get_markdown endpoint
                "url": "https://example.com",
                "f": "RAW"
            }
        }
    },
    "id": "some_unique_request_id"
}

# The SSE transport uses a client-specific POST endpoint, e.g., /mcp/messages/<client_id>
# This example cannot fully replicate that without a client_id.
# We'll try to hit a hypothetical endpoint or illustrate the payload.
print("Conceptual MCP tool call payload (actual call needs proper client/transport):")
print(json.dumps(mcp_tool_call_payload, indent=2))

# If you had a direct POST endpoint for tools (not standard MCP for SSE/WS):
# try:
#     # This is NOT how MCP typically works for SSE/WS, but for a hypothetical direct tool POST:
#     # response = requests.post(f"{BASE_URL}/mcp/call_tool_directly", json=mcp_tool_call_payload, headers=get_headers())
#     # response.raise_for_status()
#     # tool_result = response.json()
#     # print("\nResult from conceptual direct tool call:")
#     # print(json.dumps(tool_result, indent=2))
#     pass
# except requests.exceptions.RequestException as e:
#     print(f"Error in conceptual direct tool call: {e}")
```

---
## VI. Advanced Scenarios & Client-Side Best Practices

### 6.1. Chaining API Calls for Complex Workflows

#### 6.1.1. Example: Fetch preprocessed HTML using `/html`, then use this HTML as input to a local `crawl4ai` instance or another tool (conceptual).
```python
import requests
import os
import json
import asyncio
# Assuming crawl4ai is also installed as a library for local processing
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

async def chained_workflow():
    target_url = "https://example.com/article"
    
    # Step 1: Fetch preprocessed HTML from the API
    print(f"Step 1: Fetching preprocessed HTML for {target_url} via API...")
    html_payload = {"url": target_url}
    preprocessed_html = None
    try:
        response = requests.post(f"{BASE_URL}/html", json=html_payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        preprocessed_html = data.get("html")
        if preprocessed_html:
            print(f"Successfully fetched preprocessed HTML (length: {len(preprocessed_html)}).")
        else:
            print("Failed to get preprocessed HTML from API.")
            return
    except requests.exceptions.RequestException as e:
        print(f"Error fetching preprocessed HTML: {e}")
        return

    # Step 2: Use this HTML with a local Crawl4AI instance for further processing
    # (e.g., applying a very specific local Markdown generator or extraction)
    if preprocessed_html:
        print("\nStep 2: Processing fetched HTML with a local Crawl4AI instance...")
        # Example: Generate Markdown using a specific local configuration
        custom_md_generator = DefaultMarkdownGenerator(
            # content_source="raw_html" because we are feeding it raw HTML
            content_source="raw_html", 
            options={"body_width": 0} # No line wrapping
        )
        local_run_config = CrawlerRunConfig(markdown_generator=custom_md_generator)
        
        async with AsyncWebCrawler() as local_crawler:
            # Use "raw:" prefix to tell the local crawler this is direct HTML content
            result = await local_crawler.arun(url=f"raw:{preprocessed_html}", config=local_run_config)
            if result.success and result.markdown:
                print("Markdown generated locally from API-fetched HTML (first 300 chars):")
                print(result.markdown.raw_markdown[:300] + "...")
            else:
                print(f"Local processing failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(chained_workflow())
```

---
### 6.2. API Error Handling

#### 6.2.1. Example: Python script showing robust error handling for common HTTP status codes (400, 401, 403, 404, 422, 500) when calling Crawl4ai API.
```python
import requests
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
# Use a token known to be invalid or expired if testing 401/403 with auth enabled
# invalid_headers = {"Authorization": "Bearer invalidtoken123"}
# For this example, we'll use the standard get_headers()
headers = get_headers()


def make_api_call(endpoint, method="GET", payload=None):
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=payload, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        else:
            print(f"Unsupported method: {method}")
            return

        print(f"\n--- Testing {method} {url} with payload {payload} ---")
        print(f"Status Code: {response.status_code}")
        
        if response.ok: # status_code < 400
            print("Response JSON:")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:500] + "...")
            except json.JSONDecodeError:
                print("Response is not valid JSON.")
                print(f"Response Text (snippet): {response.text[:200]}...")
        else:
            print(f"Error Response Text: {response.text}")
            # Specific error handling based on status code
            if response.status_code == 400:
                print("Handling Bad Request (400)... Possible malformed payload.")
            elif response.status_code == 401:
                print("Handling Unauthorized (401)... API token might be missing or invalid.")
            elif response.status_code == 403:
                print("Handling Forbidden (403)... API token might lack permissions or IP restricted.")
            elif response.status_code == 404:
                print("Handling Not Found (404)... Endpoint or resource does not exist.")
            elif response.status_code == 422:
                print("Handling Unprocessable Entity (422)... Validation error with request data.")
                print(f"Details: {response.json().get('detail')}")
            elif response.status_code >= 500:
                print("Handling Server Error (5xx)... Problem on the server side.")
            
    except requests.exceptions.Timeout:
        print(f"Request to {url} timed out.")
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {url}. Is the server running?")
    except requests.exceptions.RequestException as e:
        print(f"An unexpected request error occurred for {url}: {e}")

if __name__ == "__main__":
    # Test a valid endpoint
    make_api_call("/health")
    
    # Test a non-existent endpoint (expected 404)
    make_api_call("/nonexistent_endpoint")

    # Test /md with missing URL (expected 422)
    make_api_call("/md", method="POST", payload={"f": "RAW"}) 

    # Test /token with invalid payload (expected 422 if email is missing)
    make_api_call("/token", method="POST", payload={"not_email": "test"})

    # If JWT is enabled, an unauthenticated call to a protected endpoint would give 401/403.
    # For this example, assume /admin is a hypothetical protected endpoint.
    # print("\nAttempting access to hypothetical protected /admin endpoint...")
    # make_api_call("/admin", headers={}) # No auth header
```

---
### 6.3. Client-Side Script for Long-Running Jobs

#### 6.3.1. Example: A Python client that submits a job to `/crawl`, polls `/task/{task_id}` with backoff, and retrieves results.
This is a more robust version of the polling mechanism shown earlier.
```python
import requests
import time
import os
import json

BASE_URL = os.environ.get("CRAWL4AI_BASE_URL", "http://localhost:11235")
headers = get_headers()

def submit_job_and_wait_with_backoff(payload, max_poll_time=300, initial_poll_interval=2, max_poll_interval=30, backoff_factor=1.5):
    try:
        # 1. Submit Job
        submit_response = requests.post(f"{BASE_URL}/crawl", json=payload, headers=headers)
        submit_response.raise_for_status()
        task_id = submit_response.json().get("task_id")
        if not task_id:
            print("Failed to get task_id from submission.")
            return None
        print(f"Job submitted. Task ID: {task_id}. Polling with backoff...")

        # 2. Poll with Exponential Backoff
        poll_interval = initial_poll_interval
        start_time = time.time()
        
        while time.time() - start_time < max_poll_time:
            status_response = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            current_status = status_data.get("status")
            
            print(f"  Task {task_id} status: {current_status} (next poll in {poll_interval:.1f}s)")

            if current_status == "COMPLETED":
                print(f"Task {task_id} COMPLETED.")
                return status_data.get("result")
            elif current_status == "FAILED":
                print(f"Task {task_id} FAILED. Error: {status_data.get('error')}")
                return None
            
            time.sleep(poll_interval)
            poll_interval = min(poll_interval * backoff_factor, max_poll_interval)
            
        print(f"Task {task_id} polling timed out after {max_poll_time} seconds.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    # Example of a potentially longer job (crawling a site known for being slow or large)
    long_job_payload = {
        "urls": ["https://archive.org/web/"], # A site that might take a bit longer
        "crawler_config": {"word_count_threshold": 500} # Higher threshold
    }
    
    print("\n--- Testing Long-Running Job Client ---")
    job_result = submit_job_and_wait_with_backoff(long_job_payload, max_poll_time=120) # 2 min timeout

    if job_result and "results" in job_result:
        for i, res_item in enumerate(job_result["results"]):
            print(f"\nResult for {res_item.get('url')}:")
            print(f"  Success: {res_item.get('success')}")
            if res_item.get('success'):
                 md_length = len(res_item.get('markdown', {}).get('raw_markdown', ''))
                 print(f"  Markdown Length: {md_length}")
    elif job_result:
         print(f"\nReceived result data (unexpected structure):")
         print(json.dumps(job_result, indent=2, ensure_ascii=False))
    else:
        print("\nJob did not complete successfully or timed out.")
```

---
### 6.4. Batching Requests to `/crawl/stream` vs. `/crawl`

#### 6.4.1. Discussion: When to use streaming for many URLs vs. submitting a single job with multiple URLs.

*   **`/crawl` (Job-based, polling):**
    *   **Pros:**
        *   Better for very large numbers of URLs where you don't need immediate feedback for each.
        *   Robust to client disconnections (job continues on server).
        *   Redis queue handles load and persistence of jobs.
        *   Server manages concurrency and resources more globally.
    *   **Cons:**
        *   Requires a polling mechanism on the client side.
        *   Results are only available once the entire batch (or individual URL within a multi-URL job if server processes them somewhat independently before final aggregation) is complete.
    *   **Use when:** You have hundreds or thousands of URLs, can tolerate some delay for results, and need a fire-and-forget submission style.

*   **`/crawl/stream` (Streaming):**
    *   **Pros:**
        *   Real-time feedback: results for each URL are streamed back as soon as they are processed.
        *   Simpler client logic if immediate processing of individual results is needed.
        *   Good for interactive applications or dashboards.
    *   **Cons:**
        *   Client must maintain an open connection. If it drops, the stream is lost.
        *   Can be less efficient for very large numbers of URLs if each URL is processed sequentially within the stream handler on the server (though `handle_stream_crawl_request` does process them concurrently up to server limits).
        *   The client needs to handle NDJSON parsing.
    *   **Use when:** You need results for URLs as they come in, are processing a moderate number of URLs, or building an interactive tool.

**General Guideline:**
*   For a few to a few dozen URLs where you want results quickly and can process them one-by-one: `/crawl/stream`.
*   For hundreds or thousands of URLs, or when you prefer to submit a batch and check back later: `/crawl` with polling.
*   If using `/crawl/stream` for many URLs, ensure your client-side processing of each streamed result is fast to avoid becoming a bottleneck. The server-side uses an `AsyncGenerator` which processes URLs concurrently up to its internal limits, so the client should be ready to consume these results efficiently.

```