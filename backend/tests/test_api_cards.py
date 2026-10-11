"""TC-004-07/08 (API part): Write card errors map to 429 / 404 without DB or LLM."""

import pytest
from fastapi.testclient import TestClient

from app.api import cards as cards_api
from app.cards import CapReached, ItemNotFound
from app.db import get_session
from app.main import app


async def no_session():
    yield None


@pytest.fixture
def client(monkeypatch):
    async def fake_item(session, item_type, item_id):
        return cards_api.CardItem(item_type=item_type, item_id=item_id, title="x/y", url=None)

    monkeypatch.setattr(cards_api, "_item", fake_item)
    app.dependency_overrides[get_session] = no_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_write_card_returns_429_when_cap_reached(client, monkeypatch):
    async def capped(*args, **kwargs):
        raise CapReached("3,000,000 of 3,000,000 tokens used this month")

    monkeypatch.setattr(cards_api, "get_or_write_card", capped)
    resp = client.post("/api/cards/repo/1")
    assert resp.status_code == 429
    assert "cap reached" in resp.json()["detail"]


def test_write_card_returns_404_for_unknown_item(client, monkeypatch):
    async def missing(*args, **kwargs):
        raise ItemNotFound("repo 999")

    monkeypatch.setattr(cards_api, "get_or_write_card", missing)
    assert client.post("/api/cards/repo/999").status_code == 404


def test_invalid_item_type_rejected(client):
    assert client.get("/api/cards/user/1").status_code == 422
