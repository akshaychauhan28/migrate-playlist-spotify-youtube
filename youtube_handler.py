import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def create_youtube_playlist(youtube, title, description="Playlist migrated from Spotify", privacy_status="private"):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {"privacyStatus": privacy_status}
        }
    )
    response = request.execute()
    playlist_id = response["id"]
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    return playlist_id, playlist_url

def search_youtube_video(youtube, query):
    try:
        request = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=1,
            type="video"
        )
        response = request.execute()
        items = response.get("items", [])
        if items:
            return items[0]["id"]["videoId"]
        else:
            print(f"No YouTube video found for query: {query}")
            return None
    except HttpError as e:
        print(f"Error searching for '{query}': {e}")
        return None

def add_tracks_to_youtube_playlist(youtube, playlist_id, video_ids):
    added_count = 0
    for video_id in video_ids:
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id}
                    }
                }
            ).execute()
            print(f"Added video ID: {video_id}")
            added_count += 1
            time.sleep(1)  # Delay to help avoid hitting API rate limits
        except HttpError as e:
            print(f"Failed to add video ID {video_id}: {e}")
        except Exception as ex:
            print(f"Unexpected error while adding video ID {video_id}: {ex}")
    return added_count
