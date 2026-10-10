"""TC-001-05..07: GitHub API payload parsing, 404 handling, rate limits (HTTP faked)."""

import hashlib

import httpx
import pytest

from app.collectors import make_client
from app.collectors.github_api import (
    MAX_RATE_LIMIT_WAIT,
    fetch_repo,
    parse_repo_payload,
    rate_limit_wait,
)

REPO_JSON = {
    "full_name": "BerriAI/litellm",
    "description": "Call 100+ LLM APIs",
    "topics": ["llm", "openai"],
    "language": "Python",
    "license": {"spdx_id": "MIT"},
    "stargazers_count": 31000,
    "forks_count": 4100,
}


def test_parse_repo_payload():
    info = parse_repo_payload(REPO_JSON)
    assert info.full_name == "berriai/litellm"
    assert info.description == "Call 100+ LLM APIs"
    assert info.topics == ["llm", "openai"]
    assert info.language == "Python"
    assert info.license == "MIT"
    assert (info.stars, info.forks) == (31000, 4100)


def test_parse_repo_payload_handles_missing_fields():
    info = parse_repo_payload({"full_name": "a/b", "license": None, "topics": None})
    assert (info.description, info.license, info.topics, info.stars) == (None, None, [], 0)


def test_rate_limit_wait():
    now = 1_000_000.0
    reset = {"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(int(now) + 120)}
    assert rate_limit_wait(200, {}, now) is None
    assert rate_limit_wait(404, {}, now) is None
    assert rate_limit_wait(403, reset, now) == pytest.approx(120)
    assert rate_limit_wait(429, {"retry-after": "30"}, now) == 30
    assert rate_limit_wait(429, {}, now) == 60
    assert rate_limit_wait(403, {"x-ratelimit-remaining": "12"}, now) is None  # not a rate limit
    far = {"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(int(now) + 99_999)}
    assert rate_limit_wait(403, far, now) == MAX_RATE_LIMIT_WAIT


def client_for(handler) -> httpx.AsyncClient:
    return make_client(github_api=True, transport=httpx.MockTransport(handler))


async def no_sleep(_seconds: float) -> None:
    return None


async def test_fetch_repo_returns_none_on_404():
    async with client_for(lambda req: httpx.Response(404, json={"message": "Not Found"})) as c:
        assert await fetch_repo(c, "gone/repo", sleep=no_sleep) is None


async def test_fetch_repo_hashes_readme():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/readme"):
            assert req.headers["accept"] == "application/vnd.github.raw"
            return httpx.Response(200, content=b"# LiteLLM")
        return httpx.Response(200, json=REPO_JSON)

    async with client_for(handler) as c:
        info = await fetch_repo(c, "berriai/litellm", sleep=no_sleep)
    assert info is not None
    assert info.readme_hash == hashlib.sha256(b"# LiteLLM").hexdigest()


async def test_fetch_repo_without_readme():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/readme"):
            return httpx.Response(404)
        return httpx.Response(200, json=REPO_JSON)

    async with client_for(handler) as c:
        info = await fetch_repo(c, "berriai/litellm", sleep=no_sleep)
    assert info is not None and info.readme_hash is None


async def test_fetch_repo_retries_after_rate_limit():
    calls = {"repo": 0}
    waited: list[float] = []

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/readme"):
            return httpx.Response(404)
        calls["repo"] += 1
        if calls["repo"] == 1:
            return httpx.Response(429, headers={"retry-after": "7"})
        return httpx.Response(200, json=REPO_JSON)

    async def record_sleep(seconds: float) -> None:
        waited.append(seconds)

    async with client_for(handler) as c:
        info = await fetch_repo(c, "berriai/litellm", sleep=record_sleep)
    assert info is not None and info.stars == 31000
    assert waited == [7.0]
    assert calls["repo"] == 2


async def test_github_client_sends_api_headers():
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen.update(req.headers)
        return httpx.Response(404)

    async with client_for(handler) as c:
        await fetch_repo(c, "a/b", sleep=no_sleep)
    assert seen["x-github-api-version"] == "2022-11-28"
    assert seen["user-agent"].startswith("tech-radar/")
