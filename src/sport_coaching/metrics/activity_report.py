from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

# Palette validée (voir skill dataviz / references/palette.md) — reprise telle quelle,
# pas de couleurs choisies à l'oeil.
_SURFACE = "#fcfcfb"
_INK_PRIMARY = "#0b0b0b"
_INK_SECONDARY = "#52514e"
_INK_MUTED = "#898781"
_GRIDLINE = "#e1e0d9"
_AXIS = "#c3c2b7"
_BLUE = "#2a78d6"  # slot 1 — allure
_RED = "#e34948"  # slot 8 — FC
_AQUA = "#1baf7a"  # slot 3 — altitude

# Sports "à pied" : l'API Strava compte la cadence par jambe (une unité = 2 pas),
# alors que l'appli affiche des pas/min totaux -> x2. Le vélo est déjà en tr/min.
# Vérifié via la communauté développeurs Strava (cf. docs/METHODOLOGIE.md), pas
# supposé : https://communityhub.strava.com/developers-api-7/cadence-numbers-from-strava-api-3130
FOOT_SPORTS = {"Run", "TrailRun", "Walk", "Hike"}


@dataclass
class ActivitySummary:
    id: int
    name: str
    sport_type: str
    start_date_local: str
    distance_m: float
    moving_time_s: int
    elapsed_time_s: int
    elevation_gain_m: float
    average_heartrate: float | None
    max_heartrate: float | None
    average_cadence: float | None
    suffer_score: float | None
    average_pace_s_per_km: float | None


def _cadence_multiplier(sport_type: str) -> int:
    return 2 if sport_type in FOOT_SPORTS else 1


def format_pace(seconds_per_km: float | None) -> str:
    if seconds_per_km is None:
        return "—"
    minutes, seconds = divmod(round(seconds_per_km), 60)
    return f"{minutes}'{seconds:02d}\"/km"


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h{minutes:02d}"
    return f"{minutes}min{secs:02d}"


