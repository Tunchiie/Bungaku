import os
import time
import json
import re
import spotipy
from dotenv import load_dotenv
from tqdm import tqdm
from spotipy import SpotifyOAuth
from rapidfuzz import fuzz

file_name = "../var.env"
load_dotenv(file_name)


class SearchSpoti:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_ID")
        self.client_secret = os.getenv("SPOTIFY_SECRET")
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri="https://github.com/Tunchiie",
                scope="playlist-modify-private playlist-modify-public",
            ),
            requests_timeout=30,
        )

    def load_cache(self, path):
        """
        loads previously saved API responses (if available)
        to avoid redundant request and use quota efficiently.
        """
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_cache(self, cache, path):
        """
        Save the lastest API responses to maximize efficiency and quota
        usage.
        """
        with open(path, "w") as f:
            json.dump(cache, f)

    def search_spotify_fuzzy(self, song, artist, score_threshold=85):
        """
        Match song to the closest response from spotipy search method
        using fuzzy matching and store its uri.
        """
        cache = self.load_cache("../data/raw/unmatched_uri_cache.json")
        query = f"track:{song} artist:{artist}"
        key = f"{song} - {artist}"

        if key not in cache:
            try:
                results = self.sp.search(q=query, type="track", limit=5)
                candidates = results["tracks"]["items"]

                best_match = None
                best_score = 0

                for track in candidates:
                    track_name = self.clean_string(track["name"])
                    track_artist = self.clean_string(track["artists"][0]["name"])

                    title_score = fuzz.ratio(song, track_name)
                    artist_score = fuzz.ratio(artist, track_artist)
                    avg_score = (title_score + artist_score) / 2

                    if avg_score > best_score:
                        best_score = avg_score
                        best_match = track

                if best_score >= score_threshold:
                    cache[key] = best_match["uri"]

            except Exception as e:
                print(f"Error searching '{song}' by '{artist}': {e}")

        self.save_cache(cache, "../data/raw/unmatched_uri_cache.json")

    def create_playlist(self, path):
        """
        Create a playlist containing songs from the
        cached song uri's via Spotify's API.
        """
        me = self.sp.current_user()

        user_id = me["id"]

        cache = self.load_cache(path)
        playlist_count = 1
        batch = []

        for key, uri in tqdm(cache.items()):
            batch.append(uri)

            if len(batch) % 100 == 0:
                playlist = self.sp.user_playlist_create(
                    user=user_id, name=f"Billboard 100_{playlist_count}_unm"
                )
                self.sp.playlist_add_items(
                    playlist_id=playlist["id"],
                    items=batch,
                )
                playlist_count += 1
                batch = []
                time.sleep(1)

    def search_uri(self, batch):
        """
        Search for song uri's using spotipy search method
        and store it in a cache.
        """
        cache = self.load_cache()

        for song in tqdm(batch):
            key = f"{song['song_name']} - {song['artist']}"

            if key in cache:
                continue
            else:
                query = f"track:{song['song_name']} artist:{song['artist']}"

                try:
                    result = self.sp.search(q=query, type="track", limit=1)["tracks"][
                        "items"
                    ]
                    time.sleep(0.2)

                    if result:
                        cache[key] = result[0]["uri"]
                except spotipy.SpotifyException as error:
                    retry_after = int(error.headers.get("Retry-After", 60))
                    print(f"Rate limit hit. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
        self.save_cache(cache)

    def clean_string(self, text):
        """
        Clean and normalize text by removing special characters,
        any characters in parenthesis and excess whitespace.
        """
        text = str(text).lower()
        text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return text.strip()
