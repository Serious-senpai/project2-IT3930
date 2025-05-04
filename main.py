from __future__ import annotations

import argparse
import os
import sys
from typing import Optional, TYPE_CHECKING

import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from server.app import app
from server.config import PORT


class __Namespace(argparse.Namespace):
    if TYPE_CHECKING:
        host: str
        port: int
        workers: Optional[int]
        log_level: str
        cors: bool


namespace = __Namespace()
__parser = argparse.ArgumentParser(
    description="Run HTTP API server for minichat application",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
__parser.add_argument("--host", type=str, default="0.0.0.0", help="The host to bind the HTTP server to")
__parser.add_argument("--port", type=int, default=PORT, help="The port to bind the HTTP server to")
__parser.add_argument("--workers", type=int, required=False, help="The number of worker processes to run")
__parser.add_argument("--log-level", type=str, default="debug", help="The log level for the application")
__parser.add_argument("--cors", action="store_true", help="Enable CORS for the HTTP server")

__parser.parse_args(namespace=namespace)


if namespace.cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )


if __name__ == "__main__":
    print(f"[{os.getpid()}]", namespace, file=sys.stderr)
    uvicorn.run(
        "main:app",
        host=namespace.host,
        port=namespace.port,
        workers=namespace.workers,
        log_level=namespace.log_level,
    )
