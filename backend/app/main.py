import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router
from app.config import ROOT_DIR
from app.db import engine
from app.scheduler import create_scheduler, schedule_catch_up

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)
log = logging.getLogger("radar")

FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler  # read by /api/collectors/status for next run times
    log.info("Scheduler started with %d job(s)", len(scheduler.get_jobs()))
    await schedule_catch_up(scheduler)
    yield
    scheduler.shutdown(wait=False)
    await engine.dispose()


app = FastAPI(title="Tech Radar", lifespan=lifespan)
app.include_router(api_router)

# After `npm run build`, serve the frontend from the same origin (one URL for daily use).
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str) -> FileResponse:
        file = FRONTEND_DIST / path
        if path and file.is_file():
            return FileResponse(file)
        return FileResponse(FRONTEND_DIST / "index.html")
