from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from stravalib.exc import ObjectNotFound
from stravalib.model import Stream
from stravalib.strava_model import ActivityType, SportType, SummaryActivity

from sport_coaching.ingestion import storage, strava_sync
from sport_coaching.ingestion.strava_parser import StravaActivity


def _summary_activity(id, start):
    return SummaryActivity(
        id=id,
        name=f"Activity {id}",
        distance=1000.0,
        moving_time=600,
        elapsed_time=650,
        total_elevation_gain=10.0,
        type=ActivityType("Run"),
        sport_type=SportType("Run"),
        start_date=start,
        start_date_local=start,
        timezone="(GMT+01:00) Europe/Paris",
    )


def test_sync_stores_activities_and_streams(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    client = MagicMock()
    client.get_activities.return_value = [
        _summary_activity(1, datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ]
    client.get_activity_streams.return_value = {
        "heartrate": Stream(type="heartrate", data=[100, 110, 120])
    }

    count = strava_sync.sync_activities(client, conn, full=True)

    assert count == 1
    row = conn.execute(
        "SELECT average_heartrate, max_heartrate, has_streams "
        "FROM strava_activities WHERE id = 1"
    ).fetchone()
    assert row == (110.0, 120.0, 1)


def test_sync_continues_when_streams_missing(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    client = MagicMock()
    client.get_activities.return_value = [
        _summary_activity(1, datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ]
    client.get_activity_streams.side_effect = ObjectNotFound("no streams")

    count = strava_sync.sync_activities(client, conn, full=True)

    assert count == 1
    row = conn.execute("SELECT has_streams FROM strava_activities WHERE id = 1").fetchone()
    assert row == (0,)


def test_sync_uses_watermark_when_not_full(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(
        conn,
        StravaActivity(
            id=1,
            name="old",
            type="Run",
            sport_type="Run",
            distance_m=1.0,
            moving_time_s=1,
            elapsed_time_s=1,
            total_elevation_gain_m=0.0,
            start_date="2026-01-01T00:00:00+00:00",
            start_date_local="2026-01-01T00:00:00+00:00",
            timezone="UTC",
            raw_json="{}",
        ),
    )

    client = MagicMock()
    client.get_activities.return_value = []

    strava_sync.sync_activities(client, conn, full=False)

    called_after = client.get_activities.call_args.kwargs["after"]
    # Marge de sécurité de 1s soustraite au watermark (voir strava_sync.py).
    assert called_after == datetime.fromisoformat("2026-01-01T00:00:00+00:00") - timedelta(
        seconds=1
    )


def test_sync_rolls_back_entirely_on_error(tmp_path):
    # Régression du bug identifié en revue de code (25/08) : sans transaction unique,
    # une activité récente déjà committée aurait fait avancer le watermark au-delà
    # d'activités plus anciennes jamais traitées, les rendant définitivement
    # inaccessibles à un sync incrémental suivant.
    conn = storage.connect(tmp_path / "test.sqlite3")
    client = MagicMock()
    client.get_activities.return_value = [
        _summary_activity(2, datetime(2026, 1, 2, tzinfo=timezone.utc)),
        _summary_activity(1, datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ]
    client.get_activity_streams.side_effect = [{}, RuntimeError("network blip")]

    with pytest.raises(RuntimeError):
        strava_sync.sync_activities(client, conn, full=True)

    rows = conn.execute("SELECT id FROM strava_activities").fetchall()
    assert rows == []


def test_sync_full_ignores_watermark(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(
        conn,
        StravaActivity(
            id=1,
            name="old",
            type="Run",
            sport_type="Run",
            distance_m=1.0,
            moving_time_s=1,
            elapsed_time_s=1,
            total_elevation_gain_m=0.0,
            start_date="2026-01-01T00:00:00+00:00",
            start_date_local="2026-01-01T00:00:00+00:00",
            timezone="UTC",
            raw_json="{}",
        ),
    )

    client = MagicMock()
    client.get_activities.return_value = []

    strava_sync.sync_activities(client, conn, full=True)

    assert client.get_activities.call_args.kwargs["after"] is None
