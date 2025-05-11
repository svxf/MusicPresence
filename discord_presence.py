import time
from pypresence import Presence, ActivityType
from pypresence.exceptions import InvalidID, PipeClosed, DiscordNotFound

class DiscordRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = Presence(client_id)
        self.rpc.connect()

    def connect(self):
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            print("[DiscordRPC] Connected to Discord.")
        except (InvalidID, DiscordNotFound) as e:
            print(f"[DiscordRPC] Could not connect to Discord: {e}")
            self.rpc = None

    def clear_status(self):
        try:
            if self.rpc:
                self.rpc.clear()
                print("[DiscordRPC] Presence cleared.")
        except Exception as e:
            print(f"[DiscordRPC] Error clearing status: {e}")

    def update_status(self, track_info, _retrying=False):
        if self.rpc is None:
            self.connect()
            if self.rpc is None:
                return
            
        try:
            track_name = track_info["track_name"]
            track_url = track_info["track_url"]
            artist_name = track_info["artist_name"]
            album_name = track_info["album_name"]
            album_cover = track_info["album_cover"]
            duration_ms = track_info["duration_ms"]
            progress_ms = track_info["progress_ms"]

            start_time = int((time.time() * 1000) - progress_ms)
            end_time = int(start_time + duration_ms)

            is_playing = track_info["is_playing"]

            if len(track_name) < 2:
                track_name = "?"
            if len(album_name) < 2:
                album_name = ""
            else:
                album_name = "- " + album_name

            buttons = [{"label": "View Repository", "url": "https://github.com/svxf/MusicPresence"}]
            if (is_playing):
                if track_url:
                    buttons.insert(0, {"label": "Listen on Spotify", "url": track_url})

                self.rpc.update(
                    activity_type = ActivityType.LISTENING,
                    state=f"by {artist_name}",
                    details=f"Listening to {track_name}",
                    large_image=album_cover,
                    large_text=f"{track_name} {album_name}",
                    start=start_time,
                    end=end_time,
                    buttons=buttons
                )
            else:
                self.rpc.update(
                    activity_type = ActivityType.LISTENING,
                    state=f"by {artist_name}",
                    details=f"Listening to {track_name}",
                    large_image=album_cover,
                    large_text=f"{track_name} {album_name}",
                    small_image="paused_white",
                    small_text="Currently Paused",
                    buttons=buttons
                )
        except PipeClosed:
            print("[DiscordRPC] Pipe was closed. Attempting to reconnect...")
            self.connect()
            if not _retrying:
                self.update_status(track_info, _retrying=True)
        except Exception as e:
            print(f"[DiscordRPC] Error updating Discord Presence: {e}")