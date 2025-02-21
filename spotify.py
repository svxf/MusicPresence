import requests, re, json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def load_config(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config['ignore_words'], config['blacklist_words'], config['full_blacklisted']

ignore_words, blacklist_words, full_blacklisted = load_config('config.json')

def should_ignore(name):
    """ checks if the name contains any ignored words """
    for word in ignore_words:
        if word.lower() in name.lower():
            return True
    return False

def is_blacklisted(name):
    """ checks if the name contains any blacklisted words """
    for word in blacklist_words:
        if word.lower() in name.lower():
            return True
    return False

def is_fully_blacklisted(name):
    for word in full_blacklisted:
        if word.lower() in name.lower():
            return True
    return False

def clean_name(name):
    """ remove ignored words from the name """
    for word in ignore_words:
        name = re.sub(re.escape(word), "", name, flags=re.IGNORECASE)
    return " ".join(name.split())

# def get_actual_artist(api_key, api_url, track_name):
#     params = {
#         'method': 'track.search',
#         'track': track_name,
#         'api_key': api_key,
#         'format': 'json'
#     }
#     response = requests.get(api_url, params=params)
#     data = response.json()

#     print("\n\n")
#     print(track_name)

#     if 'results' in data and 'trackmatches' in data['results']:
#         tracks = data['results']['trackmatches']['track']
#         if tracks:
#             print(tracks[0]['artist'])
#             return tracks[0]['artist']
#     return "Unknown Artist"

class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri, lastfm_api_key, lastfm_api_url, debug):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="user-read-playback-state playlist-modify-private playlist-read-private"
            )
        )
        self.lastfm_api_key = lastfm_api_key
        self.lastfm_api_url = lastfm_api_url
        self.album_cover_cache = {}
        self.lastfm_cache = {}
        self.debug = debug

    def get_actual_artist(self, track_name):
        """ fetches the correct artist name from Last.fm """
        if track_name in self.lastfm_cache:
            if self.debug:
                print(f"Using cached artist for {track_name}: {self.lastfm_cache[track_name]}")
            return self.lastfm_cache[track_name]
        
        params = {
            'method': 'track.search',
            'track': track_name,
            'api_key': self.lastfm_api_key,
            'format': 'json'
        }
        response = requests.get(self.lastfm_api_url, params=params)
        data = response.json()

        if 'results' in data and 'trackmatches' in data['results']:
            tracks = data['results']['trackmatches']['track']
            if tracks:
                artist_name = tracks[0]['artist']
                self.lastfm_cache[track_name] = artist_name
                if self.debug:
                    print(f"Caching artist for {track_name}: {artist_name}")
                return artist_name

        self.lastfm_cache[track_name] = "Unknown Artist"
        if self.debug:
            print(f"Caching artist for {track_name}: Unknown Artist")
        return "Unknown Artist"

    def get_current_song(self):
        try:
            current_playback = self.sp.current_playback()
            if current_playback and current_playback.get("item"):
                track = current_playback["item"]
                track_name = track["name"]
                artist_name = ", ".join(artist["name"] for artist in track["artists"])
                album_name = track["album"]["name"]

                album_cover = None
                if track["album"]["images"]:
                    album_cover = track["album"]["images"][0]["url"]

                progress_ms = current_playback["progress_ms"]
                duration_ms = track["duration_ms"]

                if self.debug:
                    print("\n-----")
                    print(f"tn: {track_name} | an: {artist_name} | abn: {album_name}")

                if should_ignore(track_name):
                    track_name = clean_name(track_name)
                    if self.debug:
                        print(f"Cleaned tn: {track_name}")

                if should_ignore(artist_name) or not artist_name:
                    if self.debug:
                        print(f"Fetching artist from Last.fm for track: {track_name}")
                    artist_name = self.get_actual_artist(track_name)

                    if should_ignore(artist_name) or is_blacklisted(artist_name):
                        print(f"{artist_name} was ignored/blacklisted!")
                        return
                
                if is_blacklisted(track_name):
                    print(f"Blacklist: {track_name}")
                    return
                
                song_id = f"{track_name}-{artist_name}"
                if song_id in self.album_cover_cache:
                    album_cover = self.album_cover_cache[song_id]
                    if self.debug:
                        print(f"Using cached album cover for {track_name} by {artist_name}")
                else:
                    if "local" in track["uri"]:
                        search_result = self.sp.search(q=f"track:{track_name} artist:{artist_name}", type='track', limit=1)
                        if search_result['tracks']['items']:
                            album_cover = search_result['tracks']['items'][0]['album']['images'][0]['url']
                        else:
                            album_cover = "https://i.imgur.com/y8qHKbD.png" # default spotify logo
                    if album_cover:
                        print(f"Got album cover: {album_cover}")
                        self.album_cover_cache[song_id] = album_cover

                if self.debug:
                    print("-----")

                is_playing = current_playback.get("is_playing", False)

                if (track_name.startswith('"') and track_name.endswith('"')) or (track_name.startswith("'") and track_name.endswith("'")):
                    track_name = track_name[1:-1]

                if is_fully_blacklisted(track_name) or is_fully_blacklisted(artist_name) or is_fully_blacklisted(album_name):
                    print(f"Full Blacklist: tn: {track_name} | an: {artist_name} | aln: {album_name}")
                    return

                return {
                    "track_name": track_name,
                    "artist_name": artist_name,
                    "album_name": album_name,
                    "album_cover": album_cover,
                    "progress_ms": progress_ms,
                    "duration_ms": duration_ms,
                    "is_playing": is_playing
                }
        except Exception as e:
            print(f"Error fetching song: {e}")
        return None