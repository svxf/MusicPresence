#!/usr/bin/env python3
import app_manager, os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    lastfm_api_key = os.getenv("LASTFM_API_KEY")
    lastfm_api_url = os.getenv("LASTFM_API_URL")
    discord_client_id = os.getenv("DISCORD_CLIENT_ID")

    manager = app_manager.AppManager(
        spotify_client_id,
        spotify_client_secret,
        spotify_redirect_uri,
        lastfm_api_key,
        lastfm_api_url,
        discord_client_id,
        debug=False
    )
    manager.start()