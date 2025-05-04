from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, RedirectResponse

from .database import Database
from .routes import routers

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
for router in routers:
    app.include_router(router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/loop", include_in_schema=False)
async def loop() -> PlainTextResponse:
    return PlainTextResponse(asyncio.get_event_loop())


@app.get("/headers", include_in_schema=False)
async def headers(request: Request) -> Dict[str, str]:
    """Echo client headers"""
    return dict(request.headers)


@app.get("/whatsmyip", include_in_schema=False)
async def whatsmyip(request: Request) -> PlainTextResponse:
    """Echo client IP address"""
    try:
        return PlainTextResponse(request.headers["Client-IP"])  # For Azure web services

    except KeyError:
        addr = request.client
        if addr is None:
            return PlainTextResponse("Unknown", status_code=404)

        return PlainTextResponse(f"{addr.host}:{addr.port}")


@app.get(
    "/routes",
    summary="List all routes, including hidden ones",
)
async def routes(request: Request) -> List[str]:
    return [getattr(route, "path") for route in app.routes]
