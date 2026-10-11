from fastapi import APIRouter

from app.api import briefs, cards, collectors, health, news, repos

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(briefs.router)
router.include_router(repos.router)
router.include_router(news.router)
router.include_router(cards.router)
router.include_router(collectors.router)
