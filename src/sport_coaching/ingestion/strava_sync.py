from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

from stravalib.client import Client
from stravalib.exc import ObjectNotFound

from sport_coaching.ingestion import storage
from sport_coaching.ingestion.strava_parser import (
    compute_heartrate_stats,
    parse_activity,
    parse_streams,
)

# Marge de sécurité soustraite au watermark avant de l'utiliser comme `after` : couvre
# le cas d'une activité future partageant exactement le même start_date (à la seconde)
# que la plus récente déjà synchronisée, qu'un filtre `after` strict exclurait sinon.
# Le refetch de l'activité déjà connue qui en résulte est sans conséquence (upsert
# idempotent). Revue de code du 25/08, voir docs/METHODOLOGIE.md.
WATERMARK_SAFETY_MARGIN = timedelta(seconds=1)


def sync_activities(client: Client, conn: sqlite3.Connection, full: bool = False) -> int:
    storage.init_db(conn)

    after: datetime | None = None
    if not full:
        watermark = storage.get_last_sync_watermark(conn)
        if watermark:
            after = datetime.fromisoformat(watermark) - WATERMARK_SAFETY_MARGIN

    count = 0
    try:
        for raw_activity in client.get_activities(after=after):
            activity = parse_activity(raw_activity)

            try:
                raw_streams = client.get_activity_streams(activity.id)
            except ObjectNotFound:
                # Certaines activités (ex: entrées manuelles côté Strava, sans
                # GPS/capteur) n'ont pas de streams — ne doit pas faire échouer le
                # sync entier.
                raw_streams = {}

            streams = parse_streams(activity.id, raw_streams)
            activity.has_streams = bool(streams)
            activity.average_heartrate, activity.max_heartrate = compute_heartrate_stats(
                streams
            )

            storage.upsert_activity(conn, activity)
            storage.upsert_streams(conn, streams)

            count += 1
    except Exception:
        # Tout le sync est une seule transaction : en cas d'interruption (rate limit,
        # coupure réseau, exception quelconque), on annule plutôt que de laisser un
        # sous-ensemble committé faire avancer le watermark au-delà d'activités plus
        # anciennes jamais traitées — cf. le bug identifié en revue de code du 25/08
        # (docs/METHODOLOGIE.md).
        conn.rollback()
        raise

    conn.commit()
    return count