def load_summary(conn: sqlite3.Connection, activity_id: int) -> ActivitySummary:
    row = conn.execute(
        """
        SELECT id, name, sport_type, start_date_local, distance_m, moving_time_s,
               elapsed_time_s, total_elevation_gain_m, average_heartrate, max_heartrate,
               average_cadence, suffer_score
        FROM strava_activities WHERE id = ?
        """,
        (activity_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Activité {activity_id} introuvable en base")

    (
        id_,
        name,
        sport_type,
        start_date_local,
        distance_m,
        moving_time_s,
        elapsed_time_s,
        elevation_gain_m,
        average_heartrate,
        max_heartrate,
        average_cadence,
        suffer_score,
    ) = row

    cadence = (
        average_cadence * _cadence_multiplier(sport_type)
        if average_cadence is not None
        else None
    )
    pace = moving_time_s / (distance_m / 1000) if distance_m else None

    return ActivitySummary(
        id=id_,
        name=name,
        sport_type=sport_type,
        start_date_local=start_date_local,
        distance_m=distance_m,
        moving_time_s=moving_time_s,
        elapsed_time_s=elapsed_time_s,
        elevation_gain_m=elevation_gain_m,
        average_heartrate=average_heartrate,
        max_heartrate=max_heartrate,
        average_cadence=cadence,
        suffer_score=suffer_score,
        average_pace_s_per_km=pace,
    )


def load_streams(conn: sqlite3.Connection, activity_id: int) -> dict[str, list]:
    rows = conn.execute(
        "SELECT stream_type, values_json FROM strava_activity_streams WHERE activity_id = ?",
        (activity_id,),
    ).fetchall()
    return {stream_type: json.loads(values_json) for stream_type, values_json in rows}


def compute_km_splits(streams: dict[str, list]) -> list[dict]:
    """Découpe l'activité en segments d'environ 1 km à partir du stream `distance`,
    avec le temps et la FC moyenne de chaque segment — reproduit les "splits" affichés
    par l'app Strava. Approximation au point d'échantillonnage près (suffisant pour la
    visualisation, pas une donnée de charge d'entraînement au sens de docs/SPEC.md)."""
    distance = streams.get("distance")
    time = streams.get("time")
    if not distance or not time:
        return []

    heartrate = streams.get("heartrate")
    moving = streams.get("moving")

    def moving_time_between(start_idx: int, end_idx: int) -> float:
        # Somme des deltas de temps entre échantillons où `moving` est vrai
        # uniquement. Sans ça, un arrêt réel (feu rouge, pause) pendant un split
        # gonfle son temps sans gonfler sa distance, et fait exploser l'allure
        # affichée pour ce seul kilomètre — observé en pratique sur une vraie
        # activité (cf. notebooks/strava_data_audit.ipynb).
        total = 0.0
        for j in range(start_idx + 1, end_idx + 1):
            dt = time[j] - time[j - 1]
            if moving is None or moving[j]:
                total += dt
        return total

    splits: list[dict] = []
    split_km = 1
    split_start_idx = 0
    for i, d in enumerate(distance):
        is_last_point = i == len(distance) - 1
        if d < split_km * 1000 and not is_last_point:
            continue

        split_distance_m = d - distance[split_start_idx]
        split_time_s = moving_time_between(split_start_idx, i)
        if split_distance_m <= 0 or split_time_s <= 0:
            continue

        hr_values = (
            [v for v in heartrate[split_start_idx : i + 1] if v is not None]
            if heartrate
            else []
        )

        splits.append(
            {
                "km": split_km,
                "distance_m": split_distance_m,
                "time_s": split_time_s,
                "pace_s_per_km": split_time_s / (split_distance_m / 1000),
                "avg_heartrate": sum(hr_values) / len(hr_values) if hr_values else None,
            }
        )
        split_km += 1
        split_start_idx = i + 1

    return splits


def _style_axis(ax) -> None:
    ax.set_facecolor(_SURFACE)
    ax.spines[["top", "right"]].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_AXIS)
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=_INK_MUTED, labelsize=9, length=0)
    ax.grid(True, axis="y", color=_GRIDLINE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def _stat_card(fig, x: float, value: str, label: str) -> None:
    fig.text(x, 0.895, value, fontsize=16, fontweight="bold", color=_INK_PRIMARY, ha="left")
    fig.text(x, 0.870, label, fontsize=9, color=_INK_MUTED, ha="left")


def plot_activity_dashboard(conn: sqlite3.Connection, activity_id: int) -> Figure:
    """Reproduit, en version allégée, le résumé qu'affiche l'app Strava pour une
    activité : stats globales + allure/FC/altitude dans le temps + splits au km.
    Palette et specs de traits : skill dataviz du projet (voir palette validée)."""
    summary = load_summary(conn, activity_id)
    streams = load_streams(conn, activity_id)
    splits = compute_km_splits(streams)

    distance_km = np.array(streams.get("distance", [])) / 1000
    velocity = np.array(streams.get("velocity_smooth", []), dtype=float)
    heartrate = streams.get("heartrate")
    altitude = streams.get("altitude")
    moving = streams.get("moving")

    n = len(distance_km)
    pace_min_per_km = np.full(n, np.nan)
    # Sous ce seuil de vitesse, l'allure explose et n'a plus de sens ; on masque aussi
    # les échantillons où `moving` est faux (arrêt réel) pour ne pas afficher un pic
    # artificiel à chaque pause — même raison que pour compute_km_splits ci-dessus.
    valid = velocity[:n] > 0.3
    if moving is not None:
        valid &= np.array(moving[:n], dtype=bool)
    pace_min_per_km[valid] = 1000 / velocity[:n][valid] / 60

    fig = plt.figure(figsize=(11, 13.5), facecolor=_SURFACE)
    gs = fig.add_gridspec(
        nrows=4,
        ncols=1,
        top=0.83,
        bottom=0.05,
        left=0.08,
        right=0.96,
        height_ratios=[1, 1, 1, 1.1],
        hspace=0.5,
    )

    # --- En-tête : titre + stats globales façon "cards" ---
    date_str = summary.start_date_local[:16].replace("T", " · ")
    fig.text(0.08, 0.975, summary.name, fontsize=19, fontweight="bold", color=_INK_PRIMARY)
    fig.text(
        0.08, 0.945, f"{date_str}  ·  {summary.sport_type}", fontsize=10.5, color=_INK_SECONDARY
    )

    stats = [
        (f"{summary.distance_m / 1000:.2f} km", "Distance"),
        (format_duration(summary.moving_time_s), "Temps"),
        (format_pace(summary.average_pace_s_per_km), "Allure moy."),
        (f"{summary.elevation_gain_m:.0f} m", "D+"),
        (
            f"{summary.average_heartrate:.0f} bpm" if summary.average_heartrate else "—",
            "FC moyenne",
        ),
        (f"{summary.max_heartrate:.0f} bpm" if summary.max_heartrate else "—", "FC max"),
        (
            f"{summary.average_cadence:.0f} /min" if summary.average_cadence else "—",
            "Cadence moy.",
        ),
        (f"{summary.suffer_score:.0f}" if summary.suffer_score else "—", "Relative Effort"),
    ]
    for i, (value, label) in enumerate(stats):
        _stat_card(fig, 0.08 + i * 0.115, value, label)

    # --- Allure ---
    ax_pace = fig.add_subplot(gs[0])
    _style_axis(ax_pace)
    ax_pace.plot(distance_km, pace_min_per_km, color=_BLUE, linewidth=2, solid_capstyle="round")
    ax_pace.invert_yaxis()  # vers le haut = plus rapide
    ax_pace.set_ylabel("Allure (min/km)", fontsize=10, color=_INK_SECONDARY)
    ax_pace.set_title("Allure", fontsize=11, color=_INK_PRIMARY, loc="left", pad=8)

    # --- Fréquence cardiaque ---
    ax_hr = fig.add_subplot(gs[1], sharex=ax_pace)
    _style_axis(ax_hr)
    if heartrate:
        ax_hr.plot(
            distance_km[: len(heartrate)],
            heartrate,
            color=_RED,
            linewidth=2,
            solid_capstyle="round",
        )
        ax_hr.set_ylabel("FC (bpm)", fontsize=10, color=_INK_SECONDARY)
    else:
        ax_hr.text(
            0.5, 0.5, "Pas de donnée FC pour cette activité",
            transform=ax_hr.transAxes, ha="center", va="center", color=_INK_MUTED,
        )
        ax_hr.set_yticks([])
    ax_hr.set_title("Fréquence cardiaque", fontsize=11, color=_INK_PRIMARY, loc="left", pad=8)

    # --- Altitude ---
    ax_alt = fig.add_subplot(gs[2], sharex=ax_pace)
    _style_axis(ax_alt)
    if altitude:
        alt = altitude[:n]
        ax_alt.fill_between(distance_km[: len(alt)], alt, color=_AQUA, alpha=0.18, linewidth=0)
        ax_alt.plot(
            distance_km[: len(alt)], alt, color=_AQUA, linewidth=2, solid_capstyle="round"
        )
        ax_alt.set_ylabel("Altitude (m)", fontsize=10, color=_INK_SECONDARY)
    ax_alt.set_xlabel("Distance (km)", fontsize=10, color=_INK_SECONDARY)
    ax_alt.set_title("Profil d'altitude", fontsize=11, color=_INK_PRIMARY, loc="left", pad=8)

    # --- Splits au km ---
    ax_splits = fig.add_subplot(gs[3])
    _style_axis(ax_splits)
    if splits:
        kms = [s["km"] for s in splits]
        paces_min = [s["pace_s_per_km"] / 60 for s in splits]
        ax_splits.bar(kms, paces_min, color=_BLUE, width=0.7, zorder=2)
        ax_splits.set_xticks(kms)
        ax_splits.set_ylabel("Allure (min/km)", fontsize=10, color=_INK_SECONDARY)
        ax_splits.set_xlabel("Kilomètre", fontsize=10, color=_INK_SECONDARY)
    ax_splits.set_title(
        "Allure par kilomètre (plus haut = plus lent)",
        fontsize=11,
        color=_INK_PRIMARY,
        loc="left",
        pad=8,
    )

    return fig
