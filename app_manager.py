import time
from discord_presence import DiscordRPC
from spotify import SpotifyClient
from tray_icon import TrayIcon

class AppManager:
    def __init__(self, spotify_client_id, spotify_client_secret, spotify_redirect_uri, lastfm_api_key, lastfm_api_url, discord_client_id, debug):
        self.spotify_client = SpotifyClient(spotify_client_id, spotify_client_secret, spotify_redirect_uri, lastfm_api_key, lastfm_api_url, debug)
        self.discord_rpc = DiscordRPC(discord_client_id)
        self.running = True
        self.previousSong = None
        self.tray_icon = TrayIcon(self)

    def start(self):
        print("Starting application...")
        self.tray_icon.run()
        print(self.tray_icon)

        try:
            while True:
                if not self.running:
                    time.sleep(0.5)
                    continue

                track_info = self.spotify_client.get_current_song()
                if track_info:
                    display_text = f"{track_info['track_name']} - {track_info['artist_name']}"
                    self.tray_icon.update_song(display_text)

                    if (
                        self.previousSong is None or
                        self.previousSong['track_name'] != track_info['track_name'] or
                        self.previousSong['is_playing'] != track_info['is_playing']
                    ):
                        print(f"Updating Discord Presence: {display_text}")
                        self.discord_rpc.update_status(track_info)

                    self.previousSong = track_info
                else:
                    self.tray_icon.update_song("No song playing")
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        print("Stopping application...")
        exit()