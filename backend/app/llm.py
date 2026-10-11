"""The one place that talks to the LLM. Model settings come from config.yaml -> llm."""

import logging
from dataclasses import dataclass
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


@dataclass(frozen=True)
class LlmResult[T: BaseModel]:
    parsed: T
    model: str
    input_tokens: int
    output_tokens: int


class LlmOutputError(RuntimeError):
    """The call ran (and used tokens) but returned no parsed output."""

    def __init__(self, message: str, model: str, input_tokens: int, output_tokens: int):
        super().__init__(message)
        self.model, self.input_tokens, self.output_tokens = model, input_tokens, output_tokens


async def generate[T: BaseModel](instructions: str, text: str, schema: type[T]) -> LlmResult[T]:
    """Run one structured-output call; return the parsed result as `schema` plus token usage."""
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
    tokens_in = resp.usage.input_tokens if resp.usage else 0
    tokens_out = resp.usage.output_tokens if resp.usage else 0
    log.info("llm model=%s in=%d out=%d", cfg.model, tokens_in, tokens_out)
    if resp.output_parsed is None:
        raise LlmOutputError(
            f"LLM returned no parsed output (status={resp.status})",
            cfg.model,
            tokens_in,
            tokens_out,
        )
    return LlmResult(resp.output_parsed, cfg.model, tokens_in, tokens_out)
