from fastapi import APIRouter

from app.api import briefs, cards, collectors, health, leaderboard, news, repos, stats

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(briefs.router)
router.include_router(leaderboard.router)
router.include_router(stats.router)
router.include_router(repos.router)
router.include_router(news.router)
router.include_router(cards.router)
router.include_router(collectors.router)
