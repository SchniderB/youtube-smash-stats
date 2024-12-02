from googleapiclient.discovery import build
import time
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
YOUTUBE_API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME")
YOUTUBE_API_VERSION = os.getenv("YOUTUBE_API_VERSION")

# Load playlists from JSON file
with open("playlists.json", "r") as file:
    playlists = json.load(file)

# Initialize the YouTube API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_video_stats(video_ids):
    """
    Fetch statistics for a batch of video IDs.
    """
    stats = {}
    for i in range(0, len(video_ids), 50):  # Batch video IDs (max 50 per request)
        batch_ids = ",".join(video_ids[i:i+50])
        response = youtube.videos().list(
            part="snippet,statistics",
            id=batch_ids
        ).execute()

        for item in response.get("items", []):
            video_id = item["id"]
            video_snippet = item["snippet"]
            video_stats = item["statistics"]
            stats[video_id] = {
                "title": video_snippet["title"],
                "viewCount": int(video_stats.get("viewCount", 0)),
                "likeCount": int(video_stats.get("likeCount", 0)),
                "commentCount": int(video_stats.get("commentCount", 0)),
            }

        time.sleep(1)  # Respect API limits (1 request per second)

    return stats

def get_playlist_video_ids(playlist_id):
    """
    Retrieve all video IDs in a playlist using pagination.
    """
    video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,  # Maximum allowed per request
            pageToken=next_page_token
        ).execute()

        # Extract video IDs
        video_ids.extend(item["contentDetails"]["videoId"] for item in response.get("items", []))

        # Check for next page
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(1)  # Respect API limits

    return video_ids

def process_playlists(playlists):
    """
    Retrieve and save statistics for all videos in the specified playlists.
    :param playlists: A dictionary where keys are playlist IDs and values are playlist titles.
    """
    output_file_path = "raw_video_stats.tsv"

    # Open the file once for writing
    with open(output_file_path, "w") as output_file:
        # Write the header row
        output_file.write("Playlist title\tPlaylist ID\tVideo title\tVideo ID\tPlayer 1\tPlayer 2\tCharacters\tViews\tLikes\tComments\n")

        # Process each playlist
        for playlist_id, playlist_title in playlists.items():
            print(f"\nProcessing playlist: {playlist_id} - {playlist_title}")

            try:
                # Get video IDs from playlist
                video_ids = get_playlist_video_ids(playlist_id)
                print(f"Found {len(video_ids)} videos in playlist.")

                # Get video statistics
                stats = get_video_stats(video_ids)

                # Write statistics for each video
                for video_id, data in stats.items():
                    # Sanitize data for TSV
                    video_title = data['title'].replace("\t", " ").replace("\n", " ")
                    output_file.write(
                        "{}\t{}\t{}\t{}\t\t\t\t{}\t{}\t{}\n".format(
                            playlist_title,
                            playlist_id,
                            video_title,
                            video_id,
                            data.get("viewCount", 0),
                            data.get("likeCount", 0),
                            data.get("commentCount", 0)
                        )
                    )

            except Exception as e:
                print(f"Error processing playlist {playlist_id}: {e}")

    print(f"\nData successfully written to {output_file_path}")


# Run the script
process_playlists(playlists)
