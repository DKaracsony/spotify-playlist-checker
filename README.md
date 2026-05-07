# Spotify Playlist Liked Songs Checker

A simple Python tool that checks whether songs from a selected Spotify playlist are also saved in your **Liked Songs**.

The script compares tracks and generates two output files:

- `already_liked.txt`
- `not_liked.txt`

---

## Features

- Loads all your Spotify playlists
- Lets you select a playlist using keyboard arrows
- Compares playlist tracks against your Liked Songs
- Prints useful statistics
- Saves results into an `output/` folder
- Caches Liked Songs locally to reduce Spotify API requests
- Handles Spotify rate-limit errors gracefully
- Optionally adds non-liked playlist tracks to your Liked Songs after manual confirmation
- Automatically updates the local liked songs cache after adding tracks

---

## Safety

This project uses Spotify permissions for:

- Reading your Liked Songs
- Reading your playlists
- Manually adding selected tracks to your Liked Songs

- `user-library-read`
- `user-library-modify`
- `playlist-read-private`
- `playlist-read-collaborative`

The application only modifies your Spotify library after explicit manual confirmation.

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
Replace the URL with your own fork if you are using this project as a template.

```bash
cd spotify-playlist-checker
```
Or just open the folder in VS Code.

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
3. Fill in name + description
4. Select **Web API**
5. Create the app

---

### 5. Configure redirect URI

In app settings, add:

```
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

### 8. Run the app

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

The app will:

1. Load your Liked Songs
2. Load your playlists
3. Show an interactive playlist selector
4. Compare the selected playlist against your Liked Songs
5. Optionally allow adding non-liked songs to your Liked Songs
6. Create result files in the `output/` folder

On first launch, the app fetches your Liked Songs from Spotify and creates a local cache inside the `cache/` folder.

Future launches can reuse the cache to avoid unnecessary Spotify API requests and rate limits.

If tracks are added through the application, the local cache is automatically updated without requiring a full Spotify refetch.
## Output

The app creates:

```
output/
  already_liked.txt
  not_liked.txt
```

Console example:

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

```
http://127.0.0.1:8888/callback
```

---

### New Spotify permission does not appear

If the application was updated with new Spotify scopes (for example `user-library-modify`), delete the local `.cache` file and run the application again.

Spotify will then ask you to approve the updated permissions.

---

### Playlist not found

- Check spelling
- Ensure playlist belongs to your account or is accessible

---

## Notes

- Spotify Web API is free to use for personal projects
- No billing risk exists for this application
- Spotify may temporarily rate-limit excessive requests
- The app uses local caching to minimize API usage
- The local cache only stays fully accurate if tracks are added through the application or the cache is refreshed manually

---

## License

Free to use