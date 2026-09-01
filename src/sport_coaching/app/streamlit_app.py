"""Interface Streamlit — visualisation des activités déjà synchronisées.

Lancer avec : streamlit run src/sport_coaching/app/streamlit_app.py

Premier jet minimal (specs/002-visualisation-activites-streamlit/spec.md) :
liste des activités filtrable par type, clic sur une activité -> carte détail
(indicateurs + graphiques), en lecture seule.
"""

from __future__ import annotations

import streamlit as st

from sport_coaching.app.queries import list_activities, list_sport_types
from sport_coaching.ingestion import storage
from sport_coaching.ingestion.config import resolve_db_path
from sport_coaching.metrics.activity_report import plot_activity_dashboard

st.set_page_config(page_title="Activités", layout="wide")


def _get_connection():
    # Pas de @st.cache_resource ici : Streamlit exécute chaque rerun (ex. changement
    # de sélection) potentiellement sur un thread différent, et sqlite3 interdit par
    # défaut de réutiliser une connexion créée dans un autre thread
    # (sqlite3.ProgrammingError). Une connexion SQLite locale est bon marché à ouvrir
    # à chaque rerun ; plus simple et sûr que de gérer le multi-thread ici.
    db_path = resolve_db_path()
    if not db_path.exists():
        return None
    return storage.connect(db_path)


def _format_distance(distance_m: float) -> str:
    return f"{distance_m / 1000:.2f} km"


def _format_duration(seconds: int) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes = remainder // 60
    if hours:
        return f"{hours}h{minutes:02d}"
    return f"{minutes}min"


def main() -> None:
    st.title("Activités")

    conn = _get_connection()
    if conn is None:
        st.warning(
            "Aucune base de données trouvée. Lancez d'abord une synchronisation "
            "Strava (voir README) avant d'ouvrir cette page."
        )
        return

    sport_types = list_sport_types(conn)
    if not sport_types:
        st.info("Aucune activité en base pour le moment.")
        return

    selected_type = st.selectbox("Type d'activité", ["Toutes"] + sport_types)
    filter_value = None if selected_type == "Toutes" else selected_type
    activities = list_activities(conn, sport_type=filter_value)

    if not activities:
        st.info(f"Aucune activité de type « {selected_type} ».")
        return

    labels = [
        f"{a.start_date_local[:10]} · {a.name} · {a.sport_type} · "
        f"{_format_distance(a.distance_m)} · {_format_duration(a.moving_time_s)}"
        for a in activities
    ]
    selected_index = st.selectbox(
        f"{len(activities)} activité(s) — sélectionner pour voir le détail",
        range(len(activities)),
        format_func=lambda i: labels[i],
    )

    selected_activity = activities[selected_index]
    st.divider()
    fig = plot_activity_dashboard(conn, selected_activity.id)
    st.pyplot(fig)


if __name__ == "__main__":
    main()
