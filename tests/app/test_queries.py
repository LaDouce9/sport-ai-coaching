from sport_coaching.app.queries import list_activities, list_sport_types
from sport_coaching.ingestion import storage
from sport_coaching.ingestion.strava_parser import StravaActivity


def _activity(**overrides):
    defaults = dict(
        id=1,
        name="Sortie test",
        type="Run",
        sport_type="Run",
        distance_m=10000.0,
        moving_time_s=3000,
        elapsed_time_s=3100,
        total_elevation_gain_m=120.0,
        start_date="2026-01-01T10:00:00+00:00",
        start_date_local="2026-01-01T11:00:00+00:00",
        timezone="(GMT+01:00) Europe/Paris",
        raw_json="{}",
    )
    defaults.update(overrides)
    return StravaActivity(**defaults)


def test_list_activities_returns_all_by_default(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(id=1, sport_type="Run"))
    storage.upsert_activity(conn, _activity(id=2, sport_type="Ride"))

    activities = list_activities(conn)

    assert {a.id for a in activities} == {1, 2}


def test_list_activities_filters_by_sport_type(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(id=1, sport_type="Run"))
    storage.upsert_activity(conn, _activity(id=2, sport_type="Ride"))

    activities = list_activities(conn, sport_type="Run")

    assert [a.id for a in activities] == [1]


def test_list_activities_unknown_sport_type_returns_empty(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(id=1, sport_type="Run"))

    assert list_activities(conn, sport_type="Swim") == []


def test_list_activities_orders_most_recent_first(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(
        conn, _activity(id=1, start_date_local="2026-01-01T11:00:00+00:00")
    )
    storage.upsert_activity(
        conn, _activity(id=2, start_date_local="2026-02-01T11:00:00+00:00")
    )

    activities = list_activities(conn)

    assert [a.id for a in activities] == [2, 1]


def test_list_sport_types_is_sorted_and_distinct(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(id=1, sport_type="Run"))
    storage.upsert_activity(conn, _activity(id=2, sport_type="Ride"))
    storage.upsert_activity(conn, _activity(id=3, sport_type="Run"))

    assert list_sport_types(conn) == ["Ride", "Run"]


def test_list_sport_types_empty_db_returns_empty(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)

    assert list_sport_types(conn) == []
