from __future__ import annotations

import sqlite3
from datetime import datetime

from stravalib.client import Client
from stravalib.exc import ObjectNotFound

from sport_coaching.ingestion import storage
from sport_coaching.ingestion.strava_parser import (
    compute_heartrate_stats,
    parse_activity,
    parse_streams,
)


def sync_activities(client: Client, conn: sqlite3.Connection, full: bool = False) -> int:
    storage.init_db(conn)

    after: datetime | None = None
    if not full:
        watermark = storage.get_last_sync_watermark(conn)
        if watermark:
            after = datetime.fromisoformat(watermark)

    count = 0
    for raw_activity in client.get_activities(after=after):
        activity = parse_activity(raw_activity)

        try:
            raw_streams = client.get_activity_streams(activity.id)
        except ObjectNotFound:
            # Certaines activités (ex: entrées manuelles côté Strava, sans GPS/capteur)
            # n'ont pas de streams — ne doit pas faire échouer le sync entier.
            raw_streams = {}

        streams = parse_streams(activity.id, raw_streams) if raw_streams else []
        activity.has_streams = bool(streams)
        activity.average_heartrate, activity.max_heartrate = compute_heartrate_stats(streams)

        storage.upsert_activity(conn, activity)
        storage.upsert_streams(conn, streams)

        count += 1

    return count
