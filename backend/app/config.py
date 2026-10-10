"""Settings: secrets from .env, everything else from config.yaml (both at the repo root)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.yaml"


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://radar:radar@localhost:5432/radar"
    github_token: str = ""
    openai_api_key: str = ""


class BriefConfig(BaseModel):
    top_repos: int = 5
    top_news: int = 3
    leaderboard_size: int = 10
    repeat_cooldown_days: int = 7


class InterestsConfig(BaseModel):
    keywords: list[str] = []


class TrendingConfig(BaseModel):
    every_hours: int = 6
    languages: list[str] = [""]
    ranges: list[str] = ["daily", "weekly"]


class GithubApiConfig(BaseModel):
    every_hours: int = 6
    track_days: int = 30


class HackerNewsConfig(BaseModel):
    every_hours: int = 1


class SourcesConfig(BaseModel):
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
    monthly_budget_usd: float = 15

    @property
    def prompt_path(self) -> Path:
        return ROOT_DIR / self.prompt_file


class AppConfig(BaseModel):
    timezone: str = "Asia/Ho_Chi_Minh"
    brief_time: str = "07:00"
    weekly_leaderboard_day: str = "mon"
    brief: BriefConfig = BriefConfig()
    interests: InterestsConfig = InterestsConfig()
    sources: SourcesConfig = SourcesConfig()
    llm: LlmConfig = LlmConfig()


@lru_cache
def get_secrets() -> Secrets:
    return Secrets()


@lru_cache
def get_config() -> AppConfig:
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    return AppConfig.model_validate(data or {})
