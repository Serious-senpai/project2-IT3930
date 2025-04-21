from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from .database import Database

try:
    import uvloop  # type: ignore
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


__all__ = ("app",)


@asynccontextmanager
async def __lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await Database.instance.prepare()
    yield
    await Database.instance.close()


app = FastAPI(
    title="Project 2 (IT3930) API",
    lifespan=__lifespan,
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/loop", include_in_schema=False)
async def loop() -> str:
    return str(asyncio.get_event_loop())


@app.get("/headers", include_in_schema=False)
async def headers(request: Request) -> Dict[str, str]:
    """Echo client headers"""
    return dict(request.headers)
