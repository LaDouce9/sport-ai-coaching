from unittest.mock import patch

from sport_coaching.ingestion import strava_auth


def test_build_authorize_url_calls_client_with_expected_params():
    with patch("sport_coaching.ingestion.strava_auth.Client") as MockClient:
        instance = MockClient.return_value
        instance.authorization_url.return_value = "https://strava.example/authorize?x=1"

        url = strava_auth.build_authorize_url(client_id=42)

        instance.authorization_url.assert_called_once_with(
            client_id=42,
            redirect_uri=strava_auth.REDIRECT_URI,
            approval_prompt="force",
            scope=strava_auth.SCOPE,
        )
        assert url == "https://strava.example/authorize?x=1"


def test_exchange_code_for_token_forwards_params():
    with patch("sport_coaching.ingestion.strava_auth.Client") as MockClient:
        instance = MockClient.return_value
        instance.exchange_code_for_token.return_value = {
            "access_token": "a",
            "refresh_token": "r",
            "expires_at": 0,
        }

        result = strava_auth.exchange_code_for_token(42, "secret", "the-code")

        instance.exchange_code_for_token.assert_called_once_with(
            client_id=42, client_secret="secret", code="the-code"
        )
        assert result["refresh_token"] == "r"


def test_refresh_access_token_forwards_params():
    with patch("sport_coaching.ingestion.strava_auth.Client") as MockClient:
        instance = MockClient.return_value
        instance.refresh_access_token.return_value = {
            "access_token": "a2",
            "refresh_token": "r2",
            "expires_at": 1,
        }

        result = strava_auth.refresh_access_token(42, "secret", "old-refresh")

        instance.refresh_access_token.assert_called_once_with(
            client_id=42, client_secret="secret", refresh_token="old-refresh"
        )
        assert result["access_token"] == "a2"


def test_build_authenticated_client_sets_access_token():
    with patch("sport_coaching.ingestion.strava_auth.Client") as MockClient:
        strava_auth.build_authenticated_client(
            {"access_token": "tok", "refresh_token": "r", "expires_at": 0}
        )
        MockClient.assert_called_once_with(access_token="tok")
