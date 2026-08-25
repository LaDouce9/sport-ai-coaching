from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


@dataclass(frozen=True)
class StravaConfig:
    client_id: int
    client_secret: str
    refresh_token: str | None
    db_path: Path


def load_strava_config() -> StravaConfig:
    load_dotenv(ENV_PATH)

    client_id = os.environ["STRAVA_CLIENT_ID"]
    client_secret = os.environ["STRAVA_CLIENT_SECRET"]
    refresh_token = os.environ.get("STRAVA_REFRESH_TOKEN") or None
    db_path = Path(
        os.environ.get(
            "SPORT_COACHING_DB_PATH",
            str(ENV_PATH.parent / "data" / "sport_coaching.sqlite3"),
        )
    )

    return StravaConfig(
        client_id=int(client_id),
        client_secret=client_secret,
        refresh_token=refresh_token,
        db_path=db_path,
    )
