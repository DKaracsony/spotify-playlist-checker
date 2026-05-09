# Spotify Playlist Utility

A Python CLI utility for managing Spotify playlists and Liked Songs.

The application currently supports:

- Comparing playlist tracks against your Liked Songs
- Adding missing playlist tracks to your Liked Songs
- Managing playlists directly from the terminal
- Removing/unfollowing playlists from your Spotify account

The app uses an interactive terminal interface powered by `questionary`.

---

## Features

### Playlist vs Liked Songs Checker

- Loads all your Spotify playlists
- Lets you select playlists using keyboard arrows
- Compares playlist tracks against your Liked Songs
- Prints detailed statistics
- Saves results into output files
- Optionally adds missing tracks to your Liked Songs
- Automatically updates the local cache after additions

### Playlist Management

- Lists all playlists available in your Spotify library
- Distinguishes:
  - Owned playlists
  - Saved/followed playlists
- Allows removing/unfollowing playlists directly from the terminal
- Includes safe confirmation prompts before modifications

### General Features

- Interactive CLI menus
- Keyboard navigation
- Local Liked Songs caching
- Reduced Spotify API usage
- Spotify rate-limit handling
- Back-to-main-menu navigation

---

## Safety

This project uses Spotify permissions for:

### Liked Songs

- Reading your Liked Songs
- Adding tracks to your Liked Songs

### Playlists

- Reading playlists
- Managing playlists
- Removing/unfollowing playlists

Spotify scopes used:

- `user-library-read`
- `user-library-modify`
- `playlist-read-private`
- `playlist-read-collaborative`
- `playlist-modify-public`
- `playlist-modify-private`

The application only modifies your Spotify account after explicit manual confirmation.

---

## Important Spotify API Note

Spotify does not provide a true permanent playlist deletion API.

When removing a playlist through this application:

- Owned playlists are removed/unfollowed from your account
- Saved playlists are removed from your library

This action does not necessarily permanently delete the playlist from Spotify itself.

---

## Ignored Files

The following files are automatically ignored and should never be committed:

- `.env`
- `.cache`
- `.venv/`
- `output/`
- `cache/`

---

## Requirements

- Python 3
- Spotify account
- Spotify Developer app

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/DKaracsony/spotify-playlist-checker.git
```

Replace the URL with your own fork if using this project as a template.

```bash
cd spotify-playlist-checker
```

Or open the folder in VS Code.

---

### 2. Create virtual environment

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

If blocked:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install spotipy python-dotenv questionary
pip freeze > requirements.txt
```

---

### 4. Create Spotify Developer app

1. Go to: https://developer.spotify.com/dashboard
2. Click **Create App**
3. Fill in name and description
4. Select **Web API**
5. Create the app

---

### 5. Configure redirect URI

In app settings, add:

```text
http://127.0.0.1:8888/callback
```

This must match exactly.

---

### 6. Get credentials

Copy:

- Client ID
- Client Secret

---

### 7. Create `.env`

Create a file called `.env` in the project root:

```env
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

---

### 8. Run the application

```bash
python main.py
```

or:

```bash
py main.py
```

---

## Usage

Run:

```bash
python main.py
```

Main menu:

```text
Choose action:
> Check playlist tracks against Liked Songs
  Manage playlists
  Exit
```

### Playlist Checker Flow

The application will:

1. Load your Liked Songs
2. Load your playlists
3. Let you select a playlist
4. Compare tracks against your Liked Songs
5. Optionally add missing tracks to your Liked Songs
6. Create result files inside `output/`

### Playlist Management Flow

The application can:

- Show all playlists in your library
- Distinguish owned vs saved playlists
- Remove/unfollow playlists after confirmation

Example:

```text
[OWNED] My Playlist | 120 tracks
[SAVED] Discover Weekly | Owner: Spotify | 30 tracks
```

---

## Cache System

On first launch, the app fetches your Liked Songs from Spotify and creates a local cache inside the `cache/` folder.

Future launches can reuse the cache to:

- Reduce Spotify API requests
- Improve loading speed
- Reduce rate-limit risk

The cache is automatically updated when tracks are added through the application.

---

## Output

The app creates:

```text
output/
  already_liked.txt
  not_liked.txt
```

Example console output:

```text
RESULT
------
Playlist: example
Total tracks according to Spotify: 100
Loaded normal tracks: 100
Already liked: 75
Not liked: 25
Unavailable/local/disabled items: 0
Non-track items: 0

Add 25 not-liked tracks to your Liked Songs? (y/N)
```

---

## Troubleshooting

### Python not recognized

Use:

```bash
py main.py
```

---

### Virtual environment activation blocked

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Redirect URI error

Make sure this matches exactly:

```text
http://127.0.0.1:8888/callback
```

---

### New Spotify permissions do not appear

If the application was updated with new Spotify scopes, delete the local `.cache` file and run the application again.

Spotify will then ask you to approve the updated permissions.

PowerShell:

```powershell
Remove-Item .cache
```

Linux / Git Bash / WSL:

```bash
rm .cache
```

---

### Playlist not found

- Ensure the playlist is accessible to your account
- Ensure the playlist still exists on Spotify

---

## Notes

- Spotify Web API is free for personal projects
- No billing risk exists for this application
- Spotify may temporarily rate-limit excessive requests
- Local caching minimizes API usage
- Cache accuracy depends on manual refreshes or modifications done through the application

---

## License

Free to use