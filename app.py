from flask import Flask, request, redirect, session, url_for, render_template_string
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os

# Allow HTTP for OAuth in local development (DO NOT use in production)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Import functions for handling Spotify and YouTube
from spotify_handler import extract_tracks_from_spotify
from youtube_handler import create_youtube_playlist, search_youtube_video, add_tracks_to_youtube_playlist

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# OAuth configuration
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the Spotify playlist link from the submitted form
        spotify_link = request.form.get("spotify_url")
        session["spotify_url"] = spotify_link
        return redirect(url_for("authorize"))
    
    return '''
    <h2>Spotify to YouTube Music Playlist Migrator</h2>
    <form method="POST">
        Spotify Playlist URL: <input type="text" name="spotify_url" placeholder="https://open.spotify.com/playlist/..." size="50" required><br><br>
        <input type="submit" value="Migrate Playlist">
    </form>
    '''

@app.route("/authorize")
def authorize():
    # Create OAuth flow from client_secrets.json
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("callback", _external=True)
    )
    auth_url, state = flow.authorization_url(prompt="consent")
    session["state"] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    state = session.get("state")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for("callback", _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    youtube = build("youtube", "v3", credentials=credentials)

    # Create a new YouTube playlist
    playlist_id, playlist_url = create_youtube_playlist(youtube, "Migrated Playlist")

    # Fetch Spotify tracks using the URL provided by the user
    spotify_link = session.get("spotify_url")
    spotify_tracks = extract_tracks_from_spotify(spotify_link) if spotify_link else []
    print("Extracted Spotify Tracks:", spotify_tracks)
    
    # Search YouTube for each track and collect video IDs
    video_ids = []
    for track in spotify_tracks:
        # The track is a dict with 'title' and 'artist'
        query = f"{track['title']} {track['artist']}"
        video_id = search_youtube_video(youtube, query)
        if video_id:
            video_ids.append(video_id)

    # Add found video IDs to the YouTube playlist
    added_count = add_tracks_to_youtube_playlist(youtube, playlist_id, video_ids)

    return render_template_string('''
        <h2>Playlist Created!</h2>
        <p><a href="{{ playlist_url }}" target="_blank">Open Playlist in YouTube</a></p>
        <p>Migrated {{ count }} tracks.</p>
    ''', playlist_url=playlist_url, count=added_count)

if __name__ == "__main__":
    app.run("localhost", 5000, debug=True)
