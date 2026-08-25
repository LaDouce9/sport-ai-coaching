from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from stravalib.model import Stream
from stravalib.strava_model import SummaryActivity


@dataclass
class StravaActivity:
    id: int
    name: str | None
    type: str | None
    sport_type: str | None
    distance_m: float | None
    moving_time_s: int | None
    elapsed_time_s: int | None
    total_elevation_gain_m: float | None
    start_date: str | None
    start_date_local: str | None
    timezone: str | None
    raw_json: str
    average_heartrate: float | None = None
    max_heartrate: float | None = None
    has_streams: bool = False


@dataclass
class StravaStream:
    activity_id: int
    stream_type: str
    values: list


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def parse_activity(raw: SummaryActivity) -> StravaActivity:
    # SummaryActivity (retour de get_activities) n'expose pas average_heartrate /
    # max_heartrate — confirmé par introspection de stravalib==2.5.0, ces champs
    # n'existent que sur la représentation "detailed". On les calcule plutôt à
    # partir du stream `heartrate` (voir compute_heartrate_stats) pour éviter un
    # appel API supplémentaire par activité.
    return StravaActivity(
        id=raw.id,
        name=raw.name,
        type=raw.type.root if raw.type else None,
        sport_type=raw.sport_type.root if raw.sport_type else None,
        distance_m=raw.distance,
        moving_time_s=raw.moving_time,
        elapsed_time_s=raw.elapsed_time,
        total_elevation_gain_m=raw.total_elevation_gain,
        start_date=_iso(raw.start_date),
        start_date_local=_iso(raw.start_date_local),
        timezone=raw.timezone,
        raw_json=json.dumps(raw.model_dump(mode="json")),
    )


def parse_streams(activity_id: int, raw_streams: dict[str, Stream]) -> list[StravaStream]:
    return [
        StravaStream(
            activity_id=activity_id,
            stream_type=stream_type,
            values=list(stream.data or []),
        )
        for stream_type, stream in raw_streams.items()
    ]


def compute_heartrate_stats(streams: list[StravaStream]) -> tuple[float | None, float | None]:
    for stream in streams:
        if stream.stream_type != "heartrate":
            continue
        values = [v for v in stream.values if v is not None]
        if not values:
            return None, None
        return sum(values) / len(values), max(values)
    return None, None
