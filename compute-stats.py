# -*- coding: utf-8 -*-
"""
YouTube Data Statistics Processing Script

This script processes a TSV file containing YouTube video statistics and computes
various metrics for players and characters. The results are saved in multiple TSV files,
sorted by specific metrics such as total views, average views, likes per view, and comments per view.

Features:
- Computes statistics for both players and characters.
- Supports multi-level sorting: primary metric and a secondary tie-breaker.
- Outputs data to structured TSV files with meaningful headers.

Input:
- TSV file with columns: "Playlist title", "Playlist ID", "Video title", "Video ID", "Player 1", "Player 2",
"Characters (Extracted)", "Views", "Likes", "Comments".

Output:
- TSV files containing computed statistics, sorted by the metrics of interest.

Usage:
- Modify the `input_file` and `file_paths` to match your data and desired output structure.
- Run the script to generate the output files.

Author: Boris
"""

import csv
from collections import defaultdict
from typing import Dict, Tuple

# File paths
input_file = "character_video_stats5.tsv"
file_paths = {
    "player": {
        "total_views": "output_statistics/total_views_per_player.tsv",
        "average_views": "output_statistics/average_views_per_player.tsv",
        "likes_per_view": "output_statistics/likes_per_view_per_player.tsv",
        "comments_per_view": "output_statistics/comments_per_view_per_player.tsv",
    },
    "character": {
        "total_views": "output_statistics/total_views_per_character.tsv",
        "average_views": "output_statistics/average_views_per_character.tsv",
        "likes_per_view": "output_statistics/likes_per_view_per_character.tsv",
        "comments_per_view": "output_statistics/comments_per_view_per_character.tsv",
    },
}

def aggregate_stats(entity: str, views: int, likes: int, comments: int, stats: Dict[str, defaultdict]):
    """
    Aggregates views, likes, comments, and matches for a given entity (player or character).

    :param entity: String name of the player or character being aggregated.
    :param views: Integer number of views to add for the entity.
    :param likes: Integer number of likes to add for the entity.
    :param comments: Integer number of comments to add for the entity.
    :param stats: A dictionary containing aggregated statistics.
    """
    stats["views"][entity] += views
    stats["likes"][entity] += likes
    stats["comments"][entity] += comments
    stats["matches"][entity] += 1

def compute_averages(data: defaultdict, match_counts: defaultdict, min_matches=0) -> Dict[str, float]:
    """
    Computes averages by dividing total values by match counts, with an optional minimum match threshold.

    :param data: A dictionary of total values (e.g., views).
    :param match_counts: A dictionary of match counts for each entity.
    :param min_matches: (Integer) Minimum number of matches required to include an entity in the result.
    :return: A dictionary of computed averages.
    """
    return {
        key: data[key] / match_counts[key]
        for key in data
        if match_counts[key] >= min_matches  # Include players with exactly 3 matches
    }

def compute_ratios(numerator: defaultdict, denominator: defaultdict, min_denominator=0) -> Dict[str, float]:
    """
    Computes ratios by dividing the numerator by the denominator, with an optional minimum denominator threshold.

    :param numerator: A dictionary of numerator values (e.g., likes).
    :param denominator: A dictionary of denominator values (e.g., views).
    :param min_denominator (int): (Integer) Minimum denominator value required to include an entity in the result.
    :return: A dictionary of computed ratios.
    """
    return {
        key: numerator[key] / denominator[key]
        for key in numerator
        if denominator[key] > min_denominator
    }

