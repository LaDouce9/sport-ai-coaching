from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from sport_coaching.ingestion.strava_parser import StravaActivity, StravaStream

SCHEMA = """
CREATE TABLE IF NOT EXISTS strava_activities (
    id INTEGER PRIMARY KEY,
    name TEXT,
    type TEXT,
    sport_type TEXT,
    distance_m REAL,
    -- moving_time_s et elapsed_time_s sont stockes tous les deux, sans trancher lequel
    -- utiliser : ce choix relève du futur module de calcul de charge, pas de
    -- l'ingestion (cf. docs/SPEC.md section 2).
    moving_time_s INTEGER,
    elapsed_time_s INTEGER,
    total_elevation_gain_m REAL,
    average_heartrate REAL,
    max_heartrate REAL,
    start_date TEXT,
    start_date_local TEXT,
    timezone TEXT,
    has_streams INTEGER NOT NULL DEFAULT 0,
    raw_json TEXT,
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS strava_activity_streams (
    activity_id INTEGER NOT NULL,
    stream_type TEXT NOT NULL,
    values_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (activity_id, stream_type),
    FOREIGN KEY (activity_id) REFERENCES strava_activities(id)
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Colonnes ajoutées après l'audit du 25/08 (notebooks/strava_data_audit.ipynb) : ces
# champs sont réellement renvoyés par l'endpoint résumé Strava (observés dans raw_json)
# bien qu'absents des model_fields déclarés de stravalib.SummaryActivity. Backfillées
# depuis raw_json déjà en base, sans réappeler l'API Strava.
_MIGRATIONS: list[tuple[str, str, str]] = [
    ("strava_average_heartrate", "REAL", "average_heartrate"),
    ("strava_max_heartrate", "REAL", "max_heartrate"),
    ("suffer_score", "REAL", "suffer_score"),
    ("average_cadence", "REAL", "average_cadence"),
]


def _migrate(conn: sqlite3.Connection) -> None:
    existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(strava_activities)")}
    for column, sql_type, raw_key in _MIGRATIONS:
        if column in existing_columns:
            continue
        conn.execute(f"ALTER TABLE strava_activities ADD COLUMN {column} {sql_type}")
        conn.execute(
            f"UPDATE strava_activities SET {column} = json_extract(raw_json, ?) "
            "WHERE raw_json IS NOT NULL",
            (f"$.{raw_key}",),
        )


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    _migrate(conn)
    conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_activity(conn: sqlite3.Connection, activity: StravaActivity) -> None:
    # strava_average_heartrate/strava_max_heartrate/suffer_score/average_cadence sont
    # extraits de raw_json via json_extract plutôt que portés par StravaActivity : ce
    # sont des champs "extra" de l'API observés dans les données réelles (cf. audit du
    # 25/08), pas des champs déclarés par stravalib — raw_json reste la source de
    # vérité pour ce qui n'est pas explicitement modélisé.
    conn.execute(
        """
        INSERT INTO strava_activities (
            id, name, type, sport_type, distance_m, moving_time_s, elapsed_time_s,
            total_elevation_gain_m, average_heartrate, max_heartrate,
            start_date, start_date_local, timezone, has_streams, raw_json, fetched_at,
            strava_average_heartrate, strava_max_heartrate, suffer_score, average_cadence
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            json_extract(?, '$.average_heartrate'), json_extract(?, '$.max_heartrate'),
            json_extract(?, '$.suffer_score'), json_extract(?, '$.average_cadence')
        )
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, type=excluded.type, sport_type=excluded.sport_type,
            distance_m=excluded.distance_m, moving_time_s=excluded.moving_time_s,
            elapsed_time_s=excluded.elapsed_time_s,
            total_elevation_gain_m=excluded.total_elevation_gain_m,
            average_heartrate=excluded.average_heartrate,
            max_heartrate=excluded.max_heartrate,
            start_date=excluded.start_date, start_date_local=excluded.start_date_local,
            timezone=excluded.timezone, has_streams=excluded.has_streams,
            raw_json=excluded.raw_json, fetched_at=excluded.fetched_at,
            strava_average_heartrate=excluded.strava_average_heartrate,
            strava_max_heartrate=excluded.strava_max_heartrate,
            suffer_score=excluded.suffer_score, average_cadence=excluded.average_cadence
        """,
        (
            activity.id,
            activity.name,
            activity.type,
            activity.sport_type,
            activity.distance_m,
            activity.moving_time_s,
            activity.elapsed_time_s,
            activity.total_elevation_gain_m,
            activity.average_heartrate,
            activity.max_heartrate,
            activity.start_date,
            activity.start_date_local,
            activity.timezone,
            int(activity.has_streams),
            activity.raw_json,
            _now(),
            activity.raw_json,
            activity.raw_json,
            activity.raw_json,
            activity.raw_json,
        ),
    )
    # Pas de commit ici : un sync entier doit être une seule transaction (voir
    # strava_sync.sync_activities) pour que le watermark de reprise reste sûr en cas
    # d'interruption partielle — cf. docs/METHODOLOGIE.md, revue de code du 25/08.


def upsert_streams(conn: sqlite3.Connection, streams: list[StravaStream]) -> None:
    if not streams:
        return
    conn.executemany(
        """
        INSERT INTO strava_activity_streams (activity_id, stream_type, values_json, fetched_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(activity_id, stream_type) DO UPDATE SET
            values_json=excluded.values_json, fetched_at=excluded.fetched_at
        """,
        [(s.activity_id, s.stream_type, json.dumps(s.values), _now()) for s in streams],
    )
    # Pas de commit ici non plus, même raison.


def get_last_sync_watermark(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT MAX(start_date) FROM strava_activities").fetchone()
    return row[0] if row else None
