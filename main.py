import json
from pathlib import Path
import questionary
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

load_dotenv()

SCOPE = (
    "user-library-read "
    "user-library-modify "
    "playlist-read-private "
    "playlist-read-collaborative "
    "playlist-modify-public "
    "playlist-modify-private"
)
OUTPUT_DIR = Path("output")
CACHE_DIR = Path("cache")
LIKED_TRACKS_CACHE = CACHE_DIR / "liked_tracks.json"
BACK_TO_MAIN_MENU = "← Back to main menu"

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

    save_liked_tracks_cache(liked_tracks)

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

    choices = [BACK_TO_MAIN_MENU]
    choices.extend(playlist["name"] for playlist in playlists)

    selected_name = questionary.select(
        "Choose playlist:",
        choices=choices,
    ).ask()

    if not selected_name or selected_name == BACK_TO_MAIN_MENU:
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

def chunk_list(items, size):
    for index in range(0, len(items), size):
        yield items[index:index + size]

def track_to_cache_entry(track):
    return {
        "id": track["id"],
        "name": track.get("name", ""),
        "artists": [
            artist.get("name", "")
            for artist in track.get("artists", [])
        ],
        "url": track.get("external_urls", {}).get("spotify", ""),
    }

def add_tracks_to_liked_songs(sp, tracks):
    if not tracks:
        print("No tracks to add to Liked Songs.")
        return 0

    track_ids = [track["id"] for track in tracks if track.get("id")]

    for chunk in chunk_list(track_ids, 50):
        sp.current_user_saved_tracks_add(tracks=chunk)

    return len(track_ids)

def save_liked_tracks_cache(liked_tracks):
    CACHE_DIR.mkdir(exist_ok=True)

    with open(LIKED_TRACKS_CACHE, "w", encoding="utf-8") as file:
        json.dump(liked_tracks, file, ensure_ascii=False, indent=2)

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

def select_main_action():
    return questionary.select(
        "Choose action:",
        choices=[
            "Check playlist tracks against Liked Songs",
            "Manage playlists",
            "Exit",
        ],
    ).ask()


def get_current_user_id(sp):
    user = sp.current_user()
    return user["id"]


def format_playlist_management_choice(playlist, current_user_id):
    name = playlist.get("name", "Unknown playlist")
    owner = playlist.get("owner", {})
    owner_name = owner.get("display_name") or owner.get("id", "Unknown owner")
    total_tracks = playlist.get("tracks", {}).get("total", "Unknown")

    if owner.get("id") == current_user_id:
        return f"[OWNED] {name} | {total_tracks} tracks"
    
    return f"[SAVED] {name} | Owner: {owner_name} | {total_tracks} tracks"


def select_playlist_for_management(playlists, current_user_id):
    if not playlists:
        print("No playlists found.")
        return None

    choices = {
        format_playlist_management_choice(playlist, current_user_id): playlist
        for playlist in playlists
    }

    selection_choices = [BACK_TO_MAIN_MENU]
    selection_choices.extend(list(choices.keys()))

    selected = questionary.select(
        "Choose playlist:",
        choices=selection_choices,
    ).ask()

    if not selected or selected == BACK_TO_MAIN_MENU:
        return None

    return choices[selected]


def remove_playlist_from_library(sp, playlist, current_user_id):
    playlist_name = playlist.get("name", "Unknown playlist")
    owner = playlist.get("owner", {})
    owner_id = owner.get("id")
    owner_name = owner.get("display_name") or owner_id or "Unknown owner"

    is_owned = owner_id == current_user_id

    print("\nSelected playlist:")
    print(f"Name: {playlist_name}")
    print(f"Owner: {owner_name}")

    if is_owned:
        print("\nThis playlist is owned by you.")
        print("Spotify API does not provide true permanent playlist deletion.")
        print("This will remove/unfollow the playlist from your Spotify account.")
    else:
        print("\nThis playlist is saved/followed from another user.")
        print("This will remove it from your Spotify library.")

    confirmed = questionary.confirm(
        "Continue?",
        default=False,
    ).ask()

    if not confirmed:
        print("Playlist removal cancelled.")
        return

    sp.current_user_unfollow_playlist(playlist["id"])

    if is_owned:
        print(f'Owned playlist "{playlist_name}" removed from your Spotify account.')
    else:
        print(f'Saved playlist "{playlist_name}" removed from your library.')


def run_playlist_management(sp):
    print("Loading playlists...")
    playlists = get_user_playlists(sp)

    current_user_id = get_current_user_id(sp)

    playlist = select_playlist_for_management(playlists, current_user_id)

    if not playlist:
        return

    remove_playlist_from_library(sp, playlist, current_user_id)

def run_liked_songs_checker(sp):

    refresh_cache = should_refresh_liked_tracks_cache()

    liked_tracks = get_all_liked_tracks(
        sp,
        force_refresh=refresh_cache,
    )

    print("Loading playlists...")
    playlists = get_user_playlists(sp)

    playlist = select_playlist(playlists)

    if not playlist:
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

    if not_liked:
        should_add = questionary.confirm(
            f"Add {len(not_liked)} not-liked tracks to your Liked Songs?",
            default=False,
        ).ask()

        if should_add:
            added_count = add_tracks_to_liked_songs(sp, not_liked)
            print(f"Added {added_count} tracks to Liked Songs.")

            liked_tracks.update(
                {
                    track["id"]: track_to_cache_entry(track)
                    for track in not_liked
                }
            )

            save_liked_tracks_cache(liked_tracks)
            print("Liked songs cache updated with newly added tracks.")
    else:
        print("All loaded playlist tracks are already liked.")

    write_tracks("already_liked.txt", already_liked)
    write_tracks("not_liked.txt", not_liked)

    print("\nCreated files:")
    print("output/already_liked.txt")
    print("output/not_liked.txt")

def main():
    sp = get_spotify_client()

    while True:
        action = select_main_action()

        if action == "Check playlist tracks against Liked Songs":
            run_liked_songs_checker(sp)
        elif action == "Manage playlists":
            run_playlist_management(sp)
        else:
            print("App closed.")
            break

if __name__ == "__main__":
    try:
        main()
    except SpotifyException as error:
        handle_spotify_error(error)
    except KeyboardInterrupt:
        print("\nApp closed by user.")