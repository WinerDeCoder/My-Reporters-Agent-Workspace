from fastapi import APIRouter

from app.api import collectors, health, repos

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(repos.router)
router.include_router(collectors.router)
