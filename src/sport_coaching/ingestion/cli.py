from __future__ import annotations

import argparse
import sys

from dotenv import set_key

from sport_coaching.ingestion import storage, strava_auth, strava_sync
from sport_coaching.ingestion.config import ENV_PATH, load_strava_config


def _cmd_authorize(_args: argparse.Namespace) -> None:
    config = load_strava_config()

    url = strava_auth.build_authorize_url(config.client_id)
    print("Ouvrez cette URL dans un navigateur et autorisez l'application :")
    print(url)
    code = input("Collez ici le paramètre 'code' de l'URL de redirection : ").strip()

    access_info = strava_auth.exchange_code_for_token(
        config.client_id, config.client_secret, code
    )
    set_key(str(ENV_PATH), "STRAVA_REFRESH_TOKEN", access_info["refresh_token"])
    print("STRAVA_REFRESH_TOKEN enregistré dans .env.")


def _cmd_sync(args: argparse.Namespace) -> None:
    config = load_strava_config()
    if not config.refresh_token:
        print(
            "Aucun STRAVA_REFRESH_TOKEN dans .env — lancez d'abord `authorize`.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    access_info = strava_auth.refresh_access_token(
        config.client_id, config.client_secret, config.refresh_token
    )
    if access_info["refresh_token"] != config.refresh_token:
        set_key(str(ENV_PATH), "STRAVA_REFRESH_TOKEN", access_info["refresh_token"])

    client = strava_auth.build_authenticated_client(access_info)
    conn = storage.connect(config.db_path)
    try:
        count = strava_sync.sync_activities(client, conn, full=args.full)
    finally:
        conn.close()
    print(f"{count} activité(s) synchronisée(s).")


def main() -> None:
    parser = argparse.ArgumentParser(prog="sport_coaching.ingestion.cli")
    subparsers = parser.add_subparsers(required=True)

    authorize_parser = subparsers.add_parser(
        "authorize", help="Autorisation OAuth2 initiale (une fois)."
    )
    authorize_parser.set_defaults(func=_cmd_authorize)

    sync_parser = subparsers.add_parser("sync", help="Synchronise les activités Strava.")
    sync_parser.add_argument(
        "--full", action="store_true", help="Ignore le watermark, refetch tout l'historique."
    )
    sync_parser.set_defaults(func=_cmd_sync)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
