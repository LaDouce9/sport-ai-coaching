from pathlib import Path

from sport_coaching.ingestion import config


def test_resolve_db_path_works_without_strava_credentials(monkeypatch):
    # Le point même de resolve_db_path() : fonctionner sans secrets Strava,
    # contrairement à load_strava_config().
    monkeypatch.delenv("STRAVA_CLIENT_ID", raising=False)
    monkeypatch.delenv("STRAVA_CLIENT_SECRET", raising=False)

    path = config.resolve_db_path()

    assert isinstance(path, Path)


def test_resolve_db_path_respects_env_override(monkeypatch, tmp_path):
    custom_path = tmp_path / "custom.sqlite3"
    monkeypatch.setenv("SPORT_COACHING_DB_PATH", str(custom_path))

    assert config.resolve_db_path() == custom_path


def test_resolve_db_path_defaults_to_data_folder(monkeypatch):
    monkeypatch.delenv("SPORT_COACHING_DB_PATH", raising=False)

    path = config.resolve_db_path()

    assert path == config.ENV_PATH.parent / "data" / "sport_coaching.sqlite3"
