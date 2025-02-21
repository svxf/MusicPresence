import time
from discord_presence import DiscordRPC
from spotify import SpotifyClient

class AppManager:
    def __init__(self, spotify_client_id, spotify_client_secret, spotify_redirect_uri, lastfm_api_key, lastfm_api_url, discord_client_id, debug):
        self.spotify_client = SpotifyClient(spotify_client_id, spotify_client_secret, spotify_redirect_uri, lastfm_api_key, lastfm_api_url, debug)
        self.discord_rpc = DiscordRPC(discord_client_id)
        self.running = True
        self.previousSong = None

    def start(self):
        print("Starting application...")
        try:
            while self.running:
                track_info = self.spotify_client.get_current_song()
                if track_info:
                    # if self.previousSong is not None:
                    #     print(f"Previous: {self.previousSong['track_name']} || Current: {track_info['track_name']}")
                    
                    if (
                        self.previousSong is None or
                        self.previousSong['track_name'] != track_info['track_name'] or
                        self.previousSong['is_playing'] != track_info['is_playing']
                    ):
                        print(f"Updating Discord Presence: {track_info['track_name']} by {track_info['artist_name']}")
                        self.discord_rpc.update_status(track_info)
                    
                    self.previousSong = track_info
                else:
                    print("No track is playing")
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        print("Stopping application...")
