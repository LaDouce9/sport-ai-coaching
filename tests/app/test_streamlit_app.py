import matplotlib

matplotlib.use("Agg")

from streamlit.testing.v1 import AppTest

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


def test_changing_activity_selection_repeatedly_does_not_crash(tmp_path, monkeypatch):
    """Régression : la connexion sqlite était mise en cache (@st.cache_resource),
    donc réutilisée à travers les reruns Streamlit — qui peuvent s'exécuter sur des
    threads différents, provoquant `sqlite3.ProgrammingError: SQLite objects created
    in a thread can only be used in that same thread` au 2e changement de sélection.
    Voir docs/JOURNAL.md. Le correctif ouvre une connexion fraîche à chaque rerun."""
    db_path = tmp_path / "test.sqlite3"
    conn = storage.connect(db_path)
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(id=1, name="Sortie 1"))
    storage.upsert_activity(conn, _activity(id=2, name="Sortie 2"))
    storage.upsert_activity(conn, _activity(id=3, name="Sortie 3"))
    conn.commit()
    conn.close()

    monkeypatch.setenv("SPORT_COACHING_DB_PATH", str(db_path))

    at = AppTest.from_file("../../src/sport_coaching/app/streamlit_app.py", default_timeout=30)
    at.run()
    assert not at.exception

    at.selectbox[1].select_index(1).run()
    assert not at.exception
    at.selectbox[1].select_index(2).run()
    assert not at.exception
    at.selectbox[1].select_index(0).run()
    assert not at.exception


def test_filter_by_type_then_select_activity_renders_detail_card(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite3"
    conn = storage.connect(db_path)
    storage.init_db(conn)
    storage.upsert_activity(conn, _activity(id=1, sport_type="Run"))
    storage.upsert_activity(conn, _activity(id=2, sport_type="Ride"))
    conn.commit()
    conn.close()

    monkeypatch.setenv("SPORT_COACHING_DB_PATH", str(db_path))

    at = AppTest.from_file("../../src/sport_coaching/app/streamlit_app.py", default_timeout=30)
    at.run()

    at.selectbox[0].select("Run").run()
    assert not at.exception

    at.selectbox[1].select_index(0).run()
    assert not at.exception
    image_elements = [c for c in at.main.children.values() if type(c).__name__ == "Image"]
    assert image_elements, "la carte détail (graphique) devrait s'afficher après sélection"
