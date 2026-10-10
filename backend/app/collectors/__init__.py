"""Shared helpers for collectors: HTTP client and retry policy."""

from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config import get_secrets

USER_AGENT = "tech-radar/0.1 (local)"
GITHUB_API = "https://api.github.com"


def make_client(github_api: bool = False, **kwargs: Any) -> httpx.AsyncClient:
    """HTTP client for collectors. With `github_api`, adds the API base URL and token headers."""
    headers = {"User-Agent": USER_AGENT}
    if github_api:
        headers["Accept"] = "application/vnd.github+json"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
        if token := get_secrets().github_token:
            headers["Authorization"] = f"Bearer {token}"
        kwargs.setdefault("base_url", GITHUB_API)
    return httpx.AsyncClient(headers=headers, timeout=20, follow_redirects=True, **kwargs)


def _is_transient(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500


# Retries network errors and 5xx responses (raised via raise_for_status) with backoff.
transient_retry = retry(
    retry=retry_if_exception(_is_transient),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10),
    reraise=True,
)
