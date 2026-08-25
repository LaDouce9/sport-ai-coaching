from __future__ import annotations

from stravalib.client import AccessInfo, Client

REDIRECT_URI = "http://localhost"

# "activity:read_all" est le scope documenté par Strava pour lire les activités
# privées. Signatures de Client vérifiées par introspection de stravalib==2.5.0
# (pas supposées) — voir docs/METHODOLOGIE.md, journal du 2026-08-25.
SCOPE = ["activity:read_all"]


def build_authorize_url(client_id: int) -> str:
    client = Client()
    return client.authorization_url(
        client_id=client_id,
        redirect_uri=REDIRECT_URI,
        approval_prompt="force",
        scope=SCOPE,
    )


def exchange_code_for_token(client_id: int, client_secret: str, code: str) -> AccessInfo:
    client = Client()
    return client.exchange_code_for_token(
        client_id=client_id, client_secret=client_secret, code=code
    )


def refresh_access_token(client_id: int, client_secret: str, refresh_token: str) -> AccessInfo:
    client = Client()
    return client.refresh_access_token(
        client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
    )


def build_authenticated_client(access_info: AccessInfo) -> Client:
    return Client(access_token=access_info["access_token"])
