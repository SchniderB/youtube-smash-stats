# -*- coding: utf-8 -*-
"""
YouTube Video Smash Ultimate Character Extractor

This script processes a TSV file containing YouTube video statistics, extracts
character names mentioned in the video titles, and maps them to a standardized
character set using a JSON configuration. The output is a modified TSV file
with the character column filled with normalized character names.

Features:
- Extracts character names from video titles using regex patterns.
- Maps extracted names to standardized names from a JSON file.
- Outputs a cleaned and annotated TSV file.

Dependencies:
- Requires a JSON file (`input_jsons/characters.json`) defining mappings of character names.
- Input TSV file must include video titles in the 3rd column.

Usage:
- Define the input file, output file, and character mapping JSON file.
- Run the script to generate the annotated TSV file.

Author: Boris
"""

import json
import re

# Define constant variables
CHARACTER_FILE = "input_jsons/characters.json"
INPUT_YT_FILE = "raw_video_stats.tsv"
OUTPUT_ANNOTATED_FILE = "character_video_stats.tsv"

# Load character mappings from JSON
with open(CHARACTER_FILE, "r") as char_file:
    character_map = json.load(char_file)

# Normalize JSON keys to lowercase for case-insensitive matching
character_map = {k.lower(): v for k, v in character_map.items()}

def extract_characters(title, character_map):
    """
    Extract and normalize character names from a video title.

    This function uses regex to extract substrings enclosed in parentheses
    from the provided title. It then normalizes and maps these substrings
    to standardized character names using the provided character map.

    :param title: String title of the video
    :param character_map: A dictionary mapping raw character names to standardized character names
    :return: A sorted, comma-separated string of unique, standardized character names
    """
    # Use regex to find words/phrases in parentheses (e.g., "Roy", "Meta Knight")
    matches = re.findall(r"\((.*?)\)", title)
    characters = set()  # Use a set to ensure uniqueness

    for match in matches:
        # Split the match on commas or slashes and normalize names
        for char in re.split(r"[,/]", match):  # Split on ',' or '/'
            char = char.strip().lower()  # Remove extra spaces and make lowercase
            if char in character_map:
                characters.add(character_map[char])

    return ", ".join(sorted(characters))  # Return characters as a sorted, comma-separated string

def process_file(input_file, output_file, character_map):
    """
    Process a TSV file, extract characters, and write to a new TSV file.

    This function reads the input TSV file line by line, extracts character
    names from the video titles, and appends a new column with normalized
    character names to the output TSV file.

    :param input_file: String path to the input TSV file
    :param output_file: String path to the output TSV file
    :param character_map: A dictionary mapping raw character names to standardized character names
    """
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        # Read header and write to output with updated column
        header = infile.readline().strip()
        outfile.write(header.replace("Characters", "Characters (Extracted)") + "\n")

        # Process each line
        for line in infile:
            parts = line.strip().split("\t")
            video_title = parts[2]  # Assuming the 3rd column is the video title
            characters = extract_characters(video_title, character_map)
            parts[6] = characters  # Assuming the 7th column is the characters column
            outfile.write("\t".join(parts) + "\n")


if __name__ == "__main__":
    # Process the file
    process_file(INPUT_YT_FILE, OUTPUT_ANNOTATED_FILE, character_map)
    print(f"Processing complete! Modified file saved as {OUTPUT_ANNOTATED_FILE}.")
