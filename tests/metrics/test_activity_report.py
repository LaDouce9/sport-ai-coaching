import matplotlib

matplotlib.use("Agg")  # pas d'affichage interactif nécessaire pour les tests

from sport_coaching.ingestion import storage
from sport_coaching.ingestion.strava_parser import StravaActivity, StravaStream
from sport_coaching.metrics.activity_report import (
    compute_km_splits,
    format_duration,
    format_pace,
    load_streams,
    load_summary,
    plot_activity_dashboard,
)


def test_format_pace():
    assert format_pace(300) == "5'00\"/km"
    assert format_pace(325) == "5'25\"/km"
    assert format_pace(None) == "—"


def test_format_duration():
    assert format_duration(1830) == "30min30"
    assert format_duration(5400) == "1h30"


def test_compute_km_splits_basic():
    streams = {
        "distance": [0, 500, 1000, 1500, 2000],
        "time": [0, 150, 300, 450, 600],
        "heartrate": [140, 145, 150, 150, 155],
    }
    splits = compute_km_splits(streams)

    assert len(splits) == 2
    assert splits[0]["km"] == 1
    assert splits[0]["distance_m"] == 1000
    assert splits[0]["time_s"] == 300
    assert splits[0]["pace_s_per_km"] == 300
    assert splits[0]["avg_heartrate"] == (140 + 145 + 150) / 3


def test_compute_km_splits_without_heartrate():
    streams = {"distance": [0, 1000], "time": [0, 300]}
    splits = compute_km_splits(streams)
    assert splits[0]["avg_heartrate"] is None


def test_compute_km_splits_missing_streams_returns_empty():
    assert compute_km_splits({}) == []
    assert compute_km_splits({"distance": [0, 1000]}) == []  # pas de "time"


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
        raw_json='{"average_heartrate": 150, "max_heartrate": 175, "average_cadence": 85}',
    )
    defaults.update(overrides)
    return StravaActivity(**defaults)


def test_load_summary_doubles_running_cadence(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity())

    summary = load_summary(conn, 1)

    assert summary.average_cadence == 170  # 85 (par jambe) x2
    assert summary.average_pace_s_per_km == 300  # 3000s / 10km


def test_load_summary_does_not_double_cycling_cadence(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(sport_type="Ride"))

    summary = load_summary(conn, 1)

    assert summary.average_cadence == 85


def test_load_summary_unknown_activity_raises(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    try:
        load_summary(conn, 999)
        assert False, "devrait lever ValueError"
    except ValueError:
        pass


def test_load_streams_roundtrip(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity())
    storage.upsert_streams(
        conn, [StravaStream(activity_id=1, stream_type="heartrate", values=[140, 150])]
    )

    streams = load_streams(conn, 1)
    assert streams == {"heartrate": [140, 150]}


def test_plot_activity_dashboard_renders_without_streams(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity())

    fig = plot_activity_dashboard(conn, 1)
    assert fig is not None


def test_plot_activity_dashboard_renders_with_streams(tmp_path):
    conn = storage.connect(tmp_path / "test.sqlite3")
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity())
    storage.upsert_streams(
        conn,
        [
            StravaStream(activity_id=1, stream_type="distance", values=[0, 500, 1000, 1500]),
            StravaStream(activity_id=1, stream_type="time", values=[0, 150, 300, 450]),
            StravaStream(
                activity_id=1, stream_type="velocity_smooth", values=[3.3, 3.4, 3.2, 3.5]
            ),
            StravaStream(activity_id=1, stream_type="heartrate", values=[140, 145, 150, 148]),
            StravaStream(activity_id=1, stream_type="altitude", values=[10, 12, 15, 14]),
        ],
    )

    fig = plot_activity_dashboard(conn, 1)
    assert fig is not None
