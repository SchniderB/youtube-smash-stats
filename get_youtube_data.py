# -*- coding: utf-8 -*-

"""
YouTube Playlist Video Statistics

This script retrieves statistics for all videos in specified YouTube playlists
using the YouTube Data API. It processes each playlist, collects video details
(view count, like count, and comment count), and writes the data to a TSV file.

Features:
- Fetch video statistics for large playlists using batch processing.
- Handles API rate limits by adding delays between requests.
- Stores output in a tab-separated file (TSV) for easy analysis.

Usage:
- Configure the YouTube API key and service details in a `.env` file.
- Specify playlists in `playlists.json` with the format:
  {
      "playlist_id_1": "Playlist Title 1",
      "playlist_id_2": "Playlist Title 2",
      ...
  }
- Run the script to fetch and store statistics.

Requirements:
- google-api-python-client
- python-dotenv

Output:
- A file `raw_video_stats.tsv` containing video statistics for all playlists.

Author: Boris
"""


import os
import json
import time
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
YOUTUBE_API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME")
YOUTUBE_API_VERSION = os.getenv("YOUTUBE_API_VERSION")

# Define constant variables
INPUT_PLAYLISTS = "input_jsons/playlists.json"
OUTPUT_FILE = "raw_video_stats.tsv"
API_RATE_LIMIT_SLEEP = 1  # seconds
BATCH_SIZE = 50  # Max batch size for video stats

# Load Youtube playlists from JSON file
with open(INPUT_PLAYLISTS, "r") as file:
    playlists = json.load(file)

# Initialize the YouTube API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_playlist_video_ids(playlist_id, api_rate_limit, batch_size):
    """
    Retrieve all video IDs in a playlist using pagination.

    :param playlist_id: URL ID of a Youtube playlist (typically found as part of the URL)
    :param api_rate_limit: Number of request per second to Youtube's API
    :param batch_size: Maximal number of results per request
    :return: Complete list of video IDs for the given playlist
    """
    video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=batch_size,  # Maximum allowed per request
            pageToken=next_page_token
        ).execute()

        # Extract video IDs
        video_ids.extend(item["contentDetails"]["videoId"] for item in response.get("items", []))

        # Check for next page
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(api_rate_limit)  # Respect API limits

    return video_ids


def get_video_stats(video_ids, api_rate_limit, batch_size):
    """
    Fetch statistics for a batch of video IDs.

    :param video_ids: List of video IDs
    :param api_rate_limit: Number of request per second to Youtube's API
    :param batch_size: Maximal number of video IDs per request
    :return: Dictionary with the video ID as key and the corresponding video title, view count, like count and comment count
    as value defined as a nested dictionary
    """
    stats = {}
    for i in range(0, len(video_ids), batch_size):  # Batch video IDs (max 50 per request)
        batch_ids = ",".join(video_ids[i:i+batch_size])
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

        time.sleep(api_rate_limit)  # Respect API limits (1 request per second)

    return stats


def write_video_stats(output_file, playlist_title, playlist_id, stats):
    """
    Write to an open output file the playlist title, playlist ID, video title, video ID, view count, like count and comment count
    for each video ID provided in an input dictionary

    :param output_file: Open output file
    :param playlist_title: String of a Youtube playlist title
    :param playlist_id: String of a Youtube playlist ID
    :param stats: Dictionary with the video ID as key and the corresponding video title, view count, like count and comment count
    as value defined as a nested dictionary
    """
    for video_id, data in stats.items():
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


def process_playlists(playlists, output_file_path, api_rate_limit, batch_size):
    """
    Retrieve and save statistics for all videos in the specified playlists.

    :param playlists: URL ID of a Youtube playlist (typically found as part of the URL)
    :param output_file_path: Path and name of the output file to be written
    :param api_rate_limit: Number of request per second to Youtube's API
    :param batch_size: Maximal number of queries / results per request
    """

    # Open the file once for writing
    with open(output_file_path, "w") as output_file:
        # Write the header row
        output_file.write("Playlist title\tPlaylist ID\tVideo title\tVideo ID\tPlayer 1\tPlayer 2\tCharacters\tViews\tLikes\tComments\n")

        # Process each playlist
        for playlist_id, playlist_title in playlists.items():
            print(f"\nProcessing playlist: {playlist_id} - {playlist_title}")

            try:
                # Get video IDs from playlist
                video_ids = get_playlist_video_ids(playlist_id, api_rate_limit, batch_size)
                print(f"Found {len(video_ids)} videos in playlist.")

                # Get video statistics
                stats = get_video_stats(video_ids, api_rate_limit, batch_size)

                # Write statistics for each video
                write_video_stats(output_file, playlist_title, playlist_id, stats)

            except Exception as e:
                print(f"Error processing playlist {playlist_id}: {e}")

    print(f"\nData successfully written to {output_file_path}")


if __name__ == "__main__":
    # Validate environment variables
    if not API_KEY or not YOUTUBE_API_SERVICE_NAME or not YOUTUBE_API_VERSION:
        raise EnvironmentError("Missing one or more required environment variables.")

    # Run the script
    process_playlists(playlists, OUTPUT_FILE, API_RATE_LIMIT_SLEEP, BATCH_SIZE)
