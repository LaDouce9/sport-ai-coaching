from datetime import datetime, timezone

import pytest
from stravalib.model import Stream
from stravalib.strava_model import ActivityType, SportType, SummaryActivity

from sport_coaching.ingestion.strava_parser import (
    StravaStream,
    compute_heartrate_stats,
    parse_activity,
    parse_streams,
)


def _summary_activity(**overrides):
    defaults = dict(
        id=123,
        name="Sortie matinale",
        distance=10000.0,
        moving_time=3000,
        elapsed_time=3100,
        total_elevation_gain=120.0,
        type=ActivityType("Run"),
        sport_type=SportType("Run"),
        start_date=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        start_date_local=datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        timezone="(GMT+01:00) Europe/Paris",
    )
    defaults.update(overrides)
    return SummaryActivity(**defaults)


def _stream(data):
    return Stream(type="heartrate", data=data)


def test_parse_activity_maps_core_fields():
    activity = parse_activity(_summary_activity())

    assert activity.id == 123
    assert activity.type == "Run"
    assert activity.sport_type == "Run"
    assert activity.distance_m == 10000.0
    assert activity.moving_time_s == 3000
    assert activity.elapsed_time_s == 3100
    assert activity.total_elevation_gain_m == 120.0
    # Le summary Strava n'expose pas la FC — confirmé par introspection stravalib 2.5.0.
    assert activity.average_heartrate is None
    assert activity.max_heartrate is None
    assert activity.has_streams is False


def test_parse_activity_handles_missing_sport_type():
    activity = parse_activity(_summary_activity(sport_type=None))
    assert activity.sport_type is None


def test_parse_streams_extracts_values_by_type():
    raw = {
        "heartrate": _stream([120, 130, 125]),
        "altitude": Stream(type="altitude", data=[10.0, 12.0, 11.5]),
    }
    streams = parse_streams(activity_id=123, raw_streams=raw)

    by_type = {s.stream_type: s.values for s in streams}
    assert by_type["heartrate"] == [120, 130, 125]
    assert by_type["altitude"] == [10.0, 12.0, 11.5]
    assert all(s.activity_id == 123 for s in streams)


def test_compute_heartrate_stats_with_data():
    streams = [StravaStream(activity_id=1, stream_type="heartrate", values=[100, 120, 140])]
    avg, mx = compute_heartrate_stats(streams)
    assert avg == 120
    assert mx == 140


def test_compute_heartrate_stats_without_heartrate_stream():
    streams = [StravaStream(activity_id=1, stream_type="altitude", values=[1, 2, 3])]
    assert compute_heartrate_stats(streams) == (None, None)


def test_compute_heartrate_stats_no_streams():
    assert compute_heartrate_stats([]) == (None, None)


FIXTURE_MISSING_REASON = (
    "Fixture réelle pas encore fournie (voir docs/SPEC.md, Definition of done V1) — "
    "à créer en anonymisant un vrai export après le premier `sync`, pas fabriquée ici."
)


@pytest.mark.skip(reason=FIXTURE_MISSING_REASON)
def test_parse_activity_against_real_anonymized_sample():
    pass
