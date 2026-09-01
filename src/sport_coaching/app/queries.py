from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class ActivityListItem:
    id: int
    name: str
    sport_type: str
    start_date_local: str
    distance_m: float
    moving_time_s: int


def list_activities(
    conn: sqlite3.Connection, sport_type: str | None = None
) -> list[ActivityListItem]:
    """Liste les activités, de la plus récente à la plus ancienne. Si `sport_type`
    est fourni, ne retourne que les activités de ce type (liste vide si aucune)."""
    query = (
        "SELECT id, name, sport_type, start_date_local, distance_m, moving_time_s "
        "FROM strava_activities"
    )
    params: tuple = ()
    if sport_type is not None:
        query += " WHERE sport_type = ?"
        params = (sport_type,)
    query += " ORDER BY start_date_local DESC"

    rows = conn.execute(query, params).fetchall()
    return [
        ActivityListItem(
            id=row[0],
            name=row[1],
            sport_type=row[2],
            start_date_local=row[3],
            distance_m=row[4],
            moving_time_s=row[5],
        )
        for row in rows
    ]


def list_sport_types(conn: sqlite3.Connection) -> list[str]:
    """Types d'activité distincts présents en base, triés alphabétiquement —
    peuple le filtre par type de l'interface."""
    rows = conn.execute(
        "SELECT DISTINCT sport_type FROM strava_activities "
        "WHERE sport_type IS NOT NULL ORDER BY sport_type"
    ).fetchall()
    return [row[0] for row in rows]
