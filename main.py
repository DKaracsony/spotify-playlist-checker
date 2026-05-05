import json
from pathlib import Path
import questionary
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

load_dotenv()

SCOPE = "user-library-read playlist-read-private playlist-read-collaborative"
OUTPUT_DIR = Path("output")
CACHE_DIR = Path("cache")
LIKED_TRACKS_CACHE = CACHE_DIR / "liked_tracks.json"

def get_spotify_client():
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            open_browser=True,
            cache_path=".cache",
        )
    )


def get_all_liked_tracks(sp, force_refresh=False):
    CACHE_DIR.mkdir(exist_ok=True)

    if LIKED_TRACKS_CACHE.exists() and not force_refresh:
        print("Loading liked songs from cache...")

        with open(LIKED_TRACKS_CACHE, "r", encoding="utf-8") as file:
            return json.load(file)

    print("Fetching liked songs from Spotify...")

    liked_tracks = {}
    offset = 0

    while True:
        results = sp.current_user_saved_tracks(limit=50, offset=offset)
        items = results.get("items", [])

        if not items:
            break

        for item in items:
            track = item.get("track")

            if track and track.get("id"):
                liked_tracks[track["id"]] = {
                    "id": track["id"],
                    "name": track.get("name", ""),
                    "artists": [
                        artist.get("name", "")
                        for artist in track.get("artists", [])
                    ],
                    "url": track.get("external_urls", {}).get("spotify", ""),
                }

        offset += 50

    with open(LIKED_TRACKS_CACHE, "w", encoding="utf-8") as file:
        json.dump(liked_tracks, file, ensure_ascii=False, indent=2)

    print("Liked songs cache updated.")

    return liked_tracks


def get_user_playlists(sp):
    playlists = []
    offset = 0

    while True:
        results = sp.current_user_playlists(limit=50, offset=offset)
        items = results.get("items", [])

        if not items:
            break

        playlists.extend(items)
        offset += 50

    return playlists


def select_playlist(playlists):
    if not playlists:
        print("No playlists found.")
        return None

    choices = [playlist["name"] for playlist in playlists]

    selected_name = questionary.select(
        "Choose playlist:",
        choices=choices,
    ).ask()

    if not selected_name:
        return None

    return next(
        playlist for playlist in playlists
        if playlist["name"] == selected_name
    )


def get_playlist_tracks(sp, playlist_id):
    tracks = []
    unavailable = []
    non_track_items = []
    offset = 0

    while True:
        results = sp.playlist_items(
            playlist_id,
            limit=100,
            offset=offset,
            market="from_token",
        )

        items = results.get("items", [])

        if not items:
            break

        for item in items:
            track = item.get("track") or item.get("item")

            if not track:
                unavailable.append(item)
                continue

            if track.get("type") != "track":
                non_track_items.append(track)
                continue

            if track.get("id") is None or track.get("is_local"):
                unavailable.append(item)
                continue

            tracks.append(track)

        offset += 100

    return tracks, unavailable, non_track_items


def format_track(track):
    artists = ", ".join(artist["name"] for artist in track.get("artists", []))
    track_name = track.get("name", "Unknown track")
    url = track.get("external_urls", {}).get("spotify", "")

    if url:
        return f"{track_name} - {artists} | {url}"

    return f"{track_name} - {artists}"


def write_tracks(filename, tracks):
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as file:
        for track in tracks:
            file.write(format_track(track) + "\n")

def should_refresh_liked_tracks_cache():
    if not LIKED_TRACKS_CACHE.exists():
        print("No liked songs cache found. Fetching from Spotify...")
        return True

    return questionary.confirm(
        "Liked songs cache found. Refresh it from Spotify?",
        default=False,
    ).ask()

def handle_spotify_error(error):
    if error.http_status == 429:
        retry_after = error.headers.get("Retry-After", "unknown")

        print("\nSpotify rate limit reached.")
        print(f"Try again after: {retry_after} seconds.")
        print("The app will now exit safely.")
        return

    print("\nSpotify API error occurred.")
    print(error)

def main():
    sp = get_spotify_client()

    refresh_cache = should_refresh_liked_tracks_cache()

    liked_tracks = get_all_liked_tracks(
        sp,
        force_refresh=refresh_cache,
    )

    print("Loading playlists...")
    playlists = get_user_playlists(sp)

    playlist = select_playlist(playlists)

    if not playlist:
        print("No playlist selected.")
        return

    print(f'Loading playlist "{playlist["name"]}"...')
    tracks, unavailable, non_track_items = get_playlist_tracks(sp, playlist["id"])

    liked_ids = set(liked_tracks.keys())

    already_liked = [track for track in tracks if track["id"] in liked_ids]
    not_liked = [track for track in tracks if track["id"] not in liked_ids]

    playlist_details = sp.playlist(playlist["id"], fields="name,tracks(total)")
    spotify_total = playlist_details.get("tracks", {}).get("total", "Unknown")

    print("\nRESULT")
    print("------")
    print(f'Playlist: {playlist["name"]}')
    print(f"Total tracks according to Spotify: {spotify_total}")
    print(f"Loaded normal tracks: {len(tracks)}")
    print(f"Already liked: {len(already_liked)}")
    print(f"Not liked: {len(not_liked)}")
    print(f"Unavailable/local/disabled items: {len(unavailable)}")
    print(f"Non-track items: {len(non_track_items)}")

    write_tracks("already_liked.txt", already_liked)
    write_tracks("not_liked.txt", not_liked)

    print("\nCreated files:")
    print("output/already_liked.txt")
    print("output/not_liked.txt")


if __name__ == "__main__":
    try:
        main()
    except SpotifyException as error:
        handle_spotify_error(error)
    except KeyboardInterrupt:
        print("\nApp closed by user.")