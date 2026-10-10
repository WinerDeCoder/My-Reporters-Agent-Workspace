"""The one place that talks to the LLM. Model settings come from config.yaml -> llm."""

import logging
from functools import lru_cache

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import get_config, get_secrets

log = logging.getLogger(__name__)


@lru_cache
def get_client() -> AsyncOpenAI:
    cfg = get_config().llm
    return AsyncOpenAI(
        api_key=get_secrets().openai_api_key or None,  # None -> SDK falls back to env var
        base_url=cfg.base_url,
        timeout=cfg.timeout_seconds,
    )


def load_prompt() -> str:
    return get_config().llm.prompt_path.read_text(encoding="utf-8")


async def generate[T: BaseModel](instructions: str, text: str, schema: type[T]) -> T:
    """Run one structured-output call and return the parsed result as `schema`."""
    cfg = get_config().llm
    extra = {"reasoning": {"effort": cfg.reasoning_effort}} if cfg.reasoning_effort else {}
    resp = await get_client().responses.parse(
        model=cfg.model,
        instructions=instructions,
        input=text,
        text_format=schema,
        max_output_tokens=cfg.max_output_tokens,
        **extra,
    )
    if resp.usage:
        log.info(
            "llm model=%s in=%d out=%d",
            cfg.model,
            resp.usage.input_tokens,
            resp.usage.output_tokens,
        )
    if resp.output_parsed is None:
        raise RuntimeError(f"LLM returned no parsed output (status={resp.status})")
    return resp.output_parsed
