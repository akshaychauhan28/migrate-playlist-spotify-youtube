import requests
import base64

# Replace these with your actual Spotify credentials from https://developer.spotify.com/dashboard/
SPOTIFY_CLIENT_ID = "edbe424561eb484797d0f008347e684e"      # ← Replace here
SPOTIFY_CLIENT_SECRET = "db21e4d5cf664f7695959e8dd66f9b59"  # ← Replace here

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    # requests.auth._basic_auth_str generates the proper "Basic ..." header string
    auth_header = requests.auth._basic_auth_str(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def extract_tracks_from_spotify(playlist_url):
    try:
        # Extract the playlist ID from the URL
        playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]
        access_token = get_access_token()

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {"Authorization": f"Bearer {access_token}"}

        tracks = []
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            for item in data["items"]:
                track = item["track"]
                if track:
                    title = track["name"]
                    # Concatenate all artist names if more than one
                    artist = ", ".join([artist["name"] for artist in track["artists"]])
                    tracks.append({"title": title, "artist": artist})
            url = data.get("next")  # Pagination
        return tracks
    except Exception as e:
        print(f"Error extracting Spotify tracks: {e}")
        return []
