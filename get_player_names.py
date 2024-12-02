import pandas as pd

def update_players_with_quotes_handling(filename):
    """
    Update Player 1 and Player 2 columns in the TSV file while handling double quotes correctly
    and avoiding duplicates between Player 1 and Player 2.
    """
    # Load the TSV file into a DataFrame
    df = pd.read_csv(filename, sep="\t")

    # Normalize double quotes in titles and player names, handling NaN values
    df["Video title"] = df["Video title"].fillna("").str.replace('""', '"', regex=False)
    df["Player 1"] = df["Player 1"].fillna("").astype(str).str.replace('""', '"', regex=False).str.strip()
    df["Player 2"] = df["Player 2"].fillna("").astype(str).str.replace('""', '"', regex=False).str.strip()

    # Get unique player names from Player 1 and Player 2 columns
    existing_players = set(df["Player 1"].dropna().unique()).union(
        df["Player 2"].dropna().unique()
    )

    # Clean and normalize player names
    existing_players = {player.strip() for player in existing_players if player}

    # Define a function to extract player names from the video title
    def extract_players_from_title(title, players):
        matches = [player for player in players if player in title]
        return matches

    # Iterate over rows to update Player 1 and Player 2 columns
    for index, row in df.iterrows():
        # Extract players from the video title
        matched_players = extract_players_from_title(row["Video title"], existing_players)

        # Ensure only unique matched players
        matched_players = list(set(matched_players))

        # Update Player 1 and Player 2 if at least one of them is empty
        if len(matched_players) > 0:
            if not row["Player 1"] and not row["Player 2"]:
                # Assign first two players if both columns are empty
                if len(matched_players) > 1:
                    df.at[index, "Player 1"] = matched_players.pop(0)
                    df.at[index, "Player 2"] = matched_players.pop(0)
                else:
                    df.at[index, "Player 1"] = matched_players.pop(0)
            elif not row["Player 1"] and row["Player 2"]:
                # Filter out Player 2 from matched_players
                matched_players = [player for player in matched_players if player != row["Player 2"]]
                if matched_players:
                    df.at[index, "Player 1"] = matched_players.pop(0)
            elif row["Player 1"] and not row["Player 2"]:
                # Filter out Player 1 from matched_players
                matched_players = [player for player in matched_players if player != row["Player 1"]]
                if matched_players:
                    df.at[index, "Player 2"] = matched_players.pop(0)

    # Save the updated DataFrame back to the file
    df.to_csv(filename, sep="\t", index=False, quoting=3)

# Example usage
update_players_with_quotes_handling("character_video_stats.tsv")
# KEN, HERO, Delta
