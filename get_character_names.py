import json
import re

# Load character mappings from JSON
with open("characters.json", "r") as char_file:
    character_map = json.load(char_file)

# Normalize JSON keys to lowercase for case-insensitive matching
character_map = {k.lower(): v for k, v in character_map.items()}

def extract_characters(title, character_map):
    """
    Extract and normalize character names from a title.
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
    Read input TSV, extract characters, and write to output TSV.
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

# File paths
input_file = "raw_video_stats.tsv"
output_file = "character_video_stats.tsv"

# Process the file
process_file(input_file, output_file, character_map)

print(f"Processing complete! Modified file saved as {output_file}.")