def write_statistics(data: Dict[str, any], output_file: str, headers: list, primary_sort_key: callable, secondary_sort_key: callable, reverse=True):
    """
    Writes computed statistics to a TSV file, sorted by two columns.

    :param data: The data to write, dictionary where keys are entity names and values are lists of metrics.
    :param output_file: String path to the output TSV file.
    :param headers: List of column headers for the output file.
    :param primary_sort_key: Callable, a function to extract the primary sorting key from each data item.
    :param secondary_sort_key: Callable, a function to extract the secondary sorting key for tie-breaking.
    :param reverse: Boolean, whether to sort in descending order.
    """
    with open(output_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(headers)

        # Sort by primary column first, and by secondary column if there are ties
        sorted_data = sorted(data.items(), key=lambda x: (primary_sort_key(x), secondary_sort_key(x)), reverse=reverse)

        for key, value in sorted_data:
            writer.writerow(value)

def process_statistics(input_file: str, file_paths: dict):
    """
    Processes the input TSV file to compute statistics per player and per character.

    :param input_file: String path to the input TSV file containing raw video statistics.
    :param file_paths: A dictionary containing paths for output TSV files for players and characters.
    """
    # Initialize data structures for players and characters
    player_stats = {
        "views": defaultdict(int),
        "likes": defaultdict(int),
        "comments": defaultdict(int),
        "matches": defaultdict(int),
    }

    character_stats = {
        "views": defaultdict(int),
        "likes": defaultdict(int),
        "comments": defaultdict(int),
        "matches": defaultdict(int),
    }

    # Read the input file
    with open(input_file, "r") as infile:
        reader = csv.DictReader(infile, delimiter="\t")

        for row in reader:
            views = int(row["Views"])
            likes = int(row["Likes"])
            comments = int(row["Comments"])
            characters = row["Characters (Extracted)"].split(", ")
            player1 = row["Player 1"].strip().lower()
            player2 = row["Player 2"].strip().lower()

            # Aggregate player stats
            if player1:
                aggregate_stats(player1, views, likes, comments, player_stats)
            if player2:
                aggregate_stats(player2, views, likes, comments, player_stats)

            # Aggregate character stats
            for character in characters:
                aggregate_stats(character, views, likes, comments, character_stats)

    # Compute statistics for players
    player_avg_views = compute_averages(player_stats["views"], player_stats["matches"], min_matches=3)
    player_likes_per_view = compute_ratios(player_stats["likes"], player_stats["views"], min_denominator=100000)
    player_comments_per_view = compute_ratios(player_stats["comments"], player_stats["views"], min_denominator=100000)

    # Compute statistics for characters
    character_avg_views = compute_averages(character_stats["views"], character_stats["matches"])
    character_likes_per_view = compute_ratios(character_stats["likes"], character_stats["views"])
    character_comments_per_view = compute_ratios(character_stats["comments"], character_stats["views"])

    # Write player statistics
    write_statistics(
        {player: [player.title(), total_views, player_stats["matches"][player]]
         for player, total_views in player_stats["views"].items()},
        file_paths["player"]["total_views"],
        ["Player", "Total Views", "Total Matches"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Matches' for tie-breaking
    )

    write_statistics(
        {player: [player.title(), round(avg_views, 2), player_stats["matches"][player]]
         for player, avg_views in player_avg_views.items()},
        file_paths["player"]["average_views"],
        ["Player", "Average Views", "Total Matches"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Matches' for tie-breaking
    )

    write_statistics(
        {player: [player.title(), round(likes_per_view, 4), player_stats["likes"][player], player_stats["views"][player]]
         for player, likes_per_view in player_likes_per_view.items()},
        file_paths["player"]["likes_per_view"],
        ["Player", "Likes Per View", "Total Likes", "Total Views"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Likes' for tie-breaking
    )

    write_statistics(
        {player: [player.title(), round(comments_per_view, 4), player_stats["comments"][player], player_stats["views"][player]]
         for player, comments_per_view in player_comments_per_view.items()},
        file_paths["player"]["comments_per_view"],
        ["Player", "Comments Per View", "Total Comments", "Total Views"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Comments' for tie-breaking
    )

    # Write character statistics
    write_statistics(
        {character: [character, total_views, character_stats["matches"][character]]
         for character, total_views in character_stats["views"].items()},
        file_paths["character"]["total_views"],
        ["Character", "Total Views", "Total Matches"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Matches' for tie-breaking
    )

    write_statistics(
        {character: [character, round(avg_views, 2), character_stats["matches"][character]]
         for character, avg_views in character_avg_views.items()},
        file_paths["character"]["average_views"],
        ["Character", "Average Views", "Total Matches"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Matches' for tie-breaking
    )

    write_statistics(
        {character: [character, round(likes_per_view, 4), character_stats["likes"][character], character_stats["views"][character]]
         for character, likes_per_view in character_likes_per_view.items()},
        file_paths["character"]["likes_per_view"],
        ["Character", "Likes Per View", "Total Likes", "Total Views"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Likes' for tie-breaking
    )

    write_statistics(
        {character: [character, round(comments_per_view, 4), character_stats["comments"][character], character_stats["views"][character]]
         for character, comments_per_view in character_comments_per_view.items()},
        file_paths["character"]["comments_per_view"],
        ["Character", "Comments Per View", "Total Comments", "Total Views"],
        primary_sort_key=lambda x: x[1][1],
        secondary_sort_key=lambda x: x[1][2],  # Sort by 'Total Comments' for tie-breaking
    )


if __name__ == "__main__":
    print("Statistics generation started.")
    process_statistics(input_file, file_paths)
    print("Statistics per player and per character processed successfully.")
