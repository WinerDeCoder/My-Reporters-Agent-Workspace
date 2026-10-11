"""Settings: secrets from .env, everything else from config.yaml (both at the repo root)."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.yaml"


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://radar:radar@localhost:5433/radar"
    github_token: str = ""
    openai_api_key: str = ""


class BriefConfig(BaseModel):
    top_repos: int = 5
    top_news: int = 3
    leaderboard_size: int = 10
    repeat_cooldown_days: int = 7


class InterestsConfig(BaseModel):
    """Interest topics and match terms (Q-005, Q-015); `~term` = weak, needs another topic."""

    topic_boost: float = 2.0  # Q-019
    max_boost: float = 5.0
    topics: dict[str, list[str]] = {}
    ai_dev_terms: list[str] = []  # news eligibility (Q-016)


class ScoringConfig(BaseModel):
    repeat_penalty: float = 0.3
    dislike_penalty: float = 0.7
    dislike_floor: float = 0.2
    dislike_days: int = 30


# "HH:MM", 24-hour, in the configured timezone (Q-014: collectors run daily).
RunAt = Annotated[str, Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")]


class TrendingConfig(BaseModel):
    run_at: RunAt = "07:10"
    languages: list[str] = [""]
    ranges: list[str] = ["daily", "weekly"]


class GithubApiConfig(BaseModel):
    run_at: RunAt = "07:20"
    track_days: int = 30


class HackerNewsConfig(BaseModel):
    run_at: RunAt = "07:00"
    popular_min_points: int = 100  # also fetch stories above this many points…
    popular_window_hours: int = 26  # …posted within this window (Q-010, Q-014)
    retention_days: int = 30  # prune stories older than this (REQ-COL-006)


class SourcesConfig(BaseModel):
    catch_up_after_hours: int = 20  # on startup, run a job if its last success is older
    github_trending: TrendingConfig = TrendingConfig()
    github_api: GithubApiConfig = GithubApiConfig()
    hacker_news: HackerNewsConfig = HackerNewsConfig()


class LlmConfig(BaseModel):
    model: str = "gpt-5-mini"
    reasoning_effort: Literal["minimal", "low", "medium", "high"] | None = "low"
    max_output_tokens: int = 2000
    timeout_seconds: float = 60
    base_url: str | None = None
    prompt_file: str = "backend/prompts/card.md"
    monthly_token_cap: int = 3_000_000  # input + output tokens per month (Q-023)
    price_per_million: "TokenPrices" = Field(default_factory=lambda: TokenPrices())

    @property
    def prompt_path(self) -> Path:
        return ROOT_DIR / self.prompt_file


class TokenPrices(BaseModel):
    """Optional USD per 1M tokens, only for an estimate in `usage`."""

    input: float | None = None
    output: float | None = None


class CardsConfig(BaseModel):
    run_at: RunAt = "07:25"
    max_source_chars: int = 12_000


class AppConfig(BaseModel):
    timezone: str = "Asia/Ho_Chi_Minh"
    brief_time: str = "07:00"
    weekly_leaderboard_day: str = "mon"
    brief: BriefConfig = BriefConfig()
    interests: InterestsConfig = InterestsConfig()
    scoring: ScoringConfig = ScoringConfig()
    sources: SourcesConfig = SourcesConfig()
    llm: LlmConfig = LlmConfig()
    cards: CardsConfig = CardsConfig()


LlmConfig.model_rebuild()


@lru_cache
def get_secrets() -> Secrets:
    return Secrets()


@lru_cache
def get_config() -> AppConfig:
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    return AppConfig.model_validate(data or {})
