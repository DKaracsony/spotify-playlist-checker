from pathlib import Path

import questionary
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

SCOPE = "user-library-read playlist-read-private playlist-read-collaborative"
OUTPUT_DIR = Path("output")


def get_spotify_client():
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            open_browser=True,
            cache_path=".cache",
        )
    )


def get_all_liked_tracks(sp):
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
                liked_tracks[track["id"]] = track

        offset += 50

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


def main():
    sp = get_spotify_client()

    print("Loading liked songs...")
    liked_tracks = get_all_liked_tracks(sp)

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
    main()