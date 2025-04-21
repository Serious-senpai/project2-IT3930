from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


__all__ = ()


PORT = int(os.environ["PORT"])
MSSQL_HOST = os.environ["MSSQL_HOST"]
MSSQL_DATABASE = os.environ["MSSQL_DATABASE"]
MSSQL_USER = os.environ["MSSQL_USER"]
MSSQL_PASSWORD = os.environ["MSSQL_PASSWORD"]

EPOCH = datetime(2025, 1, 1, 0, 0, 0, 0, timezone.utc)
DB_PAGINATION_QUERY = 50
ROOT = Path(__file__).parent.parent.resolve()
