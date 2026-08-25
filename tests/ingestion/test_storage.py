from sport_coaching.ingestion import storage
from sport_coaching.ingestion.strava_parser import StravaActivity, StravaStream


def _activity(id=1, start_date="2026-01-01T10:00:00+00:00", **overrides):
    defaults = dict(
        id=id,
        name="Run",
        type="Run",
        sport_type="Run",
        distance_m=10000.0,
        moving_time_s=3000,
        elapsed_time_s=3100,
        total_elevation_gain_m=120.0,
        start_date=start_date,
        start_date_local=start_date,
        timezone="(GMT+01:00) Europe/Paris",
        raw_json="{}",
    )
    defaults.update(overrides)
    return StravaActivity(**defaults)


def test_init_db_creates_tables(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    tables = {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"strava_activities", "strava_activity_streams"} <= tables


def test_upsert_activity_is_idempotent(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)

    storage.upsert_activity(conn, _activity(name="Run v1"))
    storage.upsert_activity(conn, _activity(name="Run v2"))

    rows = conn.execute("SELECT name FROM strava_activities WHERE id = 1").fetchall()
    assert rows == [("Run v2",)]


def test_upsert_streams_is_idempotent(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity())

    storage.upsert_streams(
        conn, [StravaStream(activity_id=1, stream_type="heartrate", values=[100, 110])]
    )
    storage.upsert_streams(
        conn, [StravaStream(activity_id=1, stream_type="heartrate", values=[100, 110, 120])]
    )

    rows = conn.execute(
        "SELECT values_json FROM strava_activity_streams "
        "WHERE activity_id = 1 AND stream_type = 'heartrate'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "[100, 110, 120]"


def test_watermark_empty_table_returns_none(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    assert storage.get_last_sync_watermark(conn) is None


def test_watermark_returns_max_start_date(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(id=1, start_date="2026-01-01T10:00:00+00:00"))
    storage.upsert_activity(conn, _activity(id=2, start_date="2026-02-01T10:00:00+00:00"))
    assert storage.get_last_sync_watermark(conn) == "2026-02-01T10:00:00+00:00"


def test_upsert_extracts_extra_fields_from_raw_json(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)

    raw = (
        '{"average_heartrate": 145.2, "max_heartrate": 178, '
        '"suffer_score": 62, "average_cadence": 88.5}'
    )
    storage.upsert_activity(conn, _activity(raw_json=raw))

    row = conn.execute(
        "SELECT strava_average_heartrate, strava_max_heartrate, suffer_score, average_cadence "
        "FROM strava_activities WHERE id = 1"
    ).fetchone()
    assert row == (145.2, 178.0, 62.0, 88.5)


def test_init_db_migration_is_idempotent(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(raw_json='{"suffer_score": 10}'))
    storage.init_db(conn)  # ne doit pas lever d'erreur sur les colonnes déjà ajoutées

    row = conn.execute("SELECT suffer_score FROM strava_activities WHERE id = 1").fetchone()
    assert row == (10.0,)
