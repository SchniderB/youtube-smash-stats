import csv
from collections import defaultdict

# File paths
input_file = "character_video_stats5.tsv"
output_total_views_file = "output_statistics/total_views_per_player.tsv"
output_avg_views_file = "output_statistics/average_views_per_player.tsv"
output_likes_per_view_file = "output_statistics/likes_per_view_per_player.tsv"
output_comments_per_view_file = "output_statistics/comments_per_view_per_player.tsv"
output_total_views_character_file = "output_statistics/total_views_per_character.tsv"
output_avg_views_character_file = "output_statistics/average_views_per_character.tsv"
output_likes_per_view_character_file = "output_statistics/likes_per_view_per_character.tsv"
output_comments_per_view_character_file = "output_statistics/comments_per_view_per_character.tsv"

def process_statistics(input_file,
                       output_total_views_file, output_avg_views_file,
                       output_likes_per_view_file, output_comments_per_view_file,
                       output_total_views_character_file, output_avg_views_character_file,
                       output_likes_per_view_character_file, output_comments_per_view_character_file):
    """
    Process the input file to compute statistics per player and per character.
    """
    # Dictionaries to store total views, likes, comments, and match counts for players and characters
    player_views = defaultdict(int)
    player_likes = defaultdict(int)
    player_comments = defaultdict(int)
    player_match_counts = defaultdict(int)

    character_views = defaultdict(int)
    character_likes = defaultdict(int)
    character_comments = defaultdict(int)
    character_match_counts = defaultdict(int)

    # Read the input file
    with open(input_file, "r") as infile:
        # Automatically skip the header using csv.DictReader
        reader = csv.DictReader(infile, delimiter="\t")

        for row in reader:
            # Extract relevant fields
            views = int(row["Views"])
            likes = int(row["Likes"])
            comments = int(row["Comments"])
            characters = row["Characters (Extracted)"].split(", ")  # Split characters by ", "
            player1 = row["Player 1"].strip().lower()
            player2 = row["Player 2"].strip().lower()

            # Only add views, likes, and comments for non-empty player names
            if player1:
                player_views[player1] += views
                player_likes[player1] += likes
                player_comments[player1] += comments
                player_match_counts[player1] += 1

            if player2:
                player_views[player2] += views
                player_likes[player2] += likes
                player_comments[player2] += comments
                player_match_counts[player2] += 1

            # Aggregate stats for each character in the match
            for character in characters:
                character_views[character] += views
                character_likes[character] += likes
                character_comments[character] += comments
                character_match_counts[character] += 1

    # Compute averages and ratios for players
    player_avg_views = {
        player: player_views[player] / player_match_counts[player]
        for player in player_views
        if player_match_counts[player] >= 3
    }

    player_likes_per_view = {
        player: player_likes[player] / player_views[player]
        for player in player_views
        if player_views[player] > 100000
    }

    player_comments_per_view = {
        player: player_comments[player] / player_views[player]
        for player in player_views
        if player_views[player] > 100000
    }

    # Compute averages and ratios for characters
    character_avg_views = {
        character: character_views[character] / character_match_counts[character]
        for character in character_views
    }

    character_likes_per_view = {
        character: character_likes[character] / character_views[character]
        for character in character_views
        if character_views[character] > 0
    }

    character_comments_per_view = {
        character: character_comments[character] / character_views[character]
        for character in character_views
        if character_views[character] > 0
    }

    # Write total views to player file
    with open(output_total_views_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Player", "Total Views", "Total Matches"])
        for player, total_views in sorted(player_views.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([player.title(), total_views, player_match_counts[player]])

    # Write average views to player file
    with open(output_avg_views_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Player", "Average Views", "Total Matches"])
        for player, avg_views in sorted(player_avg_views.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([player.title(), round(avg_views, 2), player_match_counts[player]])

    # Write likes per view to player file
    with open(output_likes_per_view_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Player", "Likes Per View", "Total Likes", "Total Views"])
        for player, likes_per_view in sorted(player_likes_per_view.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([player.title(), round(likes_per_view, 4), player_likes[player], player_views[player]])

    # Write comments per view to player file
    with open(output_comments_per_view_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Player", "Comments Per View", "Total Comments", "Total Views"])
        for player, comments_per_view in sorted(player_comments_per_view.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([player.title(), round(comments_per_view, 4), player_comments[player], player_views[player]])

    # Write total views to character file
    with open(output_total_views_character_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Character", "Total Views", "Total Matches"])
        for character, total_views in sorted(character_views.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([character, total_views, character_match_counts[character]])

    # Write average views to character file
    with open(output_avg_views_character_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Character", "Average Views", "Total Matches"])
        for character, avg_views in sorted(character_avg_views.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([character, round(avg_views, 2), character_match_counts[character]])

    # Write likes per view to character file
    with open(output_likes_per_view_character_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Character", "Likes Per View", "Total Likes", "Total Views"])
        for character, likes_per_view in sorted(character_likes_per_view.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([character, round(likes_per_view, 4), character_likes[character], character_views[character]])

    # Write comments per view to character file
    with open(output_comments_per_view_character_file, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Character", "Comments Per View", "Total Comments", "Total Views"])
        for character, comments_per_view in sorted(character_comments_per_view.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([character, round(comments_per_view, 4), character_comments[character], character_views[character]])

# Run the function
process_statistics(
    input_file,
    output_total_views_file, output_avg_views_file,
    output_likes_per_view_file, output_comments_per_view_file,
    output_total_views_character_file, output_avg_views_character_file,
    output_likes_per_view_character_file, output_comments_per_view_character_file
)

print("Statistics per player and per character processed successfully.")
